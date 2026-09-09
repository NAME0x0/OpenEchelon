# 0002. Implementation stack: Python

**Status:** Accepted
**Date:** 2026-09-09

## Context

Phase 0 cannot start without a language. The choice constrains which provider integrations are cheap, which contributors can participate, and how the organizational data model is expressed.

The decision is bounded by principles that already exist. Principle 11 requires that models and providers be replaceable, so provider-specific behaviour must sit behind adapters regardless of language. Principle 39 requires meaningful local-only operation, which means local inference must be a first-class path, not an afterthought. Principle 37 prefers integrating mature ecosystems over rebuilding them, which makes ecosystem depth a primary criterion rather than a convenience.

Three candidates were considered seriously.

**Python.** The agent and inference ecosystem is Python-first: provider SDKs, MCP server and client libraries, local inference clients, evaluation and routing research code, and the tracing and observability tooling the auditability principles demand. Contributors working on multi-agent systems are overwhelmingly working in Python. Its weaknesses are real — packaging has been historically painful, and concurrency at high fan-out requires care.

**TypeScript.** Better suited to the eventual executive-chat interface, and several coding harnesses OpenEchelon intends to employ ship as Node CLIs. Weaker for local inference, evaluation tooling, and the research code the Resource Governor will need to borrow from. Choosing it would mean reimplementing routing and evaluation work that already exists in Python.

**Rust.** Correct long-term choice for a high-concurrency execution pool, and appealing for a system that manages resources. Wrong choice now: it would spend the project's scarcest resource — maintainer time at pre-alpha — on ecosystem gaps rather than on the organizational model, and would shrink the contributor pool at exactly the stage the project needs critique and prototypes.

## Decision

Implement OpenEchelon in **Python 3.12 or newer**.

Supporting choices, all reversible and none binding on the architecture:

- **Pydantic v2** for the organizational data model. The Phase 0 records are validated, serializable, versioned documents; Pydantic gives schema validation and JSON Schema export without inventing a format.
- **SQLite** as the default persistence engine. Principle 39 requires useful local-only operation, and SQLite requires no service. The storage layer sits behind a repository interface so a server database can replace it without touching the organizational model.
- **uv** for dependency and environment management.
- **pytest** for tests, **ruff** for linting and formatting, **mypy** in strict mode for the core packages.

Language choice binds the runtime only. Nothing prevents an employee from being executed by a CLI agent, a service, or a process written in any language — that is the point of Principle 4.

## Consequences

Provider integrations, MCP support, local inference, and evaluation tooling are available rather than built. The routing and quality-estimation literature that ADR [0003](0003-quality-estimation-is-the-load-bearing-component.md) depends on is directly usable.

The contributor pool matches the domain, which matters more at pre-alpha than raw runtime performance.

The cost arrives later. Python's concurrency model will constrain the execution pool once many employees run simultaneously, and Principle 32 already anticipates that concurrency must be explicitly governed rather than maximized. The mitigation is architectural, not linguistic: the execution pool sits behind an interface, and a hot path can be replaced by a service in another language without the organizational model noticing.

Static typing is enforced from the start because the organizational model is the product. Loosely typed records here would undermine the auditability the project claims.

## Revisit if

The execution pool becomes the measured bottleneck under realistic concurrency, or a provider ecosystem OpenEchelon depends on becomes unavailable in Python. Neither would require a rewrite — both are answered by replacing one component behind its interface.
