"""Escalation policy.

The policy — not the estimator — owns the accept threshold. That separation is
what lets one calibrated estimator serve task classes with very different
tolerances for a wrong answer.

Thresholds are asymmetric by default, because the two failure directions are not
equally expensive:

    false escalate  -> money wasted, answer still correct
    false accept    -> wrong answer ships, and the review chain never looks

Principle 19 makes the second worse than it first appears: an accepted answer is
one nothing downstream has been told to check.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from openechelon.governor.estimator import Verdict
from openechelon.models.permissions import RiskLevel

DEFAULT_THRESHOLD = 0.75
"""Accept only at high confidence. Deliberately above 0.5.

An even split would treat the two failure directions as equally costly, which
they are not.
"""

RISK_THRESHOLD: dict[RiskLevel, float] = {
    RiskLevel.ROUTINE: 0.70,
    RiskLevel.SUPERVISED: 0.80,
    RiskLevel.EXECUTIVE: 0.90,
    RiskLevel.HUMAN: 1.0,
}
"""Threshold by the risk of the action the answer will inform.

``HUMAN`` maps to 1.0: no estimator score authorizes accepting an answer that
will drive an irreversible external action. Principle 23 sends that to a person.
"""


class EscalationPolicy(BaseModel):
    """How estimator scores become accept-or-escalate decisions."""

    model_config = ConfigDict(extra="forbid")

    default_threshold: float = Field(default=DEFAULT_THRESHOLD, ge=0.0, le=1.0)
    per_task_class: dict[str, float] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.ROUTINE

    abstention_escalates: bool = True
    """ADR 0003. Turning this off means accepting answers no estimator was
    willing to judge, which is the false-accept path with extra steps."""

    max_attempts: int = Field(default=3, ge=1)
    """Cap on ladder rungs per task. Principle 20: retries are deliberate and
    bounded, not a loop."""

    def threshold_for(self, task_class: str) -> float:
        """Threshold for a task class: the stricter of class and risk setting."""
        class_threshold = self.per_task_class.get(task_class, self.default_threshold)
        return max(class_threshold, RISK_THRESHOLD[self.risk_level])

    def accepts(self, verdict: Verdict, task_class: str) -> bool:
        if verdict.score is None:
            return not self.abstention_escalates
        return verdict.score >= self.threshold_for(task_class)

    @model_validator(mode="after")
    def _thresholds_in_range(self) -> EscalationPolicy:
        for task_class, threshold in self.per_task_class.items():
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"threshold for {task_class!r} out of range: {threshold}")
        return self
