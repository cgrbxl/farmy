# ADR 0006 — Consolidate architecture before deployment

Date: 2026-09-18
Status: Accepted work sequence from the maintainer. Detailed module/security proposals remain under review.

## Decision

Work in this order: capabilities and module ownership; inter-module contracts; secure communication and authorisation; per-module technical design and implementation; then independent deployment across macOS, Windows, Linux and cloud Kubernetes.

Use the [module architecture](../module-architecture.md) and [communication design](../module-communication.md) as consolidated review drafts. They do not automatically approve a core composition, identity vendor, trust protocol, grant format or application framework.

Scaleway remains the first selected cloud provider. Defer project, region, budget, sizing and infrastructure implementation until module requirements are established. Existing release and landing-zone documents remain requirements for later work, not the current implementation priority.

## Rationale and consequences

Deployment packages must follow actual responsibilities, state ownership, trust boundaries and dependencies. Designing infrastructure first risks coupling modules to one environment and disguising unresolved contracts. Maintain portability as a design constraint now, but prove each target with packaging and tests later. No application or infrastructure is implemented by this ADR.
