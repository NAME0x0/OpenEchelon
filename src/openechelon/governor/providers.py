"""Execution provider adapters.

Principle 11: provider-specific behaviour sits behind an adapter and nowhere
else. The Governor talks to this interface only, so a deployment with no network
access and a deployment using three frontier APIs run the same code path.

Only the scripted adapter ships here. It exists so the Governor can be evaluated
deterministically and offline — a real adapter cannot be used to measure an
estimator's false-accept rate, because you would be measuring the model's mood
alongside the estimator.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Protocol, runtime_checkable

from openechelon.governor.estimator import Response
from openechelon.models.common import ReasoningLevel
from openechelon.models.resource import ExecutionResource
from openechelon.models.task import Task


@runtime_checkable
class ExecutionProvider(Protocol):
    """Executes one task on one resource at one reasoning level."""

    def execute(
        self,
        resource: ExecutionResource,
        task: Task,
        reasoning: ReasoningLevel,
    ) -> Response: ...


ResponseFactory = Callable[[ExecutionResource, Task, ReasoningLevel], Response]


class ScriptedProvider:
    """Deterministic provider for evaluation and tests.

    Responses are supplied per resource class, so a scenario can express
    'the small local model drops two fields, the frontier model gets it right'
    without invoking anything.
    """

    def __init__(self, responses: Mapping[str, ResponseFactory]) -> None:
        self._responses = dict(responses)
        self.calls: list[tuple[str, str, ReasoningLevel]] = []

    def execute(
        self,
        resource: ExecutionResource,
        task: Task,
        reasoning: ReasoningLevel,
    ) -> Response:
        self.calls.append((resource.resource_id, task.task_id, reasoning))
        factory = self._responses.get(resource.resource_class.value)
        if factory is None:
            raise KeyError(
                f"no scripted response for resource class {resource.resource_class.value!r}"
            )
        return factory(resource, task, reasoning)


def fixed_response(
    text: str, *, input_tokens: int = 400, output_tokens: int = 120
) -> ResponseFactory:
    """Convenience factory for a constant response."""

    def factory(
        resource: ExecutionResource,
        task: Task,
        reasoning: ReasoningLevel,
    ) -> Response:
        return Response(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=50,
        )

    return factory
