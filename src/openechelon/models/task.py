"""Tasks and the delegation tree.

Principle 17: delegation creates explicit parent-child relationships and must not
disappear into conversational history. A ``Task`` therefore records its parent,
its creator, its owner, its supervisor, and every resource it consumed — not as
a log line, but as structure the runtime can query.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from openechelon.models.common import Identifier, ReasoningLevel, Record, new_id


class TaskState(StrEnum):
    CREATED = "created"
    ASSIGNED = "assigned"
    RUNNING = "running"
    BLOCKED = "blocked"
    AWAITING_REVIEW = "awaiting_review"
    AWAITING_APPROVAL = "awaiting_approval"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"


TERMINAL_STATES: frozenset[TaskState] = frozenset(
    {TaskState.COMPLETED, TaskState.REJECTED, TaskState.CANCELLED, TaskState.FAILED}
)

ALLOWED_TRANSITIONS: dict[TaskState, frozenset[TaskState]] = {
    TaskState.CREATED: frozenset({TaskState.ASSIGNED, TaskState.CANCELLED}),
    TaskState.ASSIGNED: frozenset({TaskState.RUNNING, TaskState.ESCALATED, TaskState.CANCELLED}),
    TaskState.RUNNING: frozenset(
        {
            TaskState.BLOCKED,
            TaskState.AWAITING_REVIEW,
            TaskState.AWAITING_APPROVAL,
            TaskState.ESCALATED,
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        }
    ),
    TaskState.BLOCKED: frozenset({TaskState.RUNNING, TaskState.ESCALATED, TaskState.CANCELLED}),
    TaskState.AWAITING_REVIEW: frozenset(
        {TaskState.COMPLETED, TaskState.REJECTED, TaskState.ESCALATED, TaskState.CANCELLED}
    ),
    TaskState.AWAITING_APPROVAL: frozenset(
        {TaskState.RUNNING, TaskState.REJECTED, TaskState.CANCELLED}
    ),
    TaskState.ESCALATED: frozenset({TaskState.ASSIGNED, TaskState.CANCELLED, TaskState.FAILED}),
    TaskState.COMPLETED: frozenset(),
    TaskState.REJECTED: frozenset({TaskState.ASSIGNED, TaskState.CANCELLED}),
    TaskState.CANCELLED: frozenset(),
    TaskState.FAILED: frozenset({TaskState.ESCALATED, TaskState.CANCELLED}),
}
"""Permitted state transitions.

Enumerated rather than left to convention so that an illegal transition is a
detectable defect. Principle 31 requires that work be interruptible, which is
why ``CANCELLED`` is reachable from every non-terminal state.
"""


class FailureKind(StrEnum):
    """Structured failure information.

    Principle 20: failure produces information that informs a deliberate
    response. An untyped failure invites the retry loop the principle forbids.
    """

    INSUFFICIENT_CAPABILITY = "insufficient_capability"
    REASONING_CEILING_EXCEEDED = "reasoning_ceiling_exceeded"
    MISSING_CONTEXT = "missing_context"
    MISSING_PERMISSION = "missing_permission"
    QUOTA_EXHAUSTED = "quota_exhausted"
    TOOL_FAILURE = "tool_failure"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    AMBIGUOUS_ASSIGNMENT = "ambiguous_assignment"
    REVIEW_REJECTED = "review_rejected"
    TIMEOUT = "timeout"


class EscalationRecommendation(StrEnum):
    RETRY_SAME = "retry_same"
    RAISE_REASONING = "raise_reasoning"
    STRONGER_RESOURCE = "stronger_resource"
    ADD_CONTEXT = "add_context"
    DIFFERENT_SPECIALIST = "different_specialist"
    SPLIT_TASK = "split_task"
    REQUEST_RESEARCH = "request_research"
    ASK_HUMAN = "ask_human"
    ABANDON = "abandon"


class Failure(Record):
    """Why an attempt did not succeed, and what should happen next."""

    kind: FailureKind
    detail: str = Field(min_length=1)
    attempt: int = Field(ge=1)
    confidence: float = Field(ge=0.0, le=1.0)
    """Reporter confidence that ``kind`` is the real cause, not a symptom."""

    recommendation: EscalationRecommendation


class Assignment(Record):
    """One attempt at a task by one employee using one execution resource.

    A task may have several. Keeping attempts as records rather than overwriting
    a single field is what allows Principle 26 to score resources against
    outcomes later.
    """

    assignment_id: Identifier = Field(default_factory=lambda: new_id("asgn"))
    employee_id: Identifier
    execution_record_id: Identifier | None = None
    reasoning_used: ReasoningLevel
    attempt: int = Field(ge=1)
    failure: Failure | None = None


class Task(Record):
    """A unit of delegated work.

    Every field here answers one of the questions Principle 17 requires a task to
    be traceable to: who created it, why it exists, its parent objective, who
    owns it, who supervises it, what it consumed, what it produced, who reviewed
    it, and what was decided.
    """

    task_id: Identifier = Field(default_factory=lambda: new_id("task"))
    parent_task_id: Identifier | None = None
    objective: str = Field(min_length=1)
    """Why this task exists, in terms of the parent objective."""

    instruction: str = Field(min_length=1)
    """What the assignee is to do. Bounded for workers (Principle 6)."""

    expected_output: str = Field(min_length=1)
    """What a complete answer looks like. Without this, review is opinion."""

    out_of_scope: list[str] = Field(default_factory=list)
    """Explicit prohibitions, e.g. 'do not redesign the architecture'."""

    task_class: str = Field(min_length=1, max_length=120)
    """Routing and performance-history key. Principles 8 and 26."""

    created_by: Identifier
    owner_id: Identifier | None = None
    supervisor_id: Identifier | None = None
    state: TaskState = TaskState.CREATED

    required_reasoning: ReasoningLevel = ReasoningLevel.NONE
    """Reasoning the task is judged to need, independent of who holds it."""

    depends_on: list[Identifier] = Field(default_factory=list)
    assignments: list[Assignment] = Field(default_factory=list)
    artifact_ids: list[Identifier] = Field(default_factory=list)
    review_ids: list[Identifier] = Field(default_factory=list)
    resolution: str | None = None

    @property
    def attempts(self) -> int:
        return len(self.assignments)

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    def can_transition_to(self, state: TaskState) -> bool:
        return state in ALLOWED_TRANSITIONS[self.state]

    def transition_to(self, state: TaskState) -> None:
        if not self.can_transition_to(state):
            raise ValueError(f"illegal task transition: {self.state.value} -> {state.value}")
        self.state = state
        self.touch()

    @model_validator(mode="after")
    def _structure_is_coherent(self) -> Task:
        if self.parent_task_id == self.task_id:
            raise ValueError("a task cannot be its own parent")
        if self.task_id in self.depends_on:
            raise ValueError("a task cannot depend on itself")
        if self.state is not TaskState.CREATED and self.owner_id is None:
            raise ValueError(f"a task in state {self.state.value} requires an owner")
        attempts = sorted(a.attempt for a in self.assignments)
        if attempts != list(range(1, len(attempts) + 1)):
            raise ValueError("assignment attempt numbers must be contiguous from 1")
        return self
