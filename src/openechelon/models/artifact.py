"""Artifacts and reviews.

Principle 18: important work does not exist only as chat text. An artifact has a
durable identity and a provenance chain. Principle 19: the agent that produced
work is not always the right one to certify it, so a review is a separate record
with its own author.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from openechelon.models.common import Identifier, Record, new_id


class ArtifactKind(StrEnum):
    SOURCE_CODE = "source_code"
    PATCH = "patch"
    REPORT = "report"
    RESEARCH = "research"
    DATASET = "dataset"
    SCREENSHOT = "screenshot"
    DIAGRAM = "diagram"
    TEST = "test"
    PLAN = "plan"
    DOCUMENT = "document"
    DECISION = "decision"
    BENCHMARK = "benchmark"
    LOG = "log"


class Artifact(Record):
    """A durable output with a traceable origin."""

    artifact_id: Identifier = Field(default_factory=lambda: new_id("art"))
    kind: ArtifactKind
    title: str = Field(min_length=1, max_length=200)
    produced_by: Identifier
    """Employee identity, never a model name. The model that executed the work
    is recorded on the execution record, which this artifact can reference."""

    task_id: Identifier
    execution_record_id: Identifier | None = None

    content_ref: str = Field(min_length=1)
    """Where the content lives: a path, URI, or content hash. The artifact
    record carries provenance; it is not the storage layer."""

    content_hash: str | None = None
    derived_from: list[Identifier] = Field(default_factory=list)
    """Artifacts this one was built from. Principle 25 requires the CEO's final
    answer to be traceable to source evidence, and this is the edge that makes
    that walk possible."""

    supersedes: Identifier | None = None

    @model_validator(mode="after")
    def _provenance_is_coherent(self) -> Artifact:
        if self.artifact_id in self.derived_from:
            raise ValueError("an artifact cannot be derived from itself")
        if self.supersedes == self.artifact_id:
            raise ValueError("an artifact cannot supersede itself")
        return self


class ReviewVerdict(StrEnum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_CORRECTIONS = "accepted_with_corrections"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class Review(Record):
    """An independent judgement on a task or artifact.

    ``independent`` is recorded rather than assumed. A review performed by the
    same employee, or on the same execution resource, that produced the work is
    still a review — it is simply worth less, and Principle 19 requires the
    difference to be visible rather than implied.
    """

    review_id: Identifier = Field(default_factory=lambda: new_id("rev"))
    task_id: Identifier
    artifact_ids: list[Identifier] = Field(default_factory=list)
    reviewer_id: Identifier
    reviewed_employee_id: Identifier
    verdict: ReviewVerdict
    rationale: str = Field(min_length=1)
    required_corrections: list[str] = Field(default_factory=list)

    independent_reviewer: bool
    """Reviewer is a different employee from the producer."""

    independent_resource: bool
    """Review ran on a different execution resource from the work.

    Principle 19 notes that provider diversity reduces correlated failure. A
    review by a different employee on the same model shares that model's blind
    spots."""

    @model_validator(mode="after")
    def _review_is_coherent(self) -> Review:
        if self.independent_reviewer and self.reviewer_id == self.reviewed_employee_id:
            raise ValueError("a review marked independent must have a different reviewer")
        if not self.independent_reviewer and self.reviewer_id != self.reviewed_employee_id:
            raise ValueError("a review by a different employee is independent by definition")
        if self.verdict is ReviewVerdict.REJECTED and not self.required_corrections:
            raise ValueError("a rejection must state what would need to change")
        return self
