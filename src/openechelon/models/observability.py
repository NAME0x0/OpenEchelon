"""Execution and routing records.

Principle 24 lists what every meaningful execution must record. Principle 25
requires that the chain reach the final answer. These records are the ones that
make both claims checkable rather than aspirational, so the field list here
tracks Principle 24 deliberately closely.

Principle 26 adds a second purpose: routing decisions stored alongside their
eventual verified outcome are the training signal that lets the organization
learn which resources work for which task classes. A routing decision without a
recorded outcome teaches nothing.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from openechelon.models.common import (
    Identifier,
    ReasoningLevel,
    Record,
    new_id,
)
from openechelon.models.resource import ResourceClass


class ExecutionRecord(Record):
    """What actually happened when a task was executed once."""

    execution_record_id: Identifier = Field(default_factory=lambda: new_id("exec"))
    task_id: Identifier
    assignment_id: Identifier
    employee_id: Identifier
    supervisor_id: Identifier | None = None
    resource_id: Identifier
    resource_class: ResourceClass
    provider: str
    model_ref: str
    reasoning: ReasoningLevel

    duration_ms: int = Field(ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cost: float = Field(default=0.0, ge=0.0)
    quota_units_consumed: int = Field(default=0, ge=0)

    tools_used: list[str] = Field(default_factory=list)
    artifact_ids: list[Identifier] = Field(default_factory=list)

    succeeded: bool
    failure_kind: str | None = None
    review_id: Identifier | None = None

    model_config = Record.model_config | {"protected_namespaces": ()}

    @model_validator(mode="after")
    def _failure_is_explained(self) -> ExecutionRecord:
        if not self.succeeded and not self.failure_kind:
            raise ValueError("a failed execution must record a failure kind")
        if self.succeeded and self.failure_kind:
            raise ValueError("a successful execution must not carry a failure kind")
        return self


class RoutingOutcome(StrEnum):
    """What the routing decision turned out to be worth.

    ``PENDING`` is the honest default. A decision whose outcome is unknown must
    not be scored as if it were correct.
    """

    PENDING = "pending"
    CORRECT_ACCEPT = "correct_accept"
    FALSE_ACCEPT = "false_accept"
    CORRECT_ESCALATE = "correct_escalate"
    FALSE_ESCALATE = "false_escalate"


class RoutingDecision(Record):
    """One decision by the Resource Governor, with the evidence behind it.

    ADR 0003 requires every routing decision to record its estimator score, the
    threshold applied, and the outcome, so estimators can be re-scored against
    ground truth as verification arrives.
    """

    decision_id: Identifier = Field(default_factory=lambda: new_id("route"))
    task_id: Identifier
    task_class: str
    attempt: int = Field(ge=1)

    selected_resource_id: Identifier
    selected_class: ResourceClass
    reasoning_requested: ReasoningLevel
    role_ceiling: ReasoningLevel

    considered_resource_ids: list[Identifier] = Field(default_factory=list)
    rationale: str = Field(min_length=1)

    sufficiency_score: float | None = Field(default=None, ge=0.0, le=1.0)
    """Calibrated probability that the produced answer is good enough.

    ``None`` when the estimator abstained. Abstention escalates (ADR 0003)."""

    threshold_applied: float | None = Field(default=None, ge=0.0, le=1.0)
    estimator_id: str | None = None
    escalated: bool = False
    outcome: RoutingOutcome = RoutingOutcome.PENDING
    verified_by_review_id: Identifier | None = None

    @model_validator(mode="after")
    def _decision_is_explainable(self) -> RoutingDecision:
        if self.sufficiency_score is not None and self.threshold_applied is None:
            raise ValueError("a scored decision must record the threshold it was judged against")
        if self.sufficiency_score is not None and self.estimator_id is None:
            raise ValueError("a scored decision must name the estimator that produced the score")
        if self.outcome is not RoutingOutcome.PENDING and self.verified_by_review_id is None:
            raise ValueError(
                "a routing outcome may only be set from a verification, not from an assumption"
            )
        if self.reasoning_requested > self.role_ceiling and not self.escalated:
            raise ValueError(
                "requested reasoning exceeds the role ceiling; Principle 7 requires escalation "
                "rather than running under-powered"
            )
        return self
