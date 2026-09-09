"""Tests for the Resource Governor cascade.

These assert behaviour the cost thesis depends on: cheap-first routing, refusal
to run under-powered, abstention escalating, and structured failure at the top of
the ladder.
"""

from __future__ import annotations

from typing import Any

import pytest

from openechelon.governor import (
    AbstainingEstimator,
    CascadeGovernor,
    EscalationPolicy,
    Response,
    SchemaComplianceEstimator,
    ScriptedProvider,
    SufficiencyEstimator,
    fixed_response,
    response_cost,
)
from openechelon.governor.providers import ResponseFactory
from openechelon.models.common import ReasoningLevel
from openechelon.models.permissions import RiskLevel
from openechelon.models.resource import ExecutionResource, Quota, ResourceClass, RuntimeKind
from openechelon.models.task import FailureKind, Task

COMPLETE = "file: auth.py\nfunction: validate\npattern: duplicated null check"
PARTIAL = "file: auth.py"
REFUSAL = "I cannot determine that from the information provided."


def local_small() -> ExecutionResource:
    return ExecutionResource(
        resource_id="res_local_small",
        name="qwen3:4b",
        resource_class=ResourceClass.LOCAL_SMALL,
        runtime=RuntimeKind.LOCAL_INFERENCE,
        provider="ollama",
        model_ref="qwen3:4b",
        max_reasoning=ReasoningLevel.NONE,
        private=True,
    )


def local_large() -> ExecutionResource:
    return ExecutionResource(
        resource_id="res_local_large",
        name="qwen3:32b",
        resource_class=ResourceClass.LOCAL_LARGE,
        runtime=RuntimeKind.LOCAL_INFERENCE,
        provider="ollama",
        model_ref="qwen3:32b",
        max_reasoning=ReasoningLevel.LOW,
        private=True,
    )


def frontier() -> ExecutionResource:
    return ExecutionResource(
        resource_id="res_frontier",
        name="frontier standard",
        resource_class=ResourceClass.FRONTIER_STANDARD,
        runtime=RuntimeKind.HOSTED_API,
        provider="example",
        model_ref="example-standard",
        max_reasoning=ReasoningLevel.HIGH,
        cost_per_million_input=3.0,
        cost_per_million_output=15.0,
    )


def extraction_task(**overrides: Any) -> Task:
    defaults: dict[str, Any] = {
        "objective": "Find duplicated validation logic",
        "instruction": "Inspect the listed files",
        "expected_output": "- file\n- function\n- pattern",
        "task_class": "structured_extraction",
        "created_by": "emp_manager",
        "required_reasoning": ReasoningLevel.NONE,
    }
    defaults.update(overrides)
    return Task(**defaults)


def governor(
    responses: dict[str, ResponseFactory],
    *,
    policy: EscalationPolicy | None = None,
    resources: list[ExecutionResource] | None = None,
    estimators: list[SufficiencyEstimator] | None = None,
) -> tuple[CascadeGovernor, ScriptedProvider]:
    provider = ScriptedProvider(responses)
    gov = CascadeGovernor(
        resources=resources or [frontier(), local_small(), local_large()],
        estimators=estimators if estimators is not None else [SchemaComplianceEstimator()],
        policy=policy or EscalationPolicy(),
        provider=provider,
    )
    return gov, provider


# --- Principle 8: cheapest sufficient intelligence ---------------------------


def test_ladder_is_ordered_cheapest_first_regardless_of_input_order() -> None:
    gov, _ = governor({"local_small": fixed_response(COMPLETE)})
    ladder = gov.ladder_for(extraction_task())
    assert [r.resource_class for r in ladder] == [
        ResourceClass.LOCAL_SMALL,
        ResourceClass.LOCAL_LARGE,
        ResourceClass.FRONTIER_STANDARD,
    ]


def test_a_sufficient_cheap_answer_never_reaches_the_frontier() -> None:
    gov, provider = governor(
        {
            "local_small": fixed_response(COMPLETE),
            "local_large": fixed_response(COMPLETE),
            "frontier_standard": fixed_response(COMPLETE),
        }
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert result.succeeded
    assert result.accepted_rung is not None
    assert result.accepted_rung.resource.resource_class is ResourceClass.LOCAL_SMALL
    assert result.escalations == 0
    assert result.total_cost == 0.0
    assert [call[0] for call in provider.calls] == ["res_local_small"]


def test_an_insufficient_cheap_answer_escalates_and_is_recorded() -> None:
    gov, provider = governor(
        {
            "local_small": fixed_response(PARTIAL),
            "local_large": fixed_response(COMPLETE),
            "frontier_standard": fixed_response(COMPLETE),
        }
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert result.succeeded
    assert result.accepted_rung is not None
    assert result.accepted_rung.resource.resource_class is ResourceClass.LOCAL_LARGE
    assert result.escalations == 1
    assert [call[0] for call in provider.calls] == ["res_local_small", "res_local_large"]

    first, second = result.decisions
    assert first.escalated is True
    assert first.sufficiency_score is not None and first.sufficiency_score < 0.75
    assert first.threshold_applied == 0.75
    assert first.estimator_id == "schema-compliance-v1"
    assert second.escalated is False


def test_a_refusal_scores_near_zero_and_escalates() -> None:
    gov, _ = governor(
        {
            "local_small": fixed_response(REFUSAL),
            "local_large": fixed_response(COMPLETE),
            "frontier_standard": fixed_response(COMPLETE),
        }
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert result.rungs[0].verdict.score == pytest.approx(0.05)
    assert "refusal marker" in result.rungs[0].verdict.evidence
    assert result.succeeded


# --- Principle 7: never run under-powered ------------------------------------


def test_a_task_above_the_role_ceiling_escalates_without_executing() -> None:
    gov, provider = governor({"local_small": fixed_response(COMPLETE)})
    result = gov.run(
        extraction_task(required_reasoning=ReasoningLevel.HIGH),
        role_ceiling=ReasoningLevel.LOW,
    )

    assert not result.succeeded
    assert result.failure_kind is FailureKind.REASONING_CEILING_EXCEEDED
    assert "rather than running under-powered" in result.detail
    assert provider.calls == [], "no resource should have been invoked"


# --- ADR 0003: abstention escalates ------------------------------------------


def test_an_unsupported_task_class_abstains_rather_than_guessing() -> None:
    gov, _ = governor(
        {
            "local_small": fixed_response(COMPLETE),
            "local_large": fixed_response(COMPLETE),
            "frontier_standard": fixed_response(COMPLETE),
        }
    )
    result = gov.run(
        extraction_task(task_class="open_ended_research"),
        role_ceiling=ReasoningLevel.LOW,
    )

    assert not result.succeeded
    assert all(rung.verdict.abstained for rung in result.rungs)
    assert all(d.sufficiency_score is None for d in result.decisions)
    assert result.failure_kind is FailureKind.INSUFFICIENT_CAPABILITY


def test_the_control_estimator_climbs_the_whole_ladder() -> None:
    """Baseline for the spike: what a no-signal estimator costs."""
    gov, provider = governor(
        {
            "local_small": fixed_response(COMPLETE),
            "local_large": fixed_response(COMPLETE),
            "frontier_standard": fixed_response(COMPLETE),
        },
        estimators=[AbstainingEstimator()],
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert not result.succeeded
    assert len(provider.calls) == 3
    assert result.total_cost > 0.0, "the control burns frontier tokens by design"


def test_disabling_abstention_escalation_accepts_unjudged_answers() -> None:
    """Documents the failure mode ADR 0003 forbids, so a change here is visible."""
    gov, _ = governor(
        {"local_small": fixed_response(COMPLETE)},
        policy=EscalationPolicy(abstention_escalates=False),
        estimators=[AbstainingEstimator()],
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)
    assert result.succeeded
    assert result.accepted_rung is not None
    assert result.accepted_rung.verdict.abstained


# --- Policy: risk raises the bar ---------------------------------------------


def test_human_risk_actions_cannot_be_accepted_on_an_estimator_score() -> None:
    """Principle 23: an irreversible action is not authorized by a probability."""
    policy = EscalationPolicy(risk_level=RiskLevel.HUMAN)
    assert policy.threshold_for("structured_extraction") == 1.0

    gov, _ = governor(
        {
            "local_small": fixed_response(COMPLETE),
            "local_large": fixed_response(COMPLETE),
            "frontier_standard": fixed_response(COMPLETE),
        },
        policy=policy,
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)
    assert not result.succeeded


def test_risk_level_raises_but_never_lowers_a_class_threshold() -> None:
    policy = EscalationPolicy(
        per_task_class={"structured_extraction": 0.6},
        risk_level=RiskLevel.EXECUTIVE,
    )
    assert policy.threshold_for("structured_extraction") == 0.9

    lenient = EscalationPolicy(per_task_class={"structured_extraction": 0.95})
    assert lenient.threshold_for("structured_extraction") == 0.95


# --- Principle 9: quota and availability -------------------------------------


def test_exhausted_and_unavailable_resources_are_skipped() -> None:
    small = local_small()
    small.quota = Quota(limit=5, used=5)
    large = local_large()
    large.available = False

    gov, provider = governor(
        {"frontier_standard": fixed_response(COMPLETE)},
        resources=[small, large, frontier()],
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert result.succeeded
    assert [call[0] for call in provider.calls] == ["res_frontier"]


def test_no_serviceable_resource_fails_with_a_reason() -> None:
    small = local_small()
    small.available = False
    gov, _ = governor({}, resources=[small])
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert not result.succeeded
    assert result.failure_kind is FailureKind.PROVIDER_UNAVAILABLE
    assert result.recommendation is not None


# --- Cost accounting ----------------------------------------------------------


def test_local_execution_has_no_monetary_cost() -> None:
    assert response_cost(local_small(), Response(text="x", input_tokens=10_000)) == 0.0


def test_frontier_cost_is_computed_per_million_tokens() -> None:
    cost = response_cost(
        frontier(),
        Response(text="x", input_tokens=1_000_000, output_tokens=1_000_000),
    )
    assert cost == pytest.approx(18.0)


def test_max_attempts_bounds_the_ladder() -> None:
    """Principle 20: retries are bounded and deliberate, never a loop."""
    gov, provider = governor(
        {
            "local_small": fixed_response(PARTIAL),
            "local_large": fixed_response(PARTIAL),
            "frontier_standard": fixed_response(COMPLETE),
        },
        policy=EscalationPolicy(max_attempts=2),
    )
    result = gov.run(extraction_task(), role_ceiling=ReasoningLevel.LOW)

    assert not result.succeeded
    assert len(provider.calls) == 2
    assert result.recommendation is not None
