# Phase 0 — the organizational data model

Phase 0 in the [roadmap](../../README.md#roadmap) listed nine nouns. Nouns have no definition of done, so this document restates them as deliverables with acceptance criteria, and records what is built.

The model lives in [`src/openechelon/models`](../../src/openechelon/models). It defines what the organization *is*. It contains no orchestration logic — deciding what happens next is the Resource Governor's job, and keeping the two apart is what lets the model be validated without running anything.

## Status

| Deliverable | Record | State |
|---|---|---|
| Organizational data model | `Department`, `Employee` | Built |
| Agent identity model | `Employee`, `PerformanceRecord` | Built |
| Hierarchical permissions | `Grant`, `Capability`, `RiskLevel` | Built |
| Task and delegation graph | `Task`, `Assignment`, `Failure` | Built |
| Structured agent-message protocol | `Message`, `MessageType`, `RoutePath` | Built |
| Provider/runtime abstraction | `ExecutionResource`, `Quota`, `RuntimeKind` | Built |
| Resource Governor | `CascadeGovernor`, `EscalationPolicy` | Spike — see [ADR 0003](../adr/0003-quality-estimation-is-the-load-bearing-component.md) |
| Artifact model | `Artifact`, `Review` | Built |
| Security boundaries | `Grant`, `RiskLevel`, `MINIMUM_APPROVER_RANK` | Partial — policy is modelled, enforcement is not |

"Built" means the record exists, its invariants are enforced by validators, and those validators are covered by tests naming the principle they protect. It does not mean a runtime uses them yet.

## Acceptance criteria

A Phase 0 record is complete when all five hold.

1. **It is traceable to a principle.** Every record maps to at least one entry in [`principles.md`](../principles.md). A field nothing requires is scope creep.
2. **Its invariants are enforced, not documented.** A rule stated in a docstring and not checked by a validator is a comment. The CEO having no manager, a grant not being self-issued, a review claiming independence — all are validator-enforced.
3. **It is tested against the principle, not the implementation.** Each test says which principle would break if the invariant failed.
4. **It survives round-tripping.** Records serialize to JSON and back without loss, and carry the schema version they were written under.
5. **It names no provider.** `ExecutionResource` is the sole exception, and Principle 11 is why: provider specifics live behind adapters, so removing a provider from a deployment invalidates no employee, task, or artifact.

## Design decisions worth knowing

**Reasoning ceilings are ceilings.** `RoutingDecision` refuses to validate when requested reasoning exceeds the role ceiling and the decision is not marked escalated. This is the corrected form of Principle 7 — the original `min()` formula silently capped reasoning below what a task needed, converting a resource limit into a wrong answer. The rule is now enforced in two places: the record refuses to describe an under-powered run, and `CascadeGovernor.run` escalates before invoking any resource.

**Outcomes may only be recorded from verification.** `RoutingDecision.outcome` defaults to `PENDING` and cannot be set to a real outcome without a review reference. Principle 26 wants the organization to learn which resources work; an assumed outcome would teach it noise, and a system that scores its own guesses as correct converges on confident nonsense.

**Acceptance rate is `None`, not zero, without evidence.** `PerformanceRecord.acceptance_rate` returns `None` for an employee with no assignments. A fabricated zero would look like poor performance and route work away from an employee nobody has tried.

**Review independence is recorded on two axes.** Whether the reviewer is a different employee, *and* whether the review ran on a different execution resource. Principle 19 notes that provider diversity reduces correlated failure — a different employee reviewing on the same model shares that model's blind spots, and the model should be able to say so.

**Cancellation is reachable from every non-terminal state.** Principle 31 requires that a human owner never wait for an autonomous process to voluntarily finish. That is asserted by a test that walks the transition table rather than by convention.

**Local inference is private by construction.** A resource declaring `LOCAL_INFERENCE` must set `private=True` or fail validation. Privacy is a routing input — some task classes should not leave local hardware — and an unmarked local resource would silently drop out of that filter.

## What Phase 0 does not include

No storage engine, no runtime, no scheduler, no organization loop. ADR [0002](../adr/0002-implementation-stack.md) names SQLite as the intended default, but the model deliberately does not depend on it: records sit behind a repository interface that does not exist yet, because writing persistence before the shape is settled means migrating twice.

No enforcement of the permission model either. `Grant` and `RiskLevel` describe what authority an action needs; nothing yet refuses to execute without it. Principle 35 says security is architectural, and the architecture is now written down — but a modelled boundary is not an enforced one, and the table above says "partial" for that reason.

## Next

The Resource Governor spike ([`spikes/resource_governor`](../../spikes/resource_governor)) is the sequenced next step, and ADR 0003 explains why it comes before the organization runtime rather than after it.
