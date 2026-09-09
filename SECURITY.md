# Security Policy

## Project status

OpenEchelon is **pre-alpha**. There is no runtime implementation and no released artifact yet. This policy exists so that a reporting channel is in place before the first code lands, not because there is currently deployed software to attack.

## Supported versions

| Version | Supported |
|---|---|
| `main` (pre-alpha) | Best effort |
| Tagged releases | None yet |

## Reporting a vulnerability

**Do not open a public issue for a security vulnerability.**

Use GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/NAME0x0/OpenEchelon/security) of this repository.
2. Select **Report a vulnerability**.
3. Include reproduction steps, affected files or components, and impact.

You should get an acknowledgement within 7 days. Because this is a single-maintainer pre-alpha project, please treat any timeline as best effort rather than a service commitment.

Please do not disclose publicly until a fix is available or 90 days have passed, whichever comes first.

## Threat model

OpenEchelon is designed as an autonomous multi-agent runtime, which makes several classes of issue architecturally in scope rather than incidental. Principle 35 of [`docs/principles.md`](docs/principles.md) states this directly: security is an architectural property, and cannot be added after autonomy.

Issues that are **in scope** once a runtime exists:

- **Prompt injection** that causes an agent to exceed its delegated authority, particularly injection arriving through fetched web content, repository files, tool output, or messages from other agents.
- **Authority escalation** — a worker performing actions reserved for a manager, executive, or the human owner.
- **Information-boundary violations** — an agent reading context, memory, or artifacts outside its organizational need-to-know (Principles 13 and 21).
- **Credential exposure** — provider API keys, tokens, or secrets reaching an agent, log, artifact, or model context that should not hold them.
- **Sandbox escape** — an agent reaching filesystem, network, or process resources beyond its granted permissions (Principle 22).
- **Governance bypass** — an external action with real-world consequences executing without the approval chain its risk level requires (Principle 23).
- **Audit-trail tampering** — falsifying or deleting the delegation, resource-usage, or decision records that make the organization inspectable (Principles 24 and 25).
- **Resource-governance abuse** — causing unbounded quota, cost, or concurrency consumption.

Issues that are **out of scope**:

- Vulnerabilities in third-party model providers, local inference servers, or external agent runtimes. Report those upstream.
- Model outputs that are simply wrong, biased, or low quality. That is a correctness concern, not a vulnerability.
- Missing hardening in documentation-only files, where no executable component exists yet.
- Findings from automated scanners without a demonstrated impact path.

## Reporting scope for architecture

Because the project is still at the design stage, **architectural security findings against `docs/principles.md` are welcome as public discussions**, not private reports. A design flaw in a published document is not a secret. Use private reporting only for issues that could be exploited against a real deployment.
