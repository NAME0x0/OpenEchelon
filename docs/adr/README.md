# Architecture Decision Records

An ADR records a decision that was expensive to make and would be expensive to reverse: why it was taken, what was rejected, and what would justify revisiting it.

OpenEchelon keeps ADRs because [`principles.md`](../principles.md) states what the system fundamentally is, but not why any particular implementation choice was made. Principles are meant to outlive languages and frameworks. ADRs record the choices the principles deliberately left open.

## Index

| # | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-implementation-stack.md) | Implementation stack: Python | Accepted |
| [0003](0003-quality-estimation-is-the-load-bearing-component.md) | Quality estimation is the load-bearing component | Accepted |

## When to write one

Write an ADR when a decision:

- constrains later work across more than one component,
- would be costly to reverse once code depends on it,
- has a credible alternative someone will otherwise re-propose, or
- was made for a reason not visible in the resulting code.

Do not write one for choices that are obvious, local, or cheap to change.

## Format

Each record uses the same five sections: Status, Context, Decision, Consequences, and Revisit if. Keep them short. An ADR that needs a table of contents is describing more than one decision.

Records are numbered sequentially and never renumbered. A superseded record stays in place with its status changed and a link forward, because the reasoning that produced a wrong decision is often more useful than the decision itself.
