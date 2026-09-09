# 0001. Record architecture decisions

**Status:** Accepted
**Date:** 2026-09-09

## Context

OpenEchelon has an unusually complete statement of intent — forty principles in [`principles.md`](../principles.md) — and no implementation. That gap is about to close, and every choice made while closing it will be invisible six months later.

The principles are deliberately implementation-neutral. They say that models must be replaceable, not which SDK to use. They say reasoning is budgeted, not how a budget is represented. The decisions that fill those gaps are exactly the ones a future contributor will question, and the ones a future maintainer will be tempted to reverse without knowing why they were made.

Principle 36 requires that the project stay inspectable: a contributor should be able to reason about why a task was delegated, why a model was selected, and why resources were consumed. That obligation applies to the project's own construction, not only to its runtime.

## Decision

Record architecturally significant decisions as numbered Markdown files in `docs/adr/`, using the format described in [the index](README.md).

An ADR is required before merging any change that fixes a cross-component choice: language, storage engine, message encoding, provider adapter contract, concurrency model, or a departure from a stated principle.

An ADR is not required for choices that are local, obvious, or cheap to reverse.

## Consequences

Decisions gain a written rationale, so revisiting one starts from the original reasoning rather than from scratch.

Contributors get a place to argue with a decision that is not the pull request implementing it, which keeps design debate out of code review.

The cost is process. A one-page record before each significant choice is real friction, and it is only worth paying where reversal is expensive. Applying the rule too broadly would produce a directory of records nobody reads.

Records are numbered permanently and never renumbered. Superseding a record changes its status and adds a forward link; it does not delete it.

## Revisit if

The directory accumulates records nobody references, or the required-ADR rule is being satisfied with records written after the fact to unblock a merge. Either indicates the threshold is set too low.
