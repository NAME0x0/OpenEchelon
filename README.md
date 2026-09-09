# OpenEchelon

> **The operating system for AI organizations.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Status: pre-alpha](https://img.shields.io/badge/status-pre--alpha-orange.svg)](#roadmap)
[![Docs CI](https://github.com/NAME0x0/OpenEchelon/actions/workflows/docs.yml/badge.svg)](https://github.com/NAME0x0/OpenEchelon/actions/workflows/docs.yml)
[![Discussions](https://img.shields.io/badge/discussions-open-brightgreen.svg)](https://github.com/NAME0x0/OpenEchelon/discussions)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**[openechelon site &rarr;](https://name0x0.github.io/OpenEchelon/)**

**OpenEchelon is a model-agnostic runtime for structured AI organizations** — hierarchical multi-agent systems where persistent AI employees operate within defined authority, permission, memory, and resource boundaries, and report ultimately to a human owner.

It is an open-source project for building and running structured organizations of AI agents.

Instead of placing a handful of agents in a shared chat and calling it a swarm, OpenEchelon models an actual organization: executives, directors, managers, specialists, and workers — each with defined responsibilities, authority, tools, memory, budgets, and reporting lines.

**You communicate with the CEO. The organization handles the rest.**

> **Status:** Pre-alpha. OpenEchelon is currently in the architecture and prototyping stage.

---

## Contents

- [The Idea](#the-idea) — why hierarchy instead of a swarm
- [AI Organization, Not AI Swarm](#ai-organization-not-ai-swarm) — structure and responsibilities per level
- [Agents Are Not Models](#agents-are-not-models) — identity separated from execution
- [The Intelligence Ladder](#the-intelligence-ladder) — cheapest sufficient intelligence
- [Resource and Quota Governance](#resource-and-quota-governance) — treating frontier models as scarce
- [Organizational Context Compression](#organizational-context-compression) — managers as compressors
- [Structured Communication](#structured-communication) — typed messages, not group chat
- [Planned Architecture](#planned-architecture) and [Roadmap](#roadmap)
- [Project State](#project-state) — what is built, what is not
- [Frequently Asked Questions](#frequently-asked-questions) — and the full [FAQ](docs/faq.md), including how this compares to flat agent frameworks
- [Immutable Principles](docs/principles.md) — the 40 architectural constraints that govern the design
- [Decision Records](docs/adr) · [Phase 0](docs/architecture/phase-0.md) · [Governor spike](spikes/resource_governor)
- [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Changelog](CHANGELOG.md)

---

## The Idea

Most multi-agent systems expose their complexity directly to the user.

You choose agents, wire workflows, select models, coordinate handoffs, manage prompts, and decide which agent should do what.

OpenEchelon takes a different approach.

```text
                         YOU
                          |
                          v
                         CEO
                          |
            +-------------+-------------+
            |             |             |
            v             v             v
           CTO           CRO           CQO
            |             |             |
            v             v             v
        Directors     Directors     Directors
            |             |             |
            v             v             v
        Managers      Managers      Managers
            |             |             |
            v             v             v
       Specialists   Specialists   Specialists
            |             |             |
            v             v             v
         Workers       Workers       Workers
```

The user should not need to manage the workforce.

The CEO receives the objective, delegates through the organization, monitors progress, resolves conflicts, commissions reviews, manages scarce model resources, and returns the consolidated result.

---

## AI Organization, Not AI Swarm

A typical agent swarm is relatively flat:

```text
             Lead
              |
       +------+------+ 
       |      |      |
     Agent  Agent  Agent
```

OpenEchelon is hierarchical.

Different levels have different responsibilities, permissions, information access, reasoning budgets, and model capabilities.

```text
+----------------------------------------------------------------+
|                            YOU                                 |
+------------------------------+---------------------------------+
                               |
                               v
+----------------------------------------------------------------+
|                            CEO                                 |
+------------------------------+---------------------------------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
         Technology        Research         Quality
         Executive         Executive        Executive
              |                |                |
              v                v                v
          Directors        Directors        Directors
              |                |                |
              v                v                v
           Managers         Managers         Managers
              |                |                |
              v                v                v
           Workers          Workers          Workers
```

Workers execute.

Managers think, delegate, inspect, and compress information.

Directors coordinate multiple teams.

Executives resolve strategic trade-offs.

The CEO communicates with the user.

---

## Agents Are Not Models

OpenEchelon separates an agent's **identity** from the model used to execute its work.

An employee is not a "Claude agent," "Gemini agent," or "Codex agent."

An employee has:

- a role
- a department
- a manager
- responsibilities
- skills
- permissions
- memory
- assignments
- a reasoning ceiling
- a resource budget
- an escalation authority
- a performance history

The execution engine is assigned separately.

```text
                       EMPLOYEE
                          |
                          v
                         TASK
                          |
                          v
                 RESOURCE GOVERNOR
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
        LOCAL          FRONTIER         TOOLS
          |               |               |
       Ollama          Codex CLI        Browser
       Qwen            Claude Code      Shell
                       Gemini / AGY      Files
                       APIs              Git
                                         MCP
```

This allows the same logical employee to use different resources depending on the task.

---

## The Intelligence Ladder

OpenEchelon is designed around a simple principle:

> **Use the cheapest intelligence capable of completing the task well.**

A possible organizational policy:

| Level | Reasoning | Typical Execution |
|---|---|---|
| Worker | None | Small local model |
| Specialist | None / Low | Local or inexpensive model |
| Manager | Low / Medium | Stronger local or frontier model |
| Director | Medium / High | Frontier model |
| Executive | High | High-quality frontier model |
| CEO | Highest justified | Best available synthesis model |

These are **ceilings, not targets**. A task needing less reasoning than its role permits runs at what the task needs. A task needing *more* than its role permits escalates to a role whose allowance covers it — it is never run under-powered, because a resource limit silently converted into a wrong answer costs more than the reasoning it saved. See [Principle 7](docs/principles.md#7-reasoning-is-a-budgeted-organizational-resource).

Workers should generally **execute**, not reconsider the entire strategy.

A manager might send a worker:

```text
TASK:
Inspect these files for duplicated validation logic.

OUTPUT:
Return the file names, functions, and duplicated patterns.

DO NOT:
Redesign the application.
Modify unrelated files.
Perform architectural analysis.
```

The manager has already decided what needs doing.

This reduces unnecessary reasoning, context, latency, and token consumption.

---

## Resource and Quota Governance

Frontier intelligence is scarce.

Codex, Claude, Gemini, APIs, subscription sessions, GPU memory, context windows, and concurrent processes all have limits.

OpenEchelon treats them as organizational resources.

The Resource Governor is intended to consider:

- task complexity
- task importance
- uncertainty
- risk
- required capabilities
- remaining provider quota
- quota reset windows
- model latency
- reasoning requirements
- local hardware availability
- historical success rates
- cost
- concurrency
- organizational rank

A routine task should not consume an executive-grade model simply because one is available.

```text
Simple task
    |
    v
Local worker
    |
    +---- success ----> complete
    |
    +---- failure
             |
             v
         Specialist
             |
             +---- success ----> complete
             |
             +---- failure
                      |
                      v
                   Manager
                      |
                      v
                Frontier model
```

Escalation happens when required.

---

## 1,000 Agents Does Not Mean 1,000 Running Models

OpenEchelon is intended to eventually support large logical organizations.

That does **not** mean keeping every employee active simultaneously.

```text
1,000 registered employees
             |
             v
      47 assigned to work
             |
             v
       21 currently active
             |
       +-----+-----+
       |           |
       v           v
   Local pool   Frontier pool
```

Agent identities persist independently of execution processes.

A single loaded local model could serve hundreds of logical workers over time.

Codex, Claude, Gemini, browsers, terminals, and sandboxes can similarly operate as pooled resources.

---

## Organizational Context Compression

Not every employee should know everything.

Workers receive the information required for their assignment.

Managers receive reports from workers.

Directors receive consolidated reports from managers.

Executives receive strategic summaries.

The CEO receives the smallest high-value representation needed to make the final decision.

```text
30 Workers
    |
    v
6 Managers
    |
    v
3 Directors
    |
    v
1 Executive
    |
    v
CEO
    |
    v
You
```

This provides both **information compartmentalization** and **context compression**.

The CEO should not need to ingest hundreds of thousands of tokens of raw worker output.

---

## Structured Communication

OpenEchelon agents should not behave like members of one enormous group chat.

Communication can have explicit organizational meaning:

```text
TASK
REPORT
QUESTION
ANSWER
REVIEW
REJECTION
APPROVAL
ESCALATION
ARTIFACT
RESEARCH_REQUEST
IMPLEMENTATION_REQUEST
VERIFICATION_REQUEST
```

Communication follows reporting relationships by default.

```text
Worker
  |
Manager
  |
Director
  |
Executive
  |
CEO
  |
User
```

Cross-team communication can be routed through management or explicitly authorized when direct collaboration is useful.

---

## Example

You ask:

> Build and evaluate a new memory architecture.

The organization may create:

```text
                            CEO
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
      Research           Technology          Quality
      Executive          Executive           Executive
          |                  |                  |
          v                  v                  v
      Research           Engineering        Review
      Manager            Manager            Manager
          |                  |                  |
      +---+---+          +---+---+          +---+---+
      |       |          |       |          |       |
    Local    AGY       Local   Codex      Local   Claude
   Workers Research   Workers Engineer    Tests  Reviewer
```

AGY can gather current information.

Codex can implement prototypes.

Claude can challenge the implementation and inspect quality.

Local models can perform routine extraction, classification, testing, summarization, and tool work.

Managers combine their outputs.

Executives resolve disagreements.

The CEO produces the final response.

---

## Design Principles

### 1. Executive Simplicity

The default interface should feel like talking to one capable executive.

No workflow editor should be required for normal use.

### 2. Local First

Routine work should be able to execute locally with models such as those served through Ollama or llama.cpp.

### 3. Model Agnostic

No employee should permanently belong to one model provider.

### 4. Harness Agnostic

CLI agents, APIs, local models, and external agent runtimes should all be valid execution resources.

### 5. Hierarchical Intelligence

Greater responsibility may justify stronger models, more context, and more reasoning.

### 6. Scarcity Aware

Compute, quota, context, money, and time are resources to manage deliberately.

### 7. Compartmentalized

Agents receive the context and permissions necessary for their role — not unrestricted access to the entire organization.

### 8. Observable

Tasks, delegation, reports, artifacts, reviews, failures, model usage, and escalation paths should be inspectable.

### 9. Interoperable

OpenEchelon should integrate with existing ecosystems rather than require users to abandon them.

### 10. Human Authority

The organization ultimately reports to its human owner.

---

## Intended Execution Ecosystem

OpenEchelon is being designed to eventually support multiple execution surfaces.

### Local inference

- Ollama
- llama.cpp
- OpenAI-compatible local servers

### Agent and coding harnesses

- Codex CLI
- Claude Code
- Gemini / Antigravity CLI
- other compatible CLI agents

### Interoperability

- MCP
- ACP
- OpenClaw
- external agent runtimes
- plugins and skills

### Tools

- browser
- terminal
- filesystem
- Git
- isolated sandboxes
- scheduled jobs
- external services
- connectors

No single model provider should be mandatory.

---

## Planned Architecture

```text
+==================================================================+
|                       USER INTERFACE                             |
|                                                                  |
|                 CEO conversation + oversight                     |
+==============================+===================================+
                               |
                               v
+==================================================================+
|                     ORGANIZATION ENGINE                          |
|                                                                  |
| Hierarchy        Delegation        Departments                   |
| Task Graph       Messaging         Reviews                       |
| Permissions      Escalation        Organizational Memory         |
+==============================+===================================+
                               |
                               v
+==================================================================+
|                     RESOURCE GOVERNOR                            |
|                                                                  |
| Model Routing    Quotas          Reasoning Budgets               |
| Cost Control     Concurrency     Performance History             |
+==============================+===================================+
                               |
             +-----------------+-----------------+
             |                                   |
             v                                   v
+----------------------------+      +----------------------------+
|       EXECUTION POOL       |      |         TOOL POOL          |
|                            |      |                            |
| Local models               |      | Browser                    |
| Codex CLI                  |      | Shell                      |
| Claude Code                |      | Filesystem                 |
| Gemini / AGY               |      | Git                        |
| API providers              |      | MCP / connectors           |
+----------------------------+      +----------------------------+
             |                                   |
             +-----------------+-----------------+
                               |
                               v
+==================================================================+
|                       ARTIFACT STORE                             |
|                                                                  |
| Code   Research   Reports   Tests   Evidence   Decisions   Files |
+==================================================================+
```

---

## Roadmap

### Phase 0 — Architecture

Acceptance criteria and design notes: [`docs/architecture/phase-0.md`](docs/architecture/phase-0.md).

- [x] Organizational data model
- [x] Agent identity model
- [x] Hierarchical permissions — modelled; enforcement is Phase 1
- [x] Task and delegation graph
- [x] Structured agent-message protocol
- [x] Provider/runtime abstraction
- [ ] Resource Governor — [spike measured](spikes/resource_governor); needs real-provider validation
- [x] Artifact model
- [ ] Security boundaries — policy modelled, technical enforcement not started

### Phase 1 — Minimum Viable Organization

- [ ] One CEO
- [ ] Three managers
- [ ] Small worker pool
- [ ] Local worker execution
- [ ] Codex CLI integration
- [ ] Claude Code integration
- [ ] Gemini / Antigravity integration
- [ ] Delegation and reporting
- [ ] Review loop
- [ ] Basic quota-aware routing
- [ ] Executive chat interface

### Phase 2 — Organization Runtime

- [ ] Departments
- [ ] Directors and executives
- [ ] Dynamic hiring
- [ ] Persistent organizational memory
- [ ] Task dependencies
- [ ] Shared and private workspaces
- [ ] Sandboxed computers
- [ ] Scheduled work
- [ ] Approval workflows
- [ ] Model escalation policies
- [ ] Performance tracking

### Phase 3 — Ecosystem

- [ ] MCP
- [ ] ACP
- [ ] OpenClaw interoperability
- [ ] Remote workers
- [ ] Distributed execution
- [ ] External agent runtimes
- [ ] Plugin / skill ecosystem
- [ ] Notification and mobile surfaces

### Phase 4 — Large Organizations

- [ ] Hundreds to thousands of logical employees
- [ ] Dynamic staffing
- [ ] Learned model routing
- [ ] Automated resource economics
- [ ] Performance-based role assignment
- [ ] Organizational restructuring
- [ ] Long-running autonomous departments

---

## Inspiration and Research

OpenEchelon is being designed independently while studying the wider agent ecosystem.

Projects and systems being examined for architecture, UX, runtime design, interoperability, and lessons learned include:

- Grok Bot
- OpenClaw
- Rakazo
- OpenMausBot
- Agent Swarm
- OpenFang
- Nanobot
- OpenHands
- Agent Zero
- OpenGrok
- OpenGrokBot
- Guaca
- BOTROSTER
- OpenOffice
- OpenExecutive
- OpenLegion
- OpenCouncil
- OpenCompany projects
- other organizational-agent experiments

These projects have different licenses, architectures, and goals.

OpenEchelon will respect their respective licenses and attribution requirements.

The objective is not to repackage another framework.

The objective is to learn from the ecosystem and build a coherent organizational runtime with its own architecture.

---

## What OpenEchelon Is Not

OpenEchelon is not intended to be:

- another multi-agent group chat
- a visual workflow builder
- a wrapper around one model provider
- a collection of hard-coded agent prompts
- a requirement to run 1,000 LLMs simultaneously
- a replacement for every existing agent framework

It is intended to become a coordination layer capable of employing different models, tools, runtimes, and frameworks as parts of one structured AI organization.

---

## Long-Term Vision

The long-term goal is simple:

> **Give an AI organization an objective. Talk to its CEO. Let the organization handle the rest.**

An individual should eventually be able to operate research, engineering, analysis, administration, monitoring, software development, and other knowledge-work functions through one coherent hierarchy of AI employees.

The complexity belongs inside the organization.

The user should see the result.

---

## Project State

Pre-alpha, and specific about it.

| Component | State |
|---|---|
| [Phase 0 organizational data model](docs/architecture/phase-0.md) | Built and tested — employees, departments, grants, tasks and delegation trees, typed messages, artifacts, reviews, execution resources, quota, routing decisions |
| [Resource Governor](spikes/resource_governor) | Spike, measured against labelled scenarios |
| Permission enforcement | Modelled, not enforced |
| Organization runtime, storage, scheduler | Not started |
| Released package | None |

The implementation is Python 3.12+ ([ADR 0002](docs/adr/0002-implementation-stack.md)). Language choice binds the runtime only — an employee can still be executed by a CLI agent or service written in anything.

```bash
git clone https://github.com/NAME0x0/OpenEchelon.git
cd OpenEchelon
uv sync --group dev
uv run pytest -q                                    # model + governor tests
uv run python spikes/resource_governor/run.py       # the cost/quality measurement
```

**Why the Governor comes first.** The economic argument — cheapest sufficient intelligence, escalate when it fails — rests entirely on a component that decides whether a cheap answer was good enough. Published routing work suggests that component generalizes poorly outside the distribution it was tuned on. Building the organization runtime on an unvalidated estimator would spend the larger investment before testing the premise, so the spike is sequenced first and its results are reported honestly, including the false accept it produces. See [ADR 0003](docs/adr/0003-quality-estimation-is-the-load-bearing-component.md).

---

## Frequently Asked Questions

Short answers below. The full set lives in [`docs/faq.md`](docs/faq.md).

**Is OpenEchelon usable today?**
No. It is pre-alpha, in the architecture and prototyping stage. There is no runtime implementation and no released package.

**How is this different from a multi-agent swarm?**
A swarm is flat — one lead fans work out to peers, usually sharing one context and one model. OpenEchelon is hierarchical, and the hierarchy carries operational meaning: information access, permissions, reasoning budgets, escalation paths, and model tier all vary by rank. In a flat swarm, ten agents on one problem tends to mean ten expensive contexts reasoning about the same thing.

**Does a thousand agents mean a thousand running models?**
No. Logical identity is deliberately separated from execution. A thousand registered employees might mean fifty assigned and twenty actively executing against a limited pool.

**Which providers does it require?**
None. Local inference (Ollama, llama.cpp, OpenAI-compatible servers), CLI coding agents (Codex CLI, Claude Code, Gemini/Antigravity), and hosted APIs all sit behind adapters. Local-only operation is a supported target.

**Is it a workflow builder or a chatbot wrapper?**
Neither, by explicit non-goal. Execution plans are constructed from organizational structure, policy, and available resources rather than pre-wired by the user.

---

## Contributing

OpenEchelon is in the architecture and prototyping stage, which shapes what is useful to contribute. Architectural critique of [`docs/principles.md`](docs/principles.md), prior-art analysis of existing agent frameworks, and concrete proposals for the core data models and protocols are the highest-value contributions right now. Large speculative implementations are premature until the core model is frozen.

Start here:

- [CONTRIBUTING.md](CONTRIBUTING.md) — what to contribute, the workflow, and the bar every change must clear
- [Discussions](https://github.com/NAME0x0/OpenEchelon/discussions) — architectural debate belongs here before it becomes an issue
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md) — threat model and private vulnerability reporting

Every substantive change is evaluated against the Architectural Test at the end of [`docs/principles.md`](docs/principles.md).

---

## License

OpenEchelon is licensed under the [Apache License 2.0](LICENSE), including its explicit patent grant. See [NOTICE](NOTICE) for attribution requirements.

OpenEchelon studies the wider agent ecosystem but does not vendor code from it. Projects referenced above carry their own licenses, and those are respected separately.

---

## Citation

If you reference OpenEchelon in academic or technical work, citation metadata is in [`CITATION.cff`](CITATION.cff).

---

> **OpenEchelon** — the operating system for AI organizations.
>
> Give an AI organization an objective. Talk to its CEO. Let the organization handle the rest.
