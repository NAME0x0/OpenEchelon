"""Shared primitives for the Phase 0 organizational data model.

Every record in the model is identified, timestamped, and versioned. Those three
properties are what make Principles 24 and 25 achievable: an organization that
cannot name a record, say when it changed, or say which schema produced it
cannot be audited afterwards.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1
"""Version of the organizational record schema.

Bumped when a change would make an older stored record invalid. Records carry
the version they were written under so a migration can find them.
"""


def new_id(prefix: str) -> str:
    """Generate a prefixed, sortable-enough identifier.

    The prefix exists so an identifier is self-describing in a log line. Reading
    ``emp_1f0c...`` in a trace should not require a lookup to know what it is.
    """
    return f"{prefix}_{uuid.uuid4().hex}"


def utcnow() -> datetime:
    return datetime.now(UTC)


Identifier = Annotated[str, Field(min_length=3, max_length=128)]


class Rank(StrEnum):
    """Organizational rank.

    Rank is not decoration. It bounds reasoning allowance (Principle 7),
    determines default information access (Principle 13), and defines the
    reporting path a message follows (Principle 16).
    """

    WORKER = "worker"
    SPECIALIST = "specialist"
    TEAM_LEAD = "team_lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"
    CEO = "ceo"

    @property
    def level(self) -> int:
        """Ordinal position, lowest first. Used for authority comparisons."""
        return _RANK_ORDER[self]

    def outranks(self, other: Rank) -> bool:
        return self.level > other.level


_RANK_ORDER: dict[Rank, int] = {
    Rank.WORKER: 0,
    Rank.SPECIALIST: 1,
    Rank.TEAM_LEAD: 2,
    Rank.MANAGER: 3,
    Rank.DIRECTOR: 4,
    Rank.EXECUTIVE: 5,
    Rank.CEO: 6,
}


class ReasoningLevel(StrEnum):
    """Reasoning effort, as a budgeted resource rather than a quality dial."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"

    @property
    def level(self) -> int:
        return _REASONING_ORDER[self]

    def __lt__(self, other: ReasoningLevel) -> bool:  # type: ignore[override]
        return self.level < other.level

    def __le__(self, other: ReasoningLevel) -> bool:  # type: ignore[override]
        return self.level <= other.level

    def __gt__(self, other: ReasoningLevel) -> bool:  # type: ignore[override]
        return self.level > other.level

    def __ge__(self, other: ReasoningLevel) -> bool:  # type: ignore[override]
        return self.level >= other.level


_REASONING_ORDER: dict[ReasoningLevel, int] = {
    ReasoningLevel.NONE: 0,
    ReasoningLevel.LOW: 1,
    ReasoningLevel.MEDIUM: 2,
    ReasoningLevel.HIGH: 3,
    ReasoningLevel.MAXIMUM: 4,
}


DEFAULT_REASONING_CEILING: dict[Rank, ReasoningLevel] = {
    Rank.WORKER: ReasoningLevel.NONE,
    Rank.SPECIALIST: ReasoningLevel.LOW,
    Rank.TEAM_LEAD: ReasoningLevel.LOW,
    Rank.MANAGER: ReasoningLevel.MEDIUM,
    Rank.DIRECTOR: ReasoningLevel.HIGH,
    Rank.EXECUTIVE: ReasoningLevel.HIGH,
    Rank.CEO: ReasoningLevel.MAXIMUM,
}
"""Default reasoning ceiling per rank.

A ceiling, never a target. Principle 7: a task needing less than the ceiling
runs at what it needs; a task needing more escalates rather than running
under-powered.
"""


class Record(BaseModel):
    """Base for every persisted organizational record."""

    model_config = ConfigDict(extra="forbid", frozen=False, use_enum_values=False)

    schema_version: int = SCHEMA_VERSION
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def touch(self) -> None:
        self.updated_at = utcnow()
