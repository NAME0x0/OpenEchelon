"""Regression tests pinning the Resource Governor spike results.

The spike's value is its numbers. If a change to the estimator or the policy
moves them, that should surface as a failing test with the new figures, not as a
quietly different README.
"""

from __future__ import annotations

from openechelon.governor import (
    AbstainingEstimator,
    EscalationPolicy,
    SchemaComplianceEstimator,
    SufficiencyEstimator,
)
from spikes.resource_governor.run import evaluate


def test_default_configuration_saves_cost_without_many_false_accepts() -> None:
    estimators: list[SufficiencyEstimator] = [SchemaComplianceEstimator()]
    tally = evaluate(estimators, EscalationPolicy(default_threshold=0.75))

    assert tally.savings > 0.80, "the cascade should avoid the frontier on most scenarios"
    assert tally.false_accept == 1, (
        "one false accept is expected: a structural estimator cannot detect a "
        "well-formed fabrication. If this changes, update the spike README."
    )
    assert tally.false_escalate == 1


def test_structural_estimator_accepts_a_well_formed_fabrication() -> None:
    """The known blind spot, asserted so it stays visible rather than forgotten."""
    from spikes.resource_governor.scenarios import SCENARIOS

    scenario = next(s for s in SCENARIOS if s.name == "structurally-complete-but-wrong")
    estimator = SchemaComplianceEstimator()

    from openechelon.governor import Response

    verdict = estimator.estimate(
        scenario.task,
        Response(text=scenario.outputs.local_small, input_tokens=100, output_tokens=50),
    )
    assert verdict.score == estimator.max_score
    assert not scenario.is_acceptable("local_small")


def test_a_threshold_above_the_estimator_ceiling_collapses_to_the_control() -> None:
    """An unreachable threshold makes the estimator contribute nothing but latency."""
    estimator = SchemaComplianceEstimator()
    strict = evaluate([estimator], EscalationPolicy(default_threshold=0.90))
    control = evaluate([AbstainingEstimator()], EscalationPolicy())

    assert estimator.max_score < 0.90
    assert strict.savings == control.savings == 0.0
    assert strict.false_accept == 0
    assert strict.unresolved == control.unresolved


def test_control_estimator_provides_no_saving() -> None:
    tally = evaluate([AbstainingEstimator()], EscalationPolicy())
    assert tally.savings == 0.0
    assert tally.correct_accept == 0
    assert tally.unresolved == 7
