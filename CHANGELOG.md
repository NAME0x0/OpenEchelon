# Changelog

All notable changes to OpenEchelon are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a version is released.

> OpenEchelon is pre-alpha. No version has been released, and no public interface is stable. Everything below describes the design record, not shipped software.

## [Unreleased]

### Added

- Phase 0 organizational data model in `src/openechelon/models`: employees and departments, capability grants with risk-graded approval authority, tasks with an explicit state machine and delegation tree, typed message envelope with authority-path routing, artifacts with provenance, reviews recording independence on two axes, execution resources with quota and reset windows, and execution/routing records. Invariants are enforced by validators and covered by tests naming the principle each protects.
- Resource Governor spike in `src/openechelon/governor` and `spikes/resource_governor`: cheapest-first escalation ladder, sufficiency estimators that abstain outside their evidence, and an escalation policy with asymmetric thresholds. Measured 85.7% cost reduction against a frontier-always baseline on labelled scenarios, with one false accept that a structural estimator cannot avoid.
- Architecture decision records: ADR 0001 (record decisions), ADR 0002 (Python 3.12+ implementation stack), ADR 0003 (quality estimation is the load-bearing component).
- `docs/architecture/phase-0.md` restating Phase 0 as deliverables with acceptance criteria.
- Python CI: ruff lint and format, mypy strict, pytest on 3.12 and 3.13, plus a job that prints the spike figures into the run log.
- Project site under `site/`, deployed to GitHub Pages, with structured data for search and generative engines.

### Fixed

- Principle 7 defined `actual_reasoning = min(required_by_task, allowed_by_role)`, which silently capped reasoning below what a task needed and contradicted the escalation contract in Principle 20. A shortfall against the role ceiling is now an escalation condition, enforced in `CascadeGovernor.run` and by a validator on `RoutingDecision`.
- Removed the unexplained "CEO / AVA" label from the README architecture diagram.

### Added in repository setup

- Apache License 2.0 and NOTICE file.
- Contribution guide, Code of Conduct, and security policy with an agent-runtime threat model.
- Issue templates for architecture proposals, prior-art reports, documentation issues, and bugs; pull request template carrying the Architectural Test.
- Documentation CI: markdown lint, link check, and a required-files metadata check.
- `CITATION.cff`, `llms.txt`, and repository metadata (description, topics) for discovery by search engines and language models.
- `docs/faq.md` answering what OpenEchelon is and how it differs from flat multi-agent frameworks.
- Immutable architectural principles in `docs/principles.md` — 40 principles, non-goals, and an Architectural Test for evaluating future design decisions.
- Project README describing the organizational model, intelligence ladder, resource governance, and phased roadmap.

[Unreleased]: https://github.com/NAME0x0/OpenEchelon/commits/main
