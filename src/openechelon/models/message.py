"""The structured message envelope.

Principle 15: internal communication carries explicit semantic type, so it can be
routed, permitted, audited, and automated. Principle 16: messages follow
authority paths by default, and a direct edge outside that path is an explicit,
recorded exception rather than an emergent property of a group chat.

Natural language lives in ``body``. Everything the runtime needs to act on lives
outside it.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from openechelon.models.common import Identifier, Record, new_id


class MessageType(StrEnum):
    TASK = "task"
    DELEGATION = "delegation"
    REPORT = "report"
    QUESTION = "question"
    ANSWER = "answer"
    STATUS = "status"
    ARTIFACT = "artifact"
    REVIEW = "review"
    APPROVAL = "approval"
    REJECTION = "rejection"
    ESCALATION = "escalation"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_GRANT = "resource_grant"
    RESOURCE_DENIAL = "resource_denial"
    IMPLEMENTATION_REQUEST = "implementation_request"
    RESEARCH_REQUEST = "research_request"
    VERIFICATION_REQUEST = "verification_request"


DOWNWARD: frozenset[MessageType] = frozenset(
    {
        MessageType.TASK,
        MessageType.DELEGATION,
        MessageType.ANSWER,
        MessageType.APPROVAL,
        MessageType.REJECTION,
        MessageType.RESOURCE_GRANT,
        MessageType.RESOURCE_DENIAL,
        MessageType.IMPLEMENTATION_REQUEST,
        MessageType.RESEARCH_REQUEST,
        MessageType.VERIFICATION_REQUEST,
    }
)
"""Types that normally travel from a manager toward a report."""

UPWARD: frozenset[MessageType] = frozenset(
    {
        MessageType.REPORT,
        MessageType.QUESTION,
        MessageType.STATUS,
        MessageType.ARTIFACT,
        MessageType.ESCALATION,
        MessageType.RESOURCE_REQUEST,
    }
)
"""Types that normally travel from a report toward a manager."""


class RoutePath(StrEnum):
    """How a message is authorized to reach its recipient."""

    REPORTING_LINE = "reporting_line"
    """Default. Sender and recipient are adjacent in the hierarchy."""

    AUTHORIZED_DIRECT = "authorized_direct"
    """A temporary cross-team edge opened for a task by a common superior."""

    HUMAN_CHANNEL = "human_channel"
    """Between the CEO and the human owner."""


class Message(Record):
    """One typed message between two organizational participants."""

    message_id: Identifier = Field(default_factory=lambda: new_id("msg"))
    type: MessageType
    sender_id: Identifier
    recipient_id: Identifier
    task_id: Identifier | None = None
    in_reply_to: Identifier | None = None
    route: RoutePath = RoutePath.REPORTING_LINE

    authorized_by: Identifier | None = None
    """Required for ``AUTHORIZED_DIRECT``: who opened the cross-team edge."""

    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(default="")
    """Natural-language payload. Never the place for routing information."""

    artifact_ids: list[Identifier] = Field(default_factory=list)
    references: list[Identifier] = Field(default_factory=list)
    """Evidence the recipient can inspect. Principle 14: compression must not
    destroy the path back to the underlying work."""

    @model_validator(mode="after")
    def _routing_is_authorized(self) -> Message:
        if self.sender_id == self.recipient_id:
            raise ValueError("a message cannot be addressed to its sender")
        if self.route is RoutePath.AUTHORIZED_DIRECT and self.authorized_by is None:
            raise ValueError("an authorized direct message must record who authorized it")
        if self.route is not RoutePath.AUTHORIZED_DIRECT and self.authorized_by is not None:
            raise ValueError("authorized_by is only meaningful for an authorized direct route")
        if self.type is MessageType.ARTIFACT and not self.artifact_ids:
            raise ValueError("an artifact message must reference at least one artifact")
        if self.type in {MessageType.APPROVAL, MessageType.REJECTION} and self.task_id is None:
            raise ValueError(f"a {self.type.value} message must reference a task")
        return self
