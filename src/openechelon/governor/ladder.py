"""The cascade: cheapest sufficient intelligence, with governed escalation.

Principle 8 as executable code. Start on the cheapest resource that can serve the
task, ask the estimator whether the answer is good enough, and climb only when it
is not.

Two rules from elsewhere in the model are enforced here rather than assumed:

* **Principle 7.** A task requiring more reasoning than the assigning role
  permits is escalated, never run under-powered. Capping reasoning below what a
  task needs turns a resource limit into a correctness failure.
* **Principle 9.** A resource that is unavailable or out of quota is skipped,
  and a ladder with no serviceable rung fails with a reason rather than
  pretending.

Every rung produces a ``RoutingDecision`` with its score, threshold, and
estimator, because ADR 0003 requires decisions to be re-scorable against ground
truth once verification arrives.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from openechelon.governor.estimator import Response, SufficiencyEstimator, Verdict
from openechelon.governor.policy import EscalationPolicy
from openechelon.governor.providers import ExecutionProvider
from openechelon.models.common import ReasoningLevel
from openechelon.models.observability import RoutingDecision
from openechelon.models.resource import ESCALATION_LADDER, ExecutionResource
from openechelon.models.task import EscalationRecommendation, FailureKind, Task


@dataclass(frozen=True)
class Rung:
    """One attempt on one resource, with what it cost and how it was judged."""

    resource: ExecutionResource
    response: Response
    verdict: Verdict
    accepted: bool
    cost: float
    decision: RoutingDecision


@dataclass
class GovernorResult:
    """Outcome of running a task up the ladder."""

    task_id: str
    rungs: list[Rung] = field(default_factory=list)
    accepted_rung: Rung | None = None
    failure_kind: FailureKind | None = None
    recommendation: EscalationRecommendation | None = None
    detail: str = ""

    @property
    def succeeded(self) -> bool:
        return self.accepted_rung is not None

    @property
    def total_cost(self) -> float:
        return sum(rung.cost for rung in self.rungs)

    @property
    def escalations(self) -> int:
        return max(len(self.rungs) - 1, 0)

    @property
    def decisions(self) -> list[RoutingDecision]:
        return [rung.decision for rung in self.rungs]


def response_cost(resource: ExecutionResource, response: Response) -> float:
    """Monetary cost of one response.

    Local inference is zero here by construction — it consumes concurrency and
    wall-clock time, which the organization governs separately, but no money.
    Treating those as the same number would make the ladder prefer local
    resources for reasons the model cannot explain.
    """
    return (
        response.input_tokens * resource.cost_per_million_input
        + response.output_tokens * resource.cost_per_million_output
    ) / 1_000_000


class CascadeGovernor:
    """Routes a task up the escalation ladder under an explicit policy."""

    def __init__(
        self,
        resources: list[ExecutionResource],
        estimators: list[SufficiencyEstimator],
        policy: EscalationPolicy,
        provider: ExecutionProvider,
    ) -> None:
        self._resources = resources
        self._estimators = estimators
        self._policy = policy
        self._provider = provider

    def ladder_for(self, task: Task) -> list[ExecutionResource]:
        """Serviceable resources, cheapest first."""
        order = {cls: i for i, cls in enumerate(ESCALATION_LADDER)}
        candidates = [r for r in self._resources if r.can_serve(task.required_reasoning)]
        return sorted(
            candidates, key=lambda r: (order[r.resource_class], r.cost_per_million_output)
        )

    def estimator_for(self, task_class: str) -> SufficiencyEstimator | None:
        """First estimator with evidence for this task class, if any."""
        return next((e for e in self._estimators if e.supports(task_class)), None)

    def run(self, task: Task, role_ceiling: ReasoningLevel) -> GovernorResult:
        result = GovernorResult(task_id=task.task_id)

        # Principle 7: the role allowance is a ceiling on spending, not a cap on
        # what the task needs. A shortfall escalates; it is never absorbed.
        if task.required_reasoning > role_ceiling:
            result.failure_kind = FailureKind.REASONING_CEILING_EXCEEDED
            result.recommendation = EscalationRecommendation.STRONGER_RESOURCE
            result.detail = (
                f"task requires {task.required_reasoning.value} reasoning; "
                f"role ceiling is {role_ceiling.value}. Escalating rather than "
                f"running under-powered."
            )
            return result

        ladder = self.ladder_for(task)
        if not ladder:
            result.failure_kind = FailureKind.PROVIDER_UNAVAILABLE
            result.recommendation = EscalationRecommendation.ASK_HUMAN
            result.detail = (
                f"no available resource can serve {task.required_reasoning.value} reasoning "
                f"within quota"
            )
            return result

        estimator = self.estimator_for(task.task_class)
        threshold = self._policy.threshold_for(task.task_class)

        for attempt, resource in enumerate(ladder[: self._policy.max_attempts], start=1):
            response = self._provider.execute(resource, task, task.required_reasoning)

            if estimator is None:
                # No estimator with evidence for this class. ADR 0003: abstain,
                # and abstention escalates. Reaching the top of the ladder this
                # way is correct behaviour, not a bug — it is the system
                # declining to guess.
                verdict = Verdict(
                    estimator_id="none",
                    score=None,
                    evidence=f"no estimator has evidence for task class {task.task_class!r}",
                )
            else:
                verdict = estimator.estimate(task, response)

            accepted = self._policy.accepts(verdict, task.task_class)
            at_top = attempt >= min(len(ladder), self._policy.max_attempts)

            decision = RoutingDecision(
                task_id=task.task_id,
                task_class=task.task_class,
                attempt=attempt,
                selected_resource_id=resource.resource_id,
                selected_class=resource.resource_class,
                reasoning_requested=task.required_reasoning,
                role_ceiling=role_ceiling,
                considered_resource_ids=[r.resource_id for r in ladder],
                rationale=(
                    f"rung {attempt} of {len(ladder)}: {resource.resource_class.value}; "
                    f"{verdict.evidence}"
                ),
                sufficiency_score=verdict.score,
                threshold_applied=None if verdict.score is None else threshold,
                estimator_id=None if verdict.score is None else verdict.estimator_id,
                escalated=not accepted and not at_top,
            )

            rung = Rung(
                resource=resource,
                response=response,
                verdict=verdict,
                accepted=accepted,
                cost=response_cost(resource, response),
                decision=decision,
            )
            result.rungs.append(rung)

            if accepted:
                result.accepted_rung = rung
                return result

        # Ladder exhausted without acceptance. Principle 20: report structured
        # failure with a recommendation rather than retrying the same rung.
        result.failure_kind = FailureKind.INSUFFICIENT_CAPABILITY
        result.recommendation = (
            EscalationRecommendation.ASK_HUMAN
            if len(result.rungs) >= len(ladder)
            else EscalationRecommendation.STRONGER_RESOURCE
        )
        result.detail = (
            f"no rung met the {threshold:.2f} sufficiency threshold for task class "
            f"{task.task_class!r} after {len(result.rungs)} attempt(s)"
        )
        return result
