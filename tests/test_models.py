"""Tests for the Phase 0 organizational data model.

Each test names the principle it protects. A model invariant with no test is a
comment.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from openechelon.models import (
    Artifact,
    ArtifactKind,
    Assignment,
    Capability,
    Employee,
    ExecutionResource,
    Grant,
    Message,
    MessageType,
    Quota,
    Rank,
    ReasoningLevel,
    Review,
    ReviewVerdict,
    RiskLevel,
    RoutePath,
    RoutingDecision,
    RoutingOutcome,
    RuntimeKind,
    Task,
    TaskState,
)
from openechelon.models.resource import ResourceClass


def make_employee(**overrides: Any) -> Employee:
    defaults: dict[str, Any] = {
        "display_name": "Test Worker",
        "title": "Worker",
        "rank": Rank.WORKER,
        "department_id": "dept_x",
        "manager_id": "emp_manager",
    }
    defaults.update(overrides)
    return Employee(**defaults)


def make_task(**overrides: Any) -> Task:
    defaults: dict[str, Any] = {
        "objective": "Support the parent objective",
        "instruction": "Inspect these files for duplicated validation logic",
        "expected_output": "- file\n- function\n- pattern",
        "task_class": "structured_extraction",
        "created_by": "emp_manager",
    }
    defaults.update(overrides)
    return Task(**defaults)


# --- Principle 4 and 30: identity is persistent and separate from a model -----


def test_employee_carries_no_provider_or_model_field() -> None:
    """An employee that named a model would be a model wearing a job title."""
    forbidden = {"model", "model_ref", "provider", "session_id", "process_id"}
    assert forbidden.isdisjoint(Employee.model_fields)


def test_ceo_reports_to_the_human_owner_not_an_employee() -> None:
    """Principle 2: the organization never places itself above its owner."""
    ceo = Employee(
        display_name="CEO",
        title="Chief Executive",
        rank=Rank.CEO,
        department_id="dept_exec",
        manager_id=None,
    )
    assert ceo.manager_id is None

    with pytest.raises(ValidationError, match="reports to the human owner"):
        Employee(
            display_name="CEO",
            title="Chief Executive",
            rank=Rank.CEO,
            department_id="dept_exec",
            manager_id="emp_someone",
        )


def test_non_ceo_requires_a_manager() -> None:
    with pytest.raises(ValidationError, match="requires a manager"):
        make_employee(manager_id=None)


def test_employee_cannot_manage_themselves() -> None:
    with pytest.raises(ValidationError, match="cannot manage themselves"):
        Employee(
            employee_id="emp_self",
            display_name="Loop",
            title="Worker",
            rank=Rank.WORKER,
            department_id="dept_x",
            manager_id="emp_self",
        )


def test_inactive_employee_keeps_its_history() -> None:
    """Principle 30: identity accumulates history across sessions."""
    employee = make_employee(active=False)
    assert employee.employee_id
    assert employee.active is False


# --- Principle 7: reasoning ceiling is a ceiling, not a target ----------------


def test_rank_defines_a_reasoning_ceiling() -> None:
    worker = make_employee(rank=Rank.WORKER)
    director = make_employee(rank=Rank.DIRECTOR)
    assert worker.effective_reasoning_ceiling is ReasoningLevel.NONE
    assert director.effective_reasoning_ceiling is ReasoningLevel.HIGH
    assert director.effective_reasoning_ceiling > worker.effective_reasoning_ceiling


def test_reasoning_exceeding_the_role_ceiling_must_be_marked_escalated() -> None:
    """The defect this repo shipped in Principle 7: min() silently capped it."""
    with pytest.raises(ValidationError, match="Principle 7 requires escalation"):
        RoutingDecision(
            task_id="task_1",
            task_class="structured_extraction",
            attempt=1,
            selected_resource_id="res_1",
            selected_class=ResourceClass.LOCAL_SMALL,
            reasoning_requested=ReasoningLevel.HIGH,
            role_ceiling=ReasoningLevel.LOW,
            rationale="attempted under-powered run",
            escalated=False,
        )


# --- Principle 17: delegation produces traceable trees -----------------------


def test_task_cannot_be_its_own_parent_or_dependency() -> None:
    with pytest.raises(ValidationError, match="own parent"):
        make_task(task_id="task_a", parent_task_id="task_a")
    with pytest.raises(ValidationError, match="depend on itself"):
        make_task(task_id="task_a", depends_on=["task_a"])


def test_task_state_machine_rejects_illegal_transitions() -> None:
    task = make_task(owner_id="emp_worker", state=TaskState.RUNNING)
    task.transition_to(TaskState.AWAITING_REVIEW)
    assert task.state is TaskState.AWAITING_REVIEW

    with pytest.raises(ValueError, match="illegal task transition"):
        task.transition_to(TaskState.RUNNING)


def test_cancelled_is_reachable_from_every_non_terminal_state() -> None:
    """Principle 31: long-running autonomous work stays interruptible."""
    from openechelon.models.task import ALLOWED_TRANSITIONS, TERMINAL_STATES

    for state, allowed in ALLOWED_TRANSITIONS.items():
        if state in TERMINAL_STATES:
            continue
        assert TaskState.CANCELLED in allowed, f"{state.value} cannot be cancelled"


def test_assignment_attempts_must_be_contiguous() -> None:
    with pytest.raises(ValidationError, match="contiguous"):
        make_task(
            owner_id="emp_worker",
            state=TaskState.RUNNING,
            assignments=[
                Assignment(employee_id="emp_a", reasoning_used=ReasoningLevel.NONE, attempt=1),
                Assignment(employee_id="emp_b", reasoning_used=ReasoningLevel.LOW, attempt=3),
            ],
        )


def test_non_created_task_requires_an_owner() -> None:
    with pytest.raises(ValidationError, match="requires an owner"):
        make_task(state=TaskState.RUNNING)


# --- Principles 15 and 16: structured messages on authority paths ------------


def test_cross_team_message_must_record_who_authorized_it() -> None:
    with pytest.raises(ValidationError, match="who authorized it"):
        Message(
            type=MessageType.QUESTION,
            sender_id="emp_a",
            recipient_id="emp_b",
            subject="direct question",
            route=RoutePath.AUTHORIZED_DIRECT,
        )


def test_reporting_line_message_must_not_claim_an_authorizer() -> None:
    with pytest.raises(ValidationError, match="only meaningful for an authorized direct route"):
        Message(
            type=MessageType.REPORT,
            sender_id="emp_a",
            recipient_id="emp_b",
            subject="status",
            authorized_by="emp_boss",
        )


def test_artifact_message_must_carry_an_artifact() -> None:
    with pytest.raises(ValidationError, match="must reference at least one artifact"):
        Message(
            type=MessageType.ARTIFACT,
            sender_id="emp_a",
            recipient_id="emp_b",
            subject="here is the work",
        )


def test_approval_must_name_the_task_it_approves() -> None:
    with pytest.raises(ValidationError, match="must reference a task"):
        Message(
            type=MessageType.APPROVAL,
            sender_id="emp_boss",
            recipient_id="emp_a",
            subject="approved",
        )


# --- Principles 18 and 19: artifacts and independent review ------------------


def test_artifact_provenance_cannot_be_circular() -> None:
    with pytest.raises(ValidationError, match="derived from itself"):
        Artifact(
            artifact_id="art_1",
            kind=ArtifactKind.REPORT,
            title="Report",
            produced_by="emp_a",
            task_id="task_1",
            content_ref="artifacts/report.md",
            derived_from=["art_1"],
        )


def test_review_independence_is_recorded_not_assumed() -> None:
    with pytest.raises(ValidationError, match="independent by definition"):
        Review(
            task_id="task_1",
            reviewer_id="emp_reviewer",
            reviewed_employee_id="emp_author",
            verdict=ReviewVerdict.ACCEPTED,
            rationale="looks fine",
            independent_reviewer=False,
            independent_resource=True,
        )


def test_rejection_must_state_what_would_need_to_change() -> None:
    with pytest.raises(ValidationError, match="what would need to change"):
        Review(
            task_id="task_1",
            reviewer_id="emp_reviewer",
            reviewed_employee_id="emp_author",
            verdict=ReviewVerdict.REJECTED,
            rationale="not good enough",
            independent_reviewer=True,
            independent_resource=True,
        )


# --- Principles 22 and 23: organizational permissions ------------------------


def test_grant_cannot_be_self_issued() -> None:
    with pytest.raises(ValidationError, match="self-issued"):
        Grant(
            employee_id="emp_a",
            capability=Capability.SHELL_EXECUTE,
            granted_by="emp_a",
        )


def test_lowering_required_authority_requires_a_justification() -> None:
    with pytest.raises(ValidationError, match="requires a justification"):
        Grant(
            employee_id="emp_a",
            capability=Capability.DEPLOY_PRODUCTION,
            granted_by="emp_boss",
            risk_override=RiskLevel.ROUTINE,
        )

    allowed = Grant(
        employee_id="emp_a",
        capability=Capability.DEPLOY_PRODUCTION,
        granted_by="emp_boss",
        risk_override=RiskLevel.EXECUTIVE,
        justification="staging-only deployment target",
    )
    assert allowed.required_authority is RiskLevel.EXECUTIVE


def test_irreversible_capabilities_default_to_human_authority() -> None:
    """Principle 23: risk determines the required approval height."""
    for capability in (
        Capability.DELETE_DATA,
        Capability.DEPLOY_PRODUCTION,
        Capability.MODIFY_PERMISSIONS,
        Capability.RESTRUCTURE_ORGANIZATION,
    ):
        grant = Grant(employee_id="emp_a", capability=capability, granted_by="emp_boss")
        assert grant.required_authority is RiskLevel.HUMAN


# --- Principles 9 and 11: resources are governed and replaceable -------------


def test_only_the_resource_record_names_a_provider() -> None:
    """Principle 11: provider specifics live behind adapters, not in identity."""
    assert "provider" in ExecutionResource.model_fields
    assert "provider" not in Employee.model_fields
    assert "provider" not in Task.model_fields


def test_exhausted_quota_becomes_available_after_its_reset_window() -> None:
    from datetime import timedelta

    from openechelon.models.common import utcnow

    quota = Quota(limit=10, used=10, window_resets_at=utcnow() + timedelta(hours=1))
    assert quota.exhausted
    assert not quota.available_at()
    assert quota.available_at(utcnow() + timedelta(hours=2))


def test_resource_cannot_serve_above_its_reasoning_capability() -> None:
    resource = ExecutionResource(
        name="small local",
        resource_class=ResourceClass.LOCAL_SMALL,
        runtime=RuntimeKind.LOCAL_INFERENCE,
        provider="ollama",
        model_ref="qwen3:4b",
        max_reasoning=ReasoningLevel.NONE,
        private=True,
    )
    assert resource.can_serve(ReasoningLevel.NONE)
    assert not resource.can_serve(ReasoningLevel.HIGH)


def test_local_inference_must_be_marked_private() -> None:
    with pytest.raises(ValidationError, match="private by definition"):
        ExecutionResource(
            name="local",
            resource_class=ResourceClass.LOCAL_SMALL,
            runtime=RuntimeKind.LOCAL_INFERENCE,
            provider="ollama",
            model_ref="qwen3:4b",
            private=False,
        )


# --- Principles 24 to 26: observability, auditability, learning --------------


def test_routing_outcome_may_only_be_set_from_a_verification() -> None:
    """Principle 26 learns from outcomes; an assumed outcome teaches noise."""
    with pytest.raises(ValidationError, match="only be set from a verification"):
        RoutingDecision(
            task_id="task_1",
            task_class="structured_extraction",
            attempt=1,
            selected_resource_id="res_1",
            selected_class=ResourceClass.LOCAL_SMALL,
            reasoning_requested=ReasoningLevel.NONE,
            role_ceiling=ReasoningLevel.LOW,
            rationale="cheap rung accepted",
            outcome=RoutingOutcome.CORRECT_ACCEPT,
        )


def test_scored_decision_must_record_threshold_and_estimator() -> None:
    with pytest.raises(ValidationError, match="threshold it was judged against"):
        RoutingDecision(
            task_id="task_1",
            task_class="structured_extraction",
            attempt=1,
            selected_resource_id="res_1",
            selected_class=ResourceClass.LOCAL_SMALL,
            reasoning_requested=ReasoningLevel.NONE,
            role_ceiling=ReasoningLevel.LOW,
            rationale="scored",
            sufficiency_score=0.9,
        )


def test_performance_outcomes_cannot_exceed_assignments() -> None:
    from openechelon.models.identity import PerformanceRecord

    with pytest.raises(ValidationError, match="exceed assignments"):
        PerformanceRecord(task_class="structured_extraction", assignments=2, accepted=3)


def test_acceptance_rate_is_none_without_evidence() -> None:
    """A fabricated rate would corrupt the routing history it feeds."""
    from openechelon.models.identity import PerformanceRecord

    assert PerformanceRecord(task_class="x").acceptance_rate is None
    assert PerformanceRecord(task_class="x", assignments=4, accepted=3).acceptance_rate == 0.75
