# OpenEchelon — Immutable Principles

> These principles define what OpenEchelon fundamentally is.

OpenEchelon may change languages, frameworks, databases, model providers, user interfaces, deployment methods, and implementation strategies over time.

These principles should remain stable.

They are architectural constraints rather than feature ideas.

---

# 1. OpenEchelon Is an Organization, Not a Swarm

OpenEchelon models structured organizations of AI agents.

The default abstraction is not:

```text
Lead Agent
   |
   +-- Agent
   +-- Agent
   +-- Agent
```

It is:

```text
                         Human Owner
                              |
                              v
                             CEO
                              |
               +--------------+--------------+
               |              |              |
               v              v              v
          Executives     Executives     Executives
               |              |              |
               v              v              v
           Directors      Directors      Directors
               |              |              |
               v              v              v
            Managers       Managers       Managers
               |              |              |
               v              v              v
         Specialists    Specialists    Specialists
               |              |              |
               v              v              v
            Workers        Workers        Workers
```

Hierarchy is a first-class architectural primitive.

OpenEchelon should support:

- reporting relationships
- authority boundaries
- departments
- delegation
- escalation
- review chains
- resource budgets
- information boundaries
- organizational memory
- accountability

A flat group of agents may exist inside OpenEchelon, but it is not the primary organizational model.

---

# 2. The Human Owner Retains Final Authority

Every OpenEchelon organization ultimately belongs to a human or authorized human group.

The organization exists to serve that authority.

By default:

```text
Human Owner
     |
     v
    CEO
     |
     v
Organization
```

The organization must never structurally place itself above its human owner.

Human authority may:

- create objectives
- stop work
- revoke permissions
- inspect decisions
- change organizational structure
- override resource policies
- approve sensitive actions
- reject recommendations
- terminate agents
- suspend departments
- replace executives

Autonomy exists within delegated authority.

It is not sovereignty.

---

# 3. The Default User Interface Is Executive-Level

The normal user should not need to coordinate individual workers.

The primary interaction model is:

```text
Human
  |
  v
CEO
```

The CEO receives goals, coordinates the organization, and returns consolidated results.

The user may inspect deeper organizational layers when desired, but operational complexity should not be imposed on them by default.

The interface should expose complexity progressively.

Normal interaction:

```text
"Investigate this problem and build the best solution."
```

Not:

```text
Choose agent.
Choose model.
Choose workflow.
Choose worker count.
Choose reviewer.
Choose tool.
Choose escalation path.
```

Those decisions belong inside the organization unless explicitly overridden.

---

# 4. Agent Identity Is Separate From Model Identity

An OpenEchelon employee is not a model.

An employee must not fundamentally be defined as:

```text
Claude Agent
Gemini Agent
Codex Agent
Qwen Agent
```

An employee is a persistent organizational identity.

```text
Agent
├── identity
├── role
├── title
├── department
├── manager
├── direct reports
├── competencies
├── permissions
├── responsibilities
├── memory
├── assignments
├── performance history
├── reasoning ceiling
├── resource authority
└── organizational history
```

Execution resources are assigned separately.

```text
Agent
  |
  v
Task
  |
  v
Resource Governor
  |
  +-- local model
  +-- frontier model
  +-- CLI agent
  +-- API model
  +-- external runtime
```

The same employee may use different execution resources for different tasks.

---

# 5. Logical Agents Are Separate From Running Processes

OpenEchelon must be able to represent far more employees than are actively executing.

```text
1,000 logical employees
         |
         v
  50 assigned employees
         |
         v
   20 active employees
         |
         v
  limited execution pool
```

An agent may exist persistently without:

- a dedicated model process
- a dedicated container
- a dedicated GPU allocation
- an active conversation
- a running browser
- a permanent CLI session

Persistent identity and active execution are separate concepts.

This separation is required for scalability.

---

# 6. Workers Execute; Managers Manage

Organizational rank must have operational meaning.

Workers should primarily perform bounded assignments.

Managers should primarily:

- understand objectives
- decompose work
- assign tasks
- resolve ambiguity
- inspect results
- coordinate dependencies
- request reviews
- escalate difficult problems
- compress information
- report upward

A worker should not repeatedly rethink strategy that has already been decided by management.

Example worker assignment:

```text
TASK:
Inspect these files for duplicated validation logic.

OUTPUT:
Return:
- file
- function
- duplicated pattern
- confidence

DO NOT:
- redesign the architecture
- inspect unrelated components
- modify source code
- reconsider the project strategy
```

This reduces unnecessary reasoning and context consumption.

---

# 7. Reasoning Is a Budgeted Organizational Resource

Reasoning should not automatically be maximized.

Organizational rank defines a maximum reasoning allowance, not a mandatory reasoning level.

Conceptually:

```text
Worker       -> none
Specialist   -> none / low
Team Lead    -> low
Manager      -> low / medium
Director     -> medium / high
Executive    -> high
CEO          -> highest justified
```

Actual reasoning should be:

```text
actual_reasoning =
    minimum(
        reasoning_required_by_task,
        reasoning_allowed_by_role
    )
```

A director performing an obvious operation should not consume high reasoning merely because the role permits it.

---

# 8. Use the Cheapest Intelligence That Can Reliably Complete the Task

OpenEchelon should optimize for quality per unit of scarce resource.

The default strategy is:

```text
Start cheap
   |
   v
Attempt task
   |
   +---- success ----> complete
   |
   +---- insufficient
              |
              v
           escalate
```

Possible execution hierarchy:

```text
Local small model
        |
        v
Local stronger model
        |
        v
Low-cost frontier model
        |
        v
Strong frontier model
        |
        v
Executive-grade model
```

Escalation should happen because it is justified, not because a powerful model happens to be available.

---

# 9. Frontier Models Are Scarce Organizational Resources

Codex, Claude, Gemini, subscription sessions, API budgets, GPU time, context windows, and concurrency are resources.

They must be governed.

OpenEchelon should maintain awareness of:

- remaining quota
- reset windows
- monetary cost
- latency
- context usage
- model availability
- concurrency
- provider reliability
- task priority
- historical success rates

Routine work must not consume resources reserved for high-value work.

Resource management is part of orchestration, not an afterthought.

---

# 10. Local-First Execution Is Preferred Where Practical

OpenEchelon should be capable of meaningful operation using local resources.

Local execution is particularly suitable for:

- classification
- routing
- extraction
- transformation
- summarization
- simple coding
- repetitive work
- bounded tool use
- validation
- structured data generation
- task preprocessing

Frontier models should be used when their additional capability materially improves expected outcome quality.

Local-first does not mean local-only.

---

# 11. Models and Providers Must Be Replaceable

OpenEchelon must not depend architecturally on one model company.

Supported execution resources may include:

- Ollama
- llama.cpp
- OpenAI-compatible servers
- Codex CLI
- Claude Code
- Gemini / Antigravity CLI
- OpenAI APIs
- Anthropic APIs
- Gemini APIs
- OpenRouter
- external agent runtimes
- future providers

Provider-specific behavior belongs behind adapters.

The organizational runtime should remain provider-independent.

---

# 12. External Agent Frameworks Can Be Employees or Tools

OpenEchelon should not need to replace every existing agent ecosystem.

Systems such as:

- OpenClaw
- OpenHands
- coding harnesses
- MCP servers
- ACP agents
- browser agents
- external automation systems

may operate as:

```text
Employee Runtime
Tool Provider
Department Service
External Specialist
Execution Backend
```

OpenEchelon should coordinate useful ecosystems rather than unnecessarily duplicate them.

---

# 13. Information Access Follows Organizational Need

Agents should not automatically share one global context.

A worker receives what is necessary for its assignment.

A manager receives what is necessary to supervise its team.

A director receives what is necessary to coordinate managers.

An executive receives what is necessary for strategic decisions.

The CEO receives the information required to represent the organization to the human owner.

Default principle:

> Minimum sufficient organizational context.

This improves:

- security
- privacy
- context efficiency
- specialization
- reliability
- scalability

---

# 14. Managers Are Context Compressors

Raw organizational output should not propagate upward unchanged.

Consider:

```text
30 workers
x
5,000 tokens each
=
150,000 tokens
```

The CEO should not need to ingest all of it.

Instead:

```text
Workers
   |
   v
Managers
   |
   | consolidate
   v
Directors
   |
   | synthesize
   v
Executives
   |
   | compress strategically
   v
CEO
```

Managers transform raw work into higher-value representations.

Reports should preserve references to underlying evidence so deeper inspection remains possible.

---

# 15. Communication Is Structured

OpenEchelon agents should not behave as members of one unrestricted group chat.

Internal communication should support explicit semantic types.

Examples:

```text
TASK
DELEGATION
REPORT
QUESTION
ANSWER
STATUS
ARTIFACT
REVIEW
APPROVAL
REJECTION
ESCALATION
RESOURCE_REQUEST
RESOURCE_GRANT
RESOURCE_DENIAL
IMPLEMENTATION_REQUEST
RESEARCH_REQUEST
VERIFICATION_REQUEST
```

Structured communication allows:

- auditing
- routing
- permissions
- automation
- task tracking
- dependency tracking
- review chains
- reliable orchestration

Natural-language payloads may exist inside structured messages.

---

# 16. Communication Follows Authority Paths by Default

A worker should not normally contact the CEO directly.

Default reporting path:

```text
Worker
  |
  v
Manager
  |
  v
Director
  |
  v
Executive
  |
  v
CEO
```

Downward work follows the inverse direction.

Cross-department communication may be:

- routed through management
- explicitly authorized
- temporarily opened for a task
- mediated through a shared project structure

The system should prevent uncontrolled agent-to-agent communication graphs.

---

# 17. Delegation Creates Traceable Task Trees

Delegation should create explicit parent-child relationships.

```text
Task A
 |
 +-- Task A.1
 |      |
 |      +-- Task A.1.1
 |
 +-- Task A.2
 |
 +-- Task A.3
```

Every task should be traceable to:

- who created it
- why it exists
- its parent objective
- who owns it
- who supervises it
- what resources it consumed
- what artifacts it produced
- who reviewed it
- what decision resulted

Delegation must not disappear into conversational history.

---

# 18. Artifacts Are First-Class Organizational Objects

Important work should not exist only as chat text.

Agents may produce:

- source code
- reports
- research
- datasets
- screenshots
- diagrams
- tests
- plans
- documents
- decisions
- benchmarks
- patches
- logs

Artifacts should have durable identities and provenance.

Example:

```text
CEO decision
    |
    +-- Executive report
            |
            +-- Director report
                    |
                    +-- Manager review
                            |
                            +-- Worker artifact
```

The system should be able to reconstruct this chain.

---

# 19. Reviews Should Be Organizationally Independent Where Useful

The same agent that performs work should not always be trusted to certify it.

Important work may pass through independent review.

```text
Implementation
     |
     v
Reviewer
     |
     +---- accepted ----> continue
     |
     +---- rejected
              |
              v
          correction
```

Different providers may deliberately be used for independent review.

Example:

```text
Codex
  |
  | implementation
  v
Claude
  |
  | quality review
  v
Manager
```

Provider diversity can reduce correlated failure modes.

---

# 20. Failure Should Trigger Escalation, Not Endless Retry

Repeatedly asking the same resource to solve the same failed task is wasteful.

Failure should produce structured information:

```text
failure type
confidence
attempt count
blocking condition
recommended escalation
```

The Resource Governor or supervising manager may then:

- change model
- increase reasoning
- add context
- request research
- request another specialist
- divide the task
- seek human input
- abandon the task

Retries must be deliberate.

---

# 21. Organizational Memory Is Layered

Memory should exist at multiple scopes.

Possible scopes:

```text
Individual Agent Memory
Team Memory
Department Memory
Project Memory
Organizational Memory
Human Preference Memory
```

Not every memory item belongs everywhere.

A worker's implementation note may not belong in organizational memory.

A company-wide security rule should not live only inside one worker.

Memory scope must be explicit.

---

# 22. Permissions Are Organizational, Not Merely Technical

Access should depend on role and responsibility.

Permissions may govern:

- filesystem access
- browser access
- credentials
- repositories
- communication
- provider usage
- spending
- model tiers
- deployment
- messaging
- external actions
- data sources
- organizational restructuring

Technical sandboxing should enforce organizational policy where possible.

---

# 23. Sensitive External Actions Require Explicit Governance

Actions with meaningful external consequences should be governable.

Examples:

- sending messages
- publishing content
- deleting data
- financial transactions
- production deployments
- changing permissions
- interacting with third-party accounts
- modifying critical infrastructure

Policies may require:

```text
Worker proposal
      |
      v
Manager approval
      |
      v
Execution
```

or:

```text
Executive proposal
      |
      v
Human approval
      |
      v
Execution
```

The required authority depends on risk.

---

# 24. Observability Is Mandatory

Every meaningful execution should be inspectable.

At minimum, OpenEchelon should be able to record:

```text
task
agent
manager
provider
model
reasoning level
runtime
duration
input size
output size
resource usage
quota impact
tools used
artifacts produced
result
review result
failure reason
```

An autonomous organization that cannot explain what happened is not manageable.

---

# 25. Auditability Must Reach the Final Answer

The CEO's final recommendation should be traceable.

Example:

```text
CEO recommendation
    |
    +-- Research Executive report
    |       |
    |       +-- Research Manager report
    |               |
    |               +-- source evidence
    |
    +-- Technology Executive report
    |       |
    |       +-- implementation artifact
    |
    +-- Quality Executive report
            |
            +-- independent review
```

The human owner should be able to ask:

```text
Why did the organization decide this?
```

and inspect the chain.

---

# 26. The Organization Should Learn From Performance

OpenEchelon should eventually learn which resources work best for which tasks.

Example observations:

```text
Local model succeeds on task class X 95% of the time.
Use local execution by default.

Claude review changes the outcome on task class Y only 2% of the time.
Skip expensive review.

Codex resolves task class Z much more reliably than local workers.
Route directly to Codex.
```

Performance history should inform:

- routing
- staffing
- review requirements
- model selection
- reasoning levels
- escalation
- organizational structure

The system should become economically smarter through use.

---

# 27. Optimization Must Consider Quality, Not Only Cost

The cheapest answer is not necessarily the best organizational outcome.

OpenEchelon should optimize across multiple dimensions:

```text
quality
cost
latency
risk
quota
privacy
reliability
importance
```

For high-value tasks, spending more intelligence may be correct.

For routine work, it may be wasteful.

Resource allocation should reflect expected value.

---

# 28. Organizational Roles Should Be Dynamic

OpenEchelon should not require one permanently hard-coded organization.

Organizations may differ.

Examples:

```text
Software Company
Research Laboratory
Investment Research Team
Personal Operations Office
Creative Studio
University Research Group
Security Operations Team
Product Company
```

Agents, departments, reporting lines, permissions, and policies should be configurable.

The organizational runtime remains the same.

---

# 29. Organizations May Restructure

Eventually, OpenEchelon should support organizational change.

Possible changes:

- hiring
- termination
- reassignment
- promotion
- demotion
- department creation
- department merger
- temporary project teams
- changes in reporting lines
- changes in resource authority

These changes must remain auditable and governed.

---

# 30. Persistent Identity Matters

An employee should accumulate organizational history.

Persistent identity may include:

```text
past assignments
performance
specializations
manager feedback
known weaknesses
preferred tools
successful strategies
relevant memory
organizational relationships
```

This allows employees to become more useful over time without requiring one permanently running model session.

---

# 31. Execution Must Be Interruptible

Long-running autonomous work must remain controllable.

The system should support:

- pause
- cancel
- reprioritize
- suspend agent
- suspend team
- suspend department
- revoke resource access
- replace executor
- request immediate report

A human owner should not need to wait for an autonomous process to voluntarily finish.

---

# 32. Concurrency Must Be Explicitly Controlled

More simultaneous agents is not automatically better.

Concurrency consumes:

- CPU
- RAM
- GPU
- provider quota
- network capacity
- context
- coordination overhead

The Resource Governor should decide how much parallelism is justified.

```text
1,000 employees
!=
1,000 simultaneous executions
```

---

# 33. Simplicity at the Surface, Sophistication Underneath

The internal architecture may become complex.

The normal user experience should not.

OpenEchelon should aim for:

```text
User:
"Build this."

CEO:
"Understood."

Organization:
[complex internal operation]

CEO:
"Here is the result, what happened, and what requires your decision."
```

The organizational complexity exists to remove coordination burden from the human.

---

# 34. No Mandatory Workflow Editor

Visual workflows may eventually be useful as an advanced feature.

They must not be required for normal operation.

OpenEchelon should be able to construct execution plans dynamically from organizational structure, policy, objectives, and available resources.

The user should not need to pre-wire every possible process.

---

# 35. Security Is an Architectural Property

Security cannot be added after autonomy.

OpenEchelon should assume:

- model outputs may be wrong
- external content may contain prompt injection
- tools may fail
- agents may misunderstand authority
- credentials require isolation
- workers should have limited access
- external actions may need approval
- organizational boundaries require enforcement

Security decisions should exist in architecture, not only prompts.

---

# 36. OpenEchelon Must Remain Inspectable and Understandable

The project should resist unnecessary architectural complexity.

Core systems should be understandable enough that contributors can reason about:

- why a task was delegated
- why a model was selected
- why an agent had permission
- why escalation occurred
- why resources were consumed
- why a final recommendation was made

Opaque orchestration is undesirable.

---

# 37. Interoperability Is More Valuable Than Reinvention

OpenEchelon should integrate mature external capabilities where doing so is better than rebuilding them.

Possible examples:

```text
MCP
ACP
OpenClaw
OpenHands
Docker
Ollama
existing CLI agents
external browsers
external sandboxes
existing connectors
```

OpenEchelon's unique value is organizational orchestration.

It should not waste resources recreating every surrounding ecosystem.

---

# 38. Open Standards Are Preferred

Where practical, internal and external interfaces should use documented, portable protocols.

Provider-specific integrations should be isolated behind adapters.

OpenEchelon should avoid unnecessary lock-in to:

- proprietary wire formats
- undocumented internal APIs
- one cloud provider
- one model provider
- one agent framework
- one operating system

---

# 39. The Core Must Be Useful Without Cloud Dependency

OpenEchelon should remain capable of operating in a local-only configuration for supported use cases.

Conceptually:

```text
OpenEchelon
    |
    +-- local model
    +-- local filesystem
    +-- local tools
    +-- local database
    +-- local browser
```

Cloud and frontier resources enhance capability.

They should not define the architecture.

---

# 40. The Organization Exists to Produce Outcomes

Agents talking to agents is not success.

Large task graphs are not success.

More tokens are not success.

More autonomous steps are not success.

The objective is:

```text
Human Objective
       |
       v
Organization
       |
       v
Useful Outcome
```

Everything else exists in service of that transformation.

---

# Non-Goals

OpenEchelon is not fundamentally intended to become:

- another chatbot wrapper
- a flat multi-agent swarm
- a mandatory workflow builder
- an interface for manually micromanaging hundreds of agents
- a wrapper around one model company
- a system that maximizes agent count
- a system that maximizes token consumption
- a replacement for every existing agent ecosystem
- an excuse to use frontier models for trivial work

---

# Architectural Test

A future OpenEchelon design decision should be questioned if it violates one or more of these conditions:

```text
Does this preserve human authority?

Does this preserve separation between agent identity and model execution?

Does this support hierarchy rather than forcing flat coordination?

Does this allow cheap work to remain cheap?

Does this avoid unnecessary context sharing?

Does this remain observable?

Does this remain auditable?

Does this preserve provider independence?

Does this support resource governance?

Does this scale logical identity separately from active execution?

Does this reduce rather than increase coordination burden on the user?
```

If the answer is no, the design should require strong justification.

---

# Core Definition

OpenEchelon can be reduced to the following statement:

> **A model-agnostic runtime for structured AI organizations where persistent agents operate within hierarchy, authority, resource, memory, and information boundaries while reporting ultimately to a human owner.**

Or, from the user's perspective:

> **Give an AI organization an objective. Talk to its CEO. Let the organization handle the rest.**
