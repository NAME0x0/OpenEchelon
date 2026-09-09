# OpenEchelon FAQ

Direct answers to the questions people ask about OpenEchelon. For the full architectural constraints, see [`principles.md`](principles.md).

---

## What is OpenEchelon?

OpenEchelon is an open-source, model-agnostic runtime for structured AI organizations. It models a hierarchy of AI agents — CEO, executives, directors, managers, specialists, and workers — where each agent has a defined role, manager, permissions, memory, reasoning budget, and reporting line. The human owner gives an objective to the CEO and retains final authority over everything the organization does.

The one-line definition:

> A model-agnostic runtime for structured AI organizations where persistent agents operate within hierarchy, authority, resource, memory, and information boundaries while reporting ultimately to a human owner.

---

## How is this different from a multi-agent swarm?

A swarm is flat: one lead agent fans work out to peer agents, usually sharing one context and one model. OpenEchelon is hierarchical, and the hierarchy carries operational meaning.

| | Flat multi-agent swarm | OpenEchelon |
|---|---|---|
| Structure | Lead plus peer agents | Multi-level organization with departments |
| Context | Often one shared context | Minimum sufficient context per role |
| Model choice | Usually one provider for all agents | Per-task assignment by a Resource Governor |
| Reasoning | Frequently maximized everywhere | Budgeted by rank and task requirement |
| Identity | Agent equals prompt plus model | Persistent employee with history and performance record |
| Scaling | More agents means more running models | Logical identity scales separately from execution |
| Escalation | Retry the same agent | Structured escalation to a stronger resource |
| Audit | Conversation history | Traceable task tree with artifacts and reviews |

The practical consequence: in a flat swarm, ten agents on one problem tends to mean ten expensive contexts reasoning about the same thing. In OpenEchelon, a worker gets a bounded assignment on a cheap model, and only the levels that need judgement pay for judgement.

---

## Is OpenEchelon usable today?

No. It is pre-alpha, in the architecture and prototyping stage. The repository currently contains the architectural principles, the intended design, and the roadmap. There is no runtime implementation and no released package.

---

## What can I actually do with the repository right now?

Read and critique the architecture. The most valuable contributions today are architectural critique of [`principles.md`](principles.md), prior-art analysis of existing agent frameworks, and concrete proposals for the core data models and protocols. See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Which models and providers does it support?

By design, no provider is mandatory. The intended execution surfaces include local inference (Ollama, llama.cpp, OpenAI-compatible servers), CLI coding agents (Codex CLI, Claude Code, Gemini and Antigravity CLI), hosted APIs, and external agent runtimes. Provider-specific behaviour lives behind adapters so the organizational runtime stays provider-independent.

---

## Does it require an internet connection or a cloud account?

No. OpenEchelon is designed to run meaningfully in a local-only configuration using local models, a local filesystem, local tools, and a local database. Frontier and cloud resources enhance capability but must not define the architecture. Local-first does not mean local-only.

---

## Does a thousand agents mean a thousand running models?

No, and this separation is a core constraint. A logical employee exists persistently without a dedicated model process, container, GPU allocation, or running session. A thousand registered employees might mean fifty assigned and twenty actively executing against a limited pool. One loaded local model can serve hundreds of logical workers over time.

---

## How does OpenEchelon decide which model runs a task?

A Resource Governor assigns execution resources per task. The default strategy is to start with the cheapest intelligence that could plausibly succeed and escalate when the attempt proves insufficient. Inputs include task complexity and importance, uncertainty and risk, remaining provider quota and reset windows, latency, local hardware availability, historical success rates, cost, concurrency, and the organizational rank of the requesting agent.

Reasoning level follows the same discipline: actual reasoning is the minimum of what the task requires and what the role permits. A director performing an obvious operation does not spend high reasoning simply because the role allows it.

---

## What stops an agent from doing something dangerous?

Several architectural constraints rather than a single guardrail prompt. Permissions are organizational and enforced technically where possible. Information access follows organizational need, so a worker does not receive the whole context. Sensitive external actions — sending messages, publishing, deleting data, financial transactions, production deployments — require an approval chain whose height depends on risk, up to human approval. Execution is interruptible: work can be paused, cancelled, or have its resource access revoked without waiting for an autonomous process to finish voluntarily. See [SECURITY.md](../SECURITY.md) for the threat model.

---

## Is this a workflow builder?

No. A visual workflow editor may eventually exist as an advanced feature, but it must never be required for normal operation. OpenEchelon is intended to construct execution plans dynamically from organizational structure, policy, objectives, and available resources. The user should not have to pre-wire every process.

---

## Is this a chatbot wrapper?

No. The default interface is a conversation with the CEO, but the substance is the organization behind it: persistent identities, delegation trees, permission boundaries, artifact provenance, independent review, and resource governance. The explicit non-goals rule out being another chatbot wrapper, a flat swarm, a mandatory workflow builder, or a wrapper around a single model company.

---

## Why hierarchy instead of letting agents self-organize?

Uncontrolled agent-to-agent communication graphs are hard to audit, hard to secure, and expensive. Hierarchy gives routing rules, permission boundaries, review chains, and — importantly — context compression. Managers turn raw worker output into higher-value summaries so an executive is not ingesting a hundred and fifty thousand tokens of raw work. Flat groups may still exist inside OpenEchelon; they are just not the primary model.

---

## What license is OpenEchelon under?

Apache License 2.0, including its explicit patent grant. See [LICENSE](../LICENSE).

---

## How does it relate to MCP, ACP, OpenHands, and similar projects?

As ecosystems to coordinate rather than replace. External agent frameworks and protocol servers may act as employee runtimes, tool providers, department services, external specialists, or execution backends. The distinct value of OpenEchelon is organizational orchestration, so rebuilding a mature surrounding ecosystem would be wasted effort.

---

## When will there be a working release?

There is no date. Phase 0 covers the organizational data model, agent identity model, hierarchical permissions, task and delegation graph, message protocol, provider abstraction, Resource Governor, artifact model, and security boundaries. Phase 1 is a minimum viable organization: one CEO, three managers, a small worker pool, local execution plus CLI agent integrations, a delegation and review loop, and quota-aware routing. Watch the repository or follow the [changelog](../CHANGELOG.md).
