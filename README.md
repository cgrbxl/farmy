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

Contributors: read [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md). Publication and Mac transfer instructions are in [docs/bootstrap.md](docs/bootstrap.md).

## Repository scope

This repository holds shared architecture and future interoperability contracts. Contributors may maintain their implementations in independent repositories. Farmy should not require one vendor, one model, one storage provider or a shared internal database.

All examples are synthetic. Do not commit farm data, credentials or private endpoints.

## Licensing

A project licence has not yet been selected. Public visibility does not itself grant an open-source licence. See [LICENSING.md](LICENSING.md) before reusing or contributing material.
