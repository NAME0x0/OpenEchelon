"""Sufficiency estimation.

ADR 0003: this is the load-bearing component of the whole cost thesis. The
cascade in ``ladder.py`` is straightforward engineering; deciding whether a cheap
answer was good enough is not.

Two design choices follow from that ADR and are enforced here rather than left
to callers:

1. An estimator returns a **calibrated probability, or abstains**. It never
   returns a boolean, because the accept/escalate threshold is a policy decision
   the organization owns per task class and per risk level — not something an
   estimator should quietly decide on the organization's behalf.
2. An estimator that has no evidence for a task class **abstains**, and
   abstention escalates. Published routing work shows router quality is strongly
   distribution-dependent; an estimator asked to judge an unfamiliar task class
   is guessing, and a confident guess here produces a false accept, which is the
   expensive failure direction.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from openechelon.models.task import Task


class Response(BaseModel):
    """What an execution resource produced."""

    model_config = ConfigDict(extra="forbid")

    text: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)


class Verdict(BaseModel):
    """An estimator's judgement of one response.

    ``score is None`` means abstention: the estimator declines to judge. That is
    a legitimate, expected answer, and it is treated as insufficient by policy.
    """

    model_config = ConfigDict(extra="forbid")

    estimator_id: str = Field(min_length=1)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence: str = Field(min_length=1)
    """Why this score. A score with no reason cannot be audited, and
    Principle 24 requires that every meaningful decision be inspectable."""

    @property
    def abstained(self) -> bool:
        return self.score is None


@runtime_checkable
class SufficiencyEstimator(Protocol):
    """Judges whether a response is good enough to accept."""

    estimator_id: str

    def supports(self, task_class: str) -> bool:
        """Whether this estimator has evaluation evidence for the task class.

        Returning ``True`` without evidence is the single most damaging thing an
        estimator implementation can do.
        """
        ...

    def estimate(self, task: Task, response: Response) -> Verdict: ...


class AbstainingEstimator:
    """Baseline that never judges. Every response escalates.

    Useful as a control: running the spike with this estimator measures what the
    cascade costs when the estimator provides no signal at all. Any real
    estimator must beat it on cost without losing quality, or it is not earning
    its complexity.
    """

    estimator_id = "abstain"

    def supports(self, task_class: str) -> bool:
        return True

    def estimate(self, task: Task, response: Response) -> Verdict:
        return Verdict(
            estimator_id=self.estimator_id,
            score=None,
            evidence="control estimator: always abstains",
        )


class SchemaComplianceEstimator:
    """Structural estimator for task classes with a checkable output contract.

    Scope is deliberately narrow. It judges whether a response satisfies the
    structural requirements the task declared — required fields present,
    non-empty, no refusal or truncation markers. It does not judge whether the
    content is *correct*, and it says so by capping its score below certainty.

    This is the honest shape of a working estimator: narrow task class, checkable
    property, calibrated ceiling. It is not a general quality judge, and the
    project should be suspicious of anything claiming to be one.
    """

    estimator_id = "schema-compliance-v1"

    #: Task classes this estimator has been evaluated on.
    supported_classes: frozenset[str] = frozenset({"structured_extraction", "classification"})

    #: Ceiling on the score. Structure passing does not prove content correct,
    #: so this estimator can never report near-certainty.
    max_score: float = 0.85

    _REFUSAL_MARKERS = (
        "i cannot",
        "i can't",
        "as an ai",
        "unable to",
        "insufficient information",
    )
    _TRUNCATION_MARKERS = ("...", "[truncated]", "continued")

    def supports(self, task_class: str) -> bool:
        return task_class in self.supported_classes

    def estimate(self, task: Task, response: Response) -> Verdict:
        if not self.supports(task.task_class):
            return Verdict(
                estimator_id=self.estimator_id,
                score=None,
                evidence=f"no evaluation evidence for task class {task.task_class!r}",
            )

        text = response.text.strip()
        if not text:
            return Verdict(
                estimator_id=self.estimator_id,
                score=0.0,
                evidence="empty response",
            )

        lowered = text.lower()
        for marker in self._REFUSAL_MARKERS:
            if marker in lowered:
                return Verdict(
                    estimator_id=self.estimator_id,
                    score=0.05,
                    evidence=f"refusal marker present: {marker!r}",
                )

        required = _required_fields(task)
        if not required:
            return Verdict(
                estimator_id=self.estimator_id,
                score=None,
                evidence="task declared no checkable output contract",
            )

        missing = [field for field in required if field.lower() not in lowered]
        present_ratio = 1.0 - (len(missing) / len(required))

        truncated = any(lowered.endswith(marker) for marker in self._TRUNCATION_MARKERS)
        penalty = 0.3 if truncated else 0.0

        score = max(0.0, min(self.max_score, present_ratio * self.max_score - penalty))
        evidence = (
            f"{len(required) - len(missing)}/{len(required)} required fields present"
            + (f"; missing {missing}" if missing else "")
            + ("; response appears truncated" if truncated else "")
        )
        return Verdict(estimator_id=self.estimator_id, score=score, evidence=evidence)


def _required_fields(task: Task) -> list[str]:
    """Extract the output contract from the task's expected output.

    Fields are declared one per line as ``- name`` or ``name:``. Deliberately
    simple: the point of the spike is to measure the estimator, not to build a
    parser.
    """
    fields: list[str] = []
    for raw in task.expected_output.splitlines():
        line = raw.strip()
        if line.startswith("- "):
            fields.append(line[2:].split(":")[0].strip())
        elif line.endswith(":") and len(line) > 1:
            fields.append(line[:-1].strip())
    return [f for f in fields if f]
