# Farmy

Farmer-controlled digital memory and a composable ecosystem of agricultural intelligence services.

**Status: architecture baseline v0.1 — documentation and illustrative contracts only. No working application, deployment package or security certification is provided yet.**

Farmy connects information held in local folders, managed encrypted vaults and cloud stores. Farmers choose independently supplied ingestion, knowledge, model and copilot services, deciding what each may access and transmit. Services can run on a laptop, private infrastructure or provider infrastructure in the same installation.

## Principles

- Separate control of information from its storage location.
- Separate capability, implementation, running instance, binding and grant.
- Make modules independently deployable wherever their resource dependencies permit it.
- Allow multiple providers and multiple instances of a capability.
- Preserve evidence, provenance and portable resource identity.
- Enforce permission at every service boundary, before data reaches a model.
- Make substitution demonstrable through public contracts and conformance tests.
- Keep the dashboard replaceable; closing it must not stop workflows.

## Current focus

Consolidate capabilities, module ownership, secure communication and per-module technical design before environment-specific deployment. Start with the [abstract capability review](docs/capability-review.md), [module integration profile](docs/module-integration.md), [module architecture](docs/module-architecture.md) and [communication design](docs/module-communication.md). Broad capability coverage, MVP delivery and the [nine-family reference grouping](docs/module-architecture.md) are the current baseline; detailed contracts and implementations remain to be built. See [ADR 0006](docs/decisions/0006-architecture-first.md) and [ADR 0007](docs/decisions/0007-incremental-modularity.md).

## Repository deliverables

| Area | Entry point |
| --- | --- |
| Reference architecture and decisions | [Architecture](docs/module-architecture.md) |
| Public integration, communication and security contracts | [Contracts](contracts/README.md) |
| Guidelines for each module family | [Module guides](modules/README.md) |
| Core and document solution templates | [Design recipes — not yet deployable](solutions/README.md) |
| macOS, Windows, Linux, Kubernetes and Scaleway | [Deployment profiles — not yet implemented](deployments/README.md) |
| Compatibility and security verification | [Conformance plan](conformance/README.md) |
| Optional integration helpers | [SDK scope](sdk/README.md) |

See [repository structure and contributor path](docs/repository-structure.md). Environment profiles implement common requirements; they do not redefine module contracts or permissions.

## Start here

1. [Vision and scope](docs/vision.md)
2. [Architecture](docs/architecture.md)
3. [Deployment and multiplicity](docs/deployment.md)
4. [Contract design](contracts/README.md)
5. [Security and trust boundaries](docs/security.md)
6. [Roadmap and acceptance criteria](docs/roadmap.md)
7. [Decisions and open questions](docs/decisions/0001-composable-services.md)
8. [Implementation kickoff and first milestone](docs/implementation-plan.md)
9. [Reference stack decision](docs/decisions/0002-reference-stack.md)
10. [Versioned solutions and module releases](docs/releases.md)
11. [Cloud provider landing zones](docs/cloud-landing-zones.md)
12. [Scaleway: first cloud provider](docs/providers/scaleway.md)

Contributors: read [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md). Publication and Mac transfer instructions are in [docs/bootstrap.md](docs/bootstrap.md).

## Repository scope

This repository holds shared architecture and future interoperability contracts. Contributors may maintain their implementations in independent repositories. Farmy should not require one vendor, one model, one storage provider or a shared internal database.

All examples are synthetic. Do not commit farm data, credentials or private endpoints.

## Licensing

Farmy’s original code, contracts and documentation are licensed under [Apache 2.0](LICENSE). Sharing improvements is encouraged, not required. See [LICENSING.md](LICENSING.md) for scope, exclusions and contribution terms.
