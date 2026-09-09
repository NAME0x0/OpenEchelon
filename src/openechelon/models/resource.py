"""Execution resources and quota.

Principles 9 and 11: frontier models, subscription sessions, API budgets, GPU
time, and concurrency are scarce organizational resources that must be governed,
and no provider may be architecturally required.

An ``ExecutionResource`` is the only place in the model where a provider is
named. Employees do not reference it; tasks are matched to it at assignment
time. Deleting a provider from a deployment should therefore never invalidate an
employee record.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

from openechelon.models.common import (
    Identifier,
    ReasoningLevel,
    Record,
    new_id,
    utcnow,
)


class ResourceClass(StrEnum):
    """Cost and capability tier. The ladder Principle 8 escalates along."""

    LOCAL_SMALL = "local_small"
    LOCAL_LARGE = "local_large"
    FRONTIER_ECONOMY = "frontier_economy"
    FRONTIER_STANDARD = "frontier_standard"
    FRONTIER_PREMIUM = "frontier_premium"

    @property
    def tier(self) -> int:
        return _CLASS_ORDER[self]


_CLASS_ORDER: dict[ResourceClass, int] = {
    ResourceClass.LOCAL_SMALL: 0,
    ResourceClass.LOCAL_LARGE: 1,
    ResourceClass.FRONTIER_ECONOMY: 2,
    ResourceClass.FRONTIER_STANDARD: 3,
    ResourceClass.FRONTIER_PREMIUM: 4,
}

ESCALATION_LADDER: tuple[ResourceClass, ...] = (
    ResourceClass.LOCAL_SMALL,
    ResourceClass.LOCAL_LARGE,
    ResourceClass.FRONTIER_ECONOMY,
    ResourceClass.FRONTIER_STANDARD,
    ResourceClass.FRONTIER_PREMIUM,
)


class RuntimeKind(StrEnum):
    """How the resource is invoked. Provider specifics live behind adapters."""

    LOCAL_INFERENCE = "local_inference"
    HOSTED_API = "hosted_api"
    CLI_AGENT = "cli_agent"
    EXTERNAL_RUNTIME = "external_runtime"


class Quota(Record):
    """Remaining allowance for a resource within a reset window.

    Modelled as a record rather than a counter because Principle 9 requires
    awareness of reset windows, not only of remaining units. A resource that is
    exhausted for the next four minutes is a different routing input from one
    exhausted for the next four hours.
    """

    limit: int | None = Field(default=None, ge=0)
    """``None`` means unmetered, not unlimited."""

    used: int = Field(default=0, ge=0)
    window_resets_at: datetime | None = None

    @property
    def remaining(self) -> int | None:
        if self.limit is None:
            return None
        return max(self.limit - self.used, 0)

    @property
    def exhausted(self) -> bool:
        remaining = self.remaining
        return remaining is not None and remaining <= 0

    def available_at(self, when: datetime | None = None) -> bool:
        when = when or utcnow()
        if not self.exhausted:
            return True
        return self.window_resets_at is not None and when >= self.window_resets_at


class ExecutionResource(Record):
    """A concrete way of executing work.

    The only provider-aware record in the organizational model.
    """

    resource_id: Identifier = Field(default_factory=lambda: new_id("res"))
    name: str = Field(min_length=1, max_length=120)
    resource_class: ResourceClass
    runtime: RuntimeKind
    provider: str = Field(min_length=1, max_length=80)
    """Adapter key, e.g. ``ollama``, ``anthropic``, ``codex-cli``. Free text so
    that adding a provider needs an adapter, not a schema change."""

    model_ref: str = Field(min_length=1, max_length=160)
    max_reasoning: ReasoningLevel = ReasoningLevel.NONE
    context_window: int | None = Field(default=None, gt=0)
    cost_per_million_input: float = Field(default=0.0, ge=0.0)
    cost_per_million_output: float = Field(default=0.0, ge=0.0)
    """Zero is correct for local inference: no marginal monetary cost. Local
    execution still consumes concurrency and time, which are governed separately."""

    max_concurrency: int = Field(default=1, ge=1)
    quota: Quota = Field(default_factory=Quota)
    available: bool = True
    supports_tools: bool = False
    private: bool = False
    """True when data does not leave the owner's machine. A routing input in its
    own right, not a footnote — some task classes may not leave local hardware."""

    model_config = Record.model_config | {"protected_namespaces": ()}

    def can_serve(self, required_reasoning: ReasoningLevel) -> bool:
        return (
            self.available and not self.quota.exhausted and self.max_reasoning >= required_reasoning
        )

    @model_validator(mode="after")
    def _local_resources_are_private(self) -> ExecutionResource:
        if self.runtime is RuntimeKind.LOCAL_INFERENCE and not self.private:
            raise ValueError("local inference is private by definition; set private=True")
        return self
