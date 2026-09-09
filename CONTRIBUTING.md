# Contributing to OpenEchelon

Thanks for your interest in OpenEchelon — a model-agnostic runtime for structured AI organizations.

OpenEchelon is in the **architecture and prototyping stage**. There is no runtime implementation yet. That shapes what is useful to contribute right now.

---

## What is most useful today

| Contribution | Status |
|---|---|
| Architectural critique of [`docs/principles.md`](docs/principles.md) | **Most valuable** |
| Prior-art analysis of existing agent frameworks | **Most valuable** |
| Concrete data-model or protocol proposals (org model, task graph, message schema) | Welcome |
| Benchmarks and failure analyses of hierarchical vs. flat agent systems | Welcome |
| Provider/runtime adapter designs (Ollama, MCP, CLI harnesses) | Welcome |
| Documentation fixes, typos, broken links | Always welcome |
| Large speculative feature implementations | **Not yet** — the core model is not frozen |

If you want to build something substantial, **open a discussion or issue first**. Implementation ahead of an agreed data model will likely be rejected, and that wastes your time.

---

## The bar every change must clear

OpenEchelon has a set of immutable principles in [`docs/principles.md`](docs/principles.md). They are architectural constraints, not feature preferences. Before proposing a change, check it against the Architectural Test at the end of that document:

- Does this preserve human authority?
- Does this preserve separation between agent identity and model execution?
- Does this support hierarchy rather than forcing flat coordination?
- Does this allow cheap work to remain cheap?
- Does this avoid unnecessary context sharing?
- Does this remain observable and auditable?
- Does this preserve provider independence?
- Does this support resource governance?
- Does this scale logical identity separately from active execution?
- Does this reduce rather than increase coordination burden on the user?

A "no" is not automatically a rejection, but it requires strong justification in the pull request description.

Changes to `docs/principles.md` itself are held to a higher standard. Principles are meant to be stable across language, framework, and provider changes. Propose principle changes as a discussion, not a drive-by pull request.

---

## Workflow

1. **Search first.** Check open issues and discussions before filing.
2. **Open an issue or discussion** describing the problem or proposal. For anything beyond a typo, agreement on the problem should precede a pull request.
3. **Fork and branch.** Use a descriptive branch name: `docs/message-protocol`, `proposal/resource-governor`, `fix/broken-links`.
4. **Keep pull requests focused.** One concern per pull request. A 40-file pull request that mixes docs, formatting, and architecture will be asked to split.
5. **Write commit messages that explain why**, not just what. [Conventional Commits](https://www.conventionalcommits.org/) format is preferred:

   ```text
   docs(principles): clarify reasoning-budget formula
   feat(governor): add quota-window tracking
   fix(links): correct MCP specification URL
   ```

6. **Open the pull request** against `main`, fill in the template, and link the issue it resolves.

---

## Style

- **Markdown** is the primary format today. Line-wrap naturally; do not hard-wrap at 80 columns.
- **ASCII diagrams** are used deliberately throughout the docs — they render everywhere, diff cleanly, and stay readable in a terminal. Prefer them over image assets.
- **Plain, precise language.** No marketing tone. State what the system does and does not do.
- **`.editorconfig`** in the repository root defines whitespace conventions. Most editors apply it automatically.

Once a runtime language is selected, language-specific standards, linting, and test requirements will be added here.

---

## Licensing and provenance

OpenEchelon is licensed under the [Apache License 2.0](LICENSE). By submitting a contribution you agree that it is licensed under the same terms, and that you have the right to submit it.

**Do not copy code from other projects into this repository.** OpenEchelon studies the wider agent ecosystem (see the Inspiration section of the [README](README.md)), and those projects carry different licenses. Learning from an architecture is fine. Copying source without a license review is not. If a contribution derives from another project, say so explicitly in the pull request, and name the source and its license.

---

## Code of Conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Do not report vulnerabilities in public issues. See [SECURITY.md](SECURITY.md).
