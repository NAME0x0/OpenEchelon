"""Resource Governor spike.

Measures what ADR 0003 says must be measured before an organization runtime is
built on top of the cascade:

* cost against a frontier-always baseline,
* **false accepts** — a wrong answer accepted at a cheap rung,
* **false escalates** — a good cheap answer rejected and paid for again,
* abstention rate.

Run it::

    uv run python spikes/resource_governor/run.py
    uv run python spikes/resource_governor/run.py --control   # no-signal baseline

The provider here is scripted, so these numbers measure the *estimator and
policy*, not any model. That is deliberate: mixing real model variance into the
first measurement would make it impossible to tell which component moved. The
same harness runs against real providers by swapping the provider adapter, which
is the next step and requires labelled outputs.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

from openechelon.governor import (  # noqa: E402
    AbstainingEstimator,
    CascadeGovernor,
    EscalationPolicy,
    Response,
    SchemaComplianceEstimator,
    ScriptedProvider,
    SufficiencyEstimator,
    response_cost,
)
from openechelon.models.common import ReasoningLevel  # noqa: E402
from openechelon.models.resource import (  # noqa: E402
    ExecutionResource,
    ResourceClass,
    RuntimeKind,
)
from openechelon.models.task import Task  # noqa: E402
from spikes.resource_governor.scenarios import SCENARIOS, Scenario  # noqa: E402

LADDER = [
    ExecutionResource(
        resource_id="res_local_small",
        name="local small",
        resource_class=ResourceClass.LOCAL_SMALL,
        runtime=RuntimeKind.LOCAL_INFERENCE,
        provider="ollama",
        model_ref="small",
        max_reasoning=ReasoningLevel.NONE,
        private=True,
    ),
    ExecutionResource(
        resource_id="res_local_large",
        name="local large",
        resource_class=ResourceClass.LOCAL_LARGE,
        runtime=RuntimeKind.LOCAL_INFERENCE,
        provider="ollama",
        model_ref="large",
        max_reasoning=ReasoningLevel.LOW,
        private=True,
    ),
    ExecutionResource(
        resource_id="res_frontier",
        name="frontier standard",
        resource_class=ResourceClass.FRONTIER_STANDARD,
        runtime=RuntimeKind.HOSTED_API,
        provider="example",
        model_ref="standard",
        max_reasoning=ReasoningLevel.HIGH,
        cost_per_million_input=3.0,
        cost_per_million_output=15.0,
    ),
]

INPUT_TOKENS = 4_000
OUTPUT_TOKENS = 300


@dataclass
class Tally:
    """Confusion counts for the accept/escalate decision."""

    correct_accept: int = 0
    false_accept: int = 0
    correct_escalate: int = 0
    false_escalate: int = 0
    abstentions: int = 0
    unresolved: int = 0
    cascade_cost: float = 0.0
    baseline_cost: float = 0.0
    rows: list[str] = field(default_factory=list)

    @property
    def decisions(self) -> int:
        return self.correct_accept + self.false_accept + self.correct_escalate + self.false_escalate

    @property
    def savings(self) -> float:
        if self.baseline_cost == 0:
            return 0.0
        return 1.0 - (self.cascade_cost / self.baseline_cost)


def scripted_provider(scenario: Scenario) -> ScriptedProvider:
    def make(text: str):  # type: ignore[no-untyped-def]
        def factory(
            resource: ExecutionResource,
            task: Task,
            reasoning: ReasoningLevel,
        ) -> Response:
            return Response(
                text=text,
                input_tokens=INPUT_TOKENS,
                output_tokens=OUTPUT_TOKENS,
                latency_ms=100,
            )

        return factory

    return ScriptedProvider(
        {
            "local_small": make(scenario.outputs.local_small),
            "local_large": make(scenario.outputs.local_large),
            "frontier_standard": make(scenario.outputs.frontier_standard),
        }
    )


def baseline_cost() -> float:
    """Cost of sending every task straight to the frontier resource."""
    frontier = LADDER[-1]
    return response_cost(
        frontier, Response(text="", input_tokens=INPUT_TOKENS, output_tokens=OUTPUT_TOKENS)
    )


def evaluate(estimators: list[SufficiencyEstimator], policy: EscalationPolicy) -> Tally:
    tally = Tally()

    for scenario in SCENARIOS:
        provider = scripted_provider(scenario)
        governor = CascadeGovernor(
            resources=list(LADDER),
            estimators=estimators,
            policy=policy,
            provider=provider,
        )
        result = governor.run(scenario.task, role_ceiling=ReasoningLevel.MEDIUM)

        tally.cascade_cost += result.total_cost
        tally.baseline_cost += baseline_cost()

        for rung in result.rungs:
            cls = rung.resource.resource_class.value
            truly_ok = scenario.is_acceptable(cls)
            if rung.verdict.abstained:
                tally.abstentions += 1
            if rung.accepted:
                if truly_ok:
                    tally.correct_accept += 1
                else:
                    tally.false_accept += 1
            elif truly_ok:
                tally.false_escalate += 1
            else:
                tally.correct_escalate += 1

        if result.succeeded:
            assert result.accepted_rung is not None
            landed = result.accepted_rung.resource.resource_class.value
            verdict = "OK " if scenario.is_acceptable(landed) else "BAD"
        else:
            landed = "none"
            verdict = "---"
            tally.unresolved += 1

        tally.rows.append(
            f"  {verdict}  {scenario.name:<34} "
            f"rungs={len(result.rungs)}  landed={landed:<18} "
            f"cost=${result.total_cost:.4f}"
        )

    return tally


def report(title: str, tally: Tally) -> None:
    print(f"\n{title}")
    print("=" * len(title))
    for row in tally.rows:
        print(row)

    print(f"\n  scenarios              {len(SCENARIOS)}")
    print(f"  rung decisions         {tally.decisions}")
    print(f"  correct accepts        {tally.correct_accept}")
    print(f"  FALSE ACCEPTS          {tally.false_accept}   <- wrong answer shipped")
    print(f"  correct escalates      {tally.correct_escalate}")
    print(f"  false escalates        {tally.false_escalate}   <- money wasted, answer fine")
    print(f"  abstentions            {tally.abstentions}")
    print(f"  unresolved (no rung)   {tally.unresolved}")
    print(f"\n  cascade cost           ${tally.cascade_cost:.4f}")
    print(f"  frontier-always cost   ${tally.baseline_cost:.4f}")
    print(f"  cost saved             {tally.savings * 100:.1f}%")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--control",
        action="store_true",
        help="run with the always-abstaining estimator to measure the no-signal baseline",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="override the accept threshold for every task class",
    )
    args = parser.parse_args()

    policy = EscalationPolicy(
        default_threshold=args.threshold if args.threshold is not None else 0.75
    )
    estimators: list[SufficiencyEstimator] = (
        [AbstainingEstimator()] if args.control else [SchemaComplianceEstimator()]
    )
    title = (
        "CONTROL: always-abstain estimator"
        if args.control
        else f"schema-compliance estimator @ threshold {policy.default_threshold:.2f}"
    )

    tally = evaluate(estimators, policy)
    report(title, tally)

    print(
        "\nRead this as a measurement of the estimator and policy, not of any model.\n"
        "The scripted provider removes model variance on purpose. Real numbers need\n"
        "the same harness pointed at real providers with labelled outputs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
