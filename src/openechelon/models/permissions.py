"""Permissions as organizational facts, not technical afterthoughts.

Principle 22: access depends on role and responsibility. Principle 23: actions
with real external consequence require an approval authority proportionate to
their risk. Both are represented here so that policy is data the runtime can
inspect, rather than prose inside a prompt.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from openechelon.models.common import Identifier, Rank, Record, new_id


class Capability(StrEnum):
    """A class of action an employee may be granted."""

    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    SHELL_EXECUTE = "shell.execute"
    NETWORK_FETCH = "network.fetch"
    BROWSER_CONTROL = "browser.control"
    REPOSITORY_READ = "repository.read"
    REPOSITORY_WRITE = "repository.write"
    CREDENTIAL_USE = "credential.use"
    PROVIDER_LOCAL = "provider.local"
    PROVIDER_FRONTIER = "provider.frontier"
    SPEND = "spend"
    MESSAGE_SEND_EXTERNAL = "message.send_external"
    PUBLISH_CONTENT = "publish.content"
    DELETE_DATA = "data.delete"
    DEPLOY_PRODUCTION = "deploy.production"
    MODIFY_PERMISSIONS = "permissions.modify"
    RESTRUCTURE_ORGANIZATION = "organization.restructure"


class RiskLevel(StrEnum):
    """How much authority an action requires before it may execute."""

    ROUTINE = "routine"
    """Executes under the employee's own grant."""

    SUPERVISED = "supervised"
    """Requires approval from the employee's manager."""

    EXECUTIVE = "executive"
    """Requires approval at executive rank."""

    HUMAN = "human"
    """Requires the human owner. Principle 2 makes this unappealable."""


DEFAULT_RISK: dict[Capability, RiskLevel] = {
    Capability.FILESYSTEM_READ: RiskLevel.ROUTINE,
    Capability.FILESYSTEM_WRITE: RiskLevel.ROUTINE,
    Capability.SHELL_EXECUTE: RiskLevel.SUPERVISED,
    Capability.NETWORK_FETCH: RiskLevel.ROUTINE,
    Capability.BROWSER_CONTROL: RiskLevel.ROUTINE,
    Capability.REPOSITORY_READ: RiskLevel.ROUTINE,
    Capability.REPOSITORY_WRITE: RiskLevel.SUPERVISED,
    Capability.CREDENTIAL_USE: RiskLevel.SUPERVISED,
    Capability.PROVIDER_LOCAL: RiskLevel.ROUTINE,
    Capability.PROVIDER_FRONTIER: RiskLevel.SUPERVISED,
    Capability.SPEND: RiskLevel.EXECUTIVE,
    Capability.MESSAGE_SEND_EXTERNAL: RiskLevel.EXECUTIVE,
    Capability.PUBLISH_CONTENT: RiskLevel.EXECUTIVE,
    Capability.DELETE_DATA: RiskLevel.HUMAN,
    Capability.DEPLOY_PRODUCTION: RiskLevel.HUMAN,
    Capability.MODIFY_PERMISSIONS: RiskLevel.HUMAN,
    Capability.RESTRUCTURE_ORGANIZATION: RiskLevel.HUMAN,
}
"""Default authority required per capability.

An organization may raise a requirement. Lowering one below its default must be
recorded, because it narrows the governance Principle 23 depends on.
"""


class Grant(Record):
    """A capability granted to an employee, optionally narrowed by scope."""

    grant_id: Identifier = Field(default_factory=lambda: new_id("grant"))
    employee_id: Identifier
    capability: Capability
    scope: str | None = None
    """Optional narrowing, e.g. a path prefix or repository name.

    ``None`` means the capability is granted unscoped, which should be rare
    below executive rank.
    """

    risk_override: RiskLevel | None = None
    """Raises or lowers the approval authority for this grant only."""

    justification: str | None = None
    granted_by: Identifier
    """Employee or human owner who issued the grant. Never self-issued."""

    @property
    def required_authority(self) -> RiskLevel:
        return self.risk_override or DEFAULT_RISK[self.capability]

    @model_validator(mode="after")
    def _lowered_risk_needs_justification(self) -> Grant:
        default = DEFAULT_RISK[self.capability]
        override = self.risk_override
        lowered = override is not None and _RISK_ORDER[override] < _RISK_ORDER[default]
        if lowered and not self.justification:
            assert override is not None  # narrowed by `lowered`
            raise ValueError(
                f"lowering required authority for {self.capability.value} from "
                f"{default.value} to {override.value} requires a justification"
            )
        if self.granted_by == self.employee_id:
            raise ValueError("a grant may not be self-issued")
        return self


_RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.ROUTINE: 0,
    RiskLevel.SUPERVISED: 1,
    RiskLevel.EXECUTIVE: 2,
    RiskLevel.HUMAN: 3,
}

MINIMUM_APPROVER_RANK: dict[RiskLevel, Rank | None] = {
    RiskLevel.ROUTINE: None,
    RiskLevel.SUPERVISED: Rank.MANAGER,
    RiskLevel.EXECUTIVE: Rank.EXECUTIVE,
    RiskLevel.HUMAN: None,
}
"""Minimum approver rank per risk level.

``ROUTINE`` needs no approver. ``HUMAN`` maps to ``None`` because no rank
satisfies it — only the human owner does.
"""
