"""Phase 0 organizational data model.

Nine records, each traceable to the principle that requires it:

===========================  ==============================================
Record                       Requiring principle
===========================  ==============================================
``Employee``, ``Department``  4 (identity separate from model), 5, 30
``Grant``                     22 (organizational permissions), 23
``Task``, ``Assignment``      6 (bounded assignments), 17 (traceable trees)
``Failure``                   20 (escalation, not endless retry)
``Message``                   15 (structured), 16 (authority paths)
``Artifact``, ``Review``      18 (first-class artifacts), 19 (independence)
``ExecutionResource``         9 (scarce resources), 11 (replaceable providers)
``ExecutionRecord``           24 (observability)
``RoutingDecision``           25 (auditability), 26 (learning from outcomes)
===========================  ==============================================

The model deliberately contains no orchestration logic. It defines what the
organization *is*; ``openechelon.governor`` decides what happens next.
"""

from openechelon.models.artifact import (
    Artifact,
    ArtifactKind,
    Review,
    ReviewVerdict,
)
from openechelon.models.common import (
    DEFAULT_REASONING_CEILING,
    SCHEMA_VERSION,
    Identifier,
    Rank,
    ReasoningLevel,
    Record,
    new_id,
    utcnow,
)
from openechelon.models.identity import Department, Employee, PerformanceRecord
from openechelon.models.message import (
    DOWNWARD,
    UPWARD,
    Message,
    MessageType,
    RoutePath,
)
from openechelon.models.observability import (
    ExecutionRecord,
    RoutingDecision,
    RoutingOutcome,
)
from openechelon.models.permissions import (
    DEFAULT_RISK,
    MINIMUM_APPROVER_RANK,
    Capability,
    Grant,
    RiskLevel,
)
from openechelon.models.resource import (
    ESCALATION_LADDER,
    ExecutionResource,
    Quota,
    ResourceClass,
    RuntimeKind,
)
from openechelon.models.task import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    Assignment,
    EscalationRecommendation,
    Failure,
    FailureKind,
    Task,
    TaskState,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "DEFAULT_REASONING_CEILING",
    "DEFAULT_RISK",
    "DOWNWARD",
    "ESCALATION_LADDER",
    "MINIMUM_APPROVER_RANK",
    "SCHEMA_VERSION",
    "TERMINAL_STATES",
    "UPWARD",
    "Artifact",
    "ArtifactKind",
    "Assignment",
    "Capability",
    "Department",
    "Employee",
    "EscalationRecommendation",
    "ExecutionRecord",
    "ExecutionResource",
    "Failure",
    "FailureKind",
    "Grant",
    "Identifier",
    "Message",
    "MessageType",
    "PerformanceRecord",
    "Quota",
    "Rank",
    "ReasoningLevel",
    "Record",
    "ResourceClass",
    "Review",
    "ReviewVerdict",
    "RiskLevel",
    "RoutePath",
    "RoutingDecision",
    "RoutingOutcome",
    "RuntimeKind",
    "Task",
    "TaskState",
    "new_id",
    "utcnow",
]
