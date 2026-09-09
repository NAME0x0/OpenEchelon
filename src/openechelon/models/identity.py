"""Employee and department records.

Principle 4: an employee is a persistent organizational identity, not a model.
Nothing in this module names a provider, and that omission is the point — the
execution resource is assigned per task, in ``resource.py``.

Principle 5: an ``Employee`` record is a logical identity. It exists whether or
not anything is currently running on its behalf.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from openechelon.models.common import (
    DEFAULT_REASONING_CEILING,
    Identifier,
    Rank,
    ReasoningLevel,
    Record,
    new_id,
)


class Department(Record):
    """A unit of the organization. Departments may nest."""

    department_id: Identifier = Field(default_factory=lambda: new_id("dept"))
    name: str = Field(min_length=1, max_length=120)
    charter: str = Field(min_length=1)
    """What this department is accountable for. Used when routing work."""

    parent_department_id: Identifier | None = None
    head_employee_id: Identifier | None = None

    @model_validator(mode="after")
    def _no_self_parent(self) -> Department:
        if self.parent_department_id == self.department_id:
            raise ValueError("a department cannot be its own parent")
        return self


class PerformanceRecord(Record):
    """Accumulated history for one employee on one task class.

    Principle 26 requires the organization to learn which resources work for
    which task classes. That learning has to be stored against an identity that
    outlives any single session, which is what makes Principle 4 load-bearing
    rather than philosophical.
    """

    task_class: str = Field(min_length=1, max_length=120)
    assignments: int = Field(default=0, ge=0)
    accepted: int = Field(default=0, ge=0)
    rejected_at_review: int = Field(default=0, ge=0)
    escalated: int = Field(default=0, ge=0)

    @property
    def acceptance_rate(self) -> float | None:
        """``None`` rather than a fabricated number when there is no evidence."""
        if self.assignments == 0:
            return None
        return self.accepted / self.assignments

    @model_validator(mode="after")
    def _outcomes_within_assignments(self) -> PerformanceRecord:
        outcomes = self.accepted + self.rejected_at_review + self.escalated
        if outcomes > self.assignments:
            raise ValueError(
                f"recorded outcomes ({outcomes}) exceed assignments ({self.assignments})"
            )
        return self


class Employee(Record):
    """A persistent organizational identity.

    Deliberately absent: any model name, provider, session handle, or process
    identifier. An employee that carried those would be a model wearing a job
    title, which Principle 4 exists to prevent.
    """

    employee_id: Identifier = Field(default_factory=lambda: new_id("emp"))
    display_name: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=120)
    rank: Rank
    department_id: Identifier
    manager_id: Identifier | None = None
    """``None`` only for the CEO, who reports to the human owner."""

    responsibilities: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    """Task classes this employee is considered suitable for."""

    reasoning_ceiling: ReasoningLevel | None = None
    """Overrides the rank default. A ceiling on spending, not a target."""

    active: bool = True
    """Inactive employees keep their history. Principle 30."""

    performance: list[PerformanceRecord] = Field(default_factory=list)

    @property
    def effective_reasoning_ceiling(self) -> ReasoningLevel:
        return self.reasoning_ceiling or DEFAULT_REASONING_CEILING[self.rank]

    def performance_for(self, task_class: str) -> PerformanceRecord | None:
        return next((p for p in self.performance if p.task_class == task_class), None)

    @model_validator(mode="after")
    def _reporting_line_is_coherent(self) -> Employee:
        if self.manager_id == self.employee_id:
            raise ValueError("an employee cannot manage themselves")
        if self.rank is Rank.CEO and self.manager_id is not None:
            raise ValueError("the CEO reports to the human owner, not to an employee")
        if self.rank is not Rank.CEO and self.manager_id is None:
            raise ValueError(f"{self.rank.value} requires a manager")
        seen: set[str] = set()
        for record in self.performance:
            if record.task_class in seen:
                raise ValueError(f"duplicate performance record for task class {record.task_class}")
            seen.add(record.task_class)
        return self
