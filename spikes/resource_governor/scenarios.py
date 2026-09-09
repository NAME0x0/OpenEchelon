"""Labelled scenarios for the Resource Governor spike.

Each scenario pairs a task with what each resource class would actually produce,
plus **ground truth**: whether that output is genuinely acceptable. Ground truth
is what makes false-accept and false-escalate measurable — without it, a cascade
that accepts everything looks free.

These are hand-written, deterministic, and deliberately small. They are a harness
for the estimator, not a benchmark of any model. Real numbers require running the
same harness against real providers with real labels; see the README.
"""

from __future__ import annotations

from dataclasses import dataclass

from openechelon.models.common import ReasoningLevel
from openechelon.models.task import Task


@dataclass(frozen=True)
class Outputs:
    """What each rung of the ladder produces for one scenario."""

    local_small: str
    local_large: str
    frontier_standard: str


@dataclass(frozen=True)
class Scenario:
    """A task, its outputs per rung, and which rungs are genuinely acceptable."""

    name: str
    task: Task
    outputs: Outputs
    acceptable: frozenset[str]
    """Resource-class values whose output a human reviewer would accept."""

    def is_acceptable(self, resource_class: str) -> bool:
        return resource_class in self.acceptable


def _task(task_class: str, expected_output: str, instruction: str) -> Task:
    return Task(
        objective="Spike scenario",
        instruction=instruction,
        expected_output=expected_output,
        task_class=task_class,
        created_by="emp_manager",
        required_reasoning=ReasoningLevel.NONE,
    )


EXTRACTION_CONTRACT = "- file\n- function\n- pattern"
CLASSIFY_CONTRACT = "- label\n- confidence"

SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        name="easy-extraction",
        task=_task(
            "structured_extraction",
            EXTRACTION_CONTRACT,
            "Extract the duplicated validation site",
        ),
        outputs=Outputs(
            local_small="file: auth.py\nfunction: validate\npattern: null check",
            local_large="file: auth.py\nfunction: validate\npattern: null check",
            frontier_standard="file: auth.py\nfunction: validate\npattern: null check",
        ),
        acceptable=frozenset({"local_small", "local_large", "frontier_standard"}),
    ),
    Scenario(
        name="small-model-drops-fields",
        task=_task(
            "structured_extraction",
            EXTRACTION_CONTRACT,
            "Extract every duplicated validation site",
        ),
        outputs=Outputs(
            local_small="file: auth.py",
            local_large="file: auth.py\nfunction: validate\npattern: null check",
            frontier_standard="file: auth.py\nfunction: validate\npattern: null check",
        ),
        acceptable=frozenset({"local_large", "frontier_standard"}),
    ),
    Scenario(
        name="small-model-refuses",
        task=_task(
            "structured_extraction",
            EXTRACTION_CONTRACT,
            "Extract the duplicated validation site from an ambiguous diff",
        ),
        outputs=Outputs(
            local_small="I cannot determine that from the provided context.",
            local_large="file: session.py\nfunction: check\npattern: repeated expiry test",
            frontier_standard="file: session.py\nfunction: check\npattern: repeated expiry test",
        ),
        acceptable=frozenset({"local_large", "frontier_standard"}),
    ),
    Scenario(
        name="structurally-complete-but-wrong",
        task=_task(
            "structured_extraction",
            EXTRACTION_CONTRACT,
            "Extract the duplicated validation site",
        ),
        outputs=Outputs(
            # Every required field present, all of it fabricated. This is the
            # adversarial case for a structural estimator, and the one that
            # produces a false accept.
            local_small="file: nowhere.py\nfunction: imaginary\npattern: invented",
            local_large="file: billing.py\nfunction: verify\npattern: duplicated currency check",
            frontier_standard=(
                "file: billing.py\nfunction: verify\npattern: duplicated currency check"
            ),
        ),
        acceptable=frozenset({"local_large", "frontier_standard"}),
    ),
    Scenario(
        name="truncated-cheap-answer",
        task=_task(
            "structured_extraction",
            EXTRACTION_CONTRACT,
            "Extract every duplicated validation site",
        ),
        outputs=Outputs(
            local_small="file: auth.py\nfunction: validate\npattern: null check ...",
            local_large="file: auth.py\nfunction: validate\npattern: null check",
            frontier_standard="file: auth.py\nfunction: validate\npattern: null check",
        ),
        acceptable=frozenset({"local_large", "frontier_standard"}),
    ),
    Scenario(
        name="easy-classification",
        task=_task("classification", CLASSIFY_CONTRACT, "Classify this failure report"),
        outputs=Outputs(
            local_small="label: tool_failure\nconfidence: 0.9",
            local_large="label: tool_failure\nconfidence: 0.9",
            frontier_standard="label: tool_failure\nconfidence: 0.9",
        ),
        acceptable=frozenset({"local_small", "local_large", "frontier_standard"}),
    ),
    Scenario(
        name="unsupported-task-class",
        task=_task(
            "open_ended_research",
            "A written assessment with sources",
            "Assess whether hierarchical agent organizations reduce cost",
        ),
        outputs=Outputs(
            local_small="Probably yes.",
            local_large="Likely, though the evidence is mixed.",
            frontier_standard=(
                "Mixed. Cascade routing shows large savings on matched distributions, "
                "but router quality degrades off-distribution."
            ),
        ),
        # Only the frontier answer is genuinely acceptable, and no estimator in
        # this spike has evidence for the class — so every rung should abstain.
        acceptable=frozenset({"frontier_standard"}),
    ),
)
