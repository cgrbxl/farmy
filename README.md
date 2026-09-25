# Farmy

Farmer-controlled digital memory and a composable ecosystem of agricultural intelligence services.

**Status: architecture baseline, draft integration contracts, and nine verified synthetic macOS technical slices covering controlled memory, exact-source evidence, source-scoped observations, a cited local-model answer and a live operational dashboard and controlled disclosure across separate services. This is an experimental development build, not a production application or cross-platform release.**

Farmy connects information held in local folders, managed encrypted vaults and cloud stores. Farmers choose independently supplied ingestion, knowledge, model and copilot services, deciding what each may access and transmit. Services can run on a laptop, private infrastructure or provider infrastructure in the same installation.

Explore the [interactive visual project guide](dashboard/README.md): architecture, capabilities, data flows and delivery progress. Open `dashboard/index.html` locally; no installation or build is needed.

Explore the [phone solution mockup](docs/mock/README.md): Las Tres Encinas illustrates the intended farmer experience, with optional explanations of the nine module families. All interactions are simulated.

## What can I actually use?

**One interactive journey is available:** preview a synthetic source document, add it to your Wallet, open its exact managed copy, grant a demo consumer access and revoke it. [Launch the workbench and follow the steps](solutions/interactive/uc010/README.md). The operational monitor is read-only. Other foundations run through scripts/APIs; the phone mockup remains simulated. Technical slice/test counts are not a count of usable product features.

## Three ideas brought together

- **AI-enabled plasticity:** AI can analyse content, create embeddings and propose ontologies, and also generate source-interface mappings or adapter code. A module with an appropriate extension mechanism can admit new behaviour without redeploying its host. Extensions still need versions, validation and explicitly delegated activation rights.
- **Source-governed data spaces:** independently controlled sources retain their own consumption and disclosure policies while participating in common governance. A shared ecosystem does not require centralising their data or authority.
- **Wallet-based trust networks:** owners and contributors can issue signed, scoped claims that holders present and other parties verify or build upon. Signatures support attribution and integrity; accepting ownership or a contribution requires explicit trust rules and evidence, separately from data-access permission.

These are core design aims. Runtime-generated interfaces, federated data-space governance and credential trust chains are **not yet implemented** by the nine local slices. Read [the concepts, examples and boundaries](docs/core-concepts.md).

A source can be on your own device and still be **outside the Wallet**. Explicit admission creates an individually governed item with metadata and provenance; its storage location remains independent. See [connected sources and managed items](docs/sources-and-managed-items.md).

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

Build one small use case from design to a running demonstration, then extend it without breaking earlier cases. The reference architecture and nine-family grouping are in place. [Run UC-001](solutions/core/uc001/README.md) for controlled memory, or [run UC-002](solutions/document-path/uc002/README.md) for extraction, evidence retrieval and recoverable jobs across five services. [Run UC-003](solutions/sensor-path/uc003/README.md) for source permissions covering ongoing observations. [Run UC-004](solutions/assisted-answer/uc004/README.md) for a cited answer using installed local Qwen through Ollama. [Launch UC-005](solutions/operations/uc005/README.md) for a live, read-only view of module health, dependencies and authorised contents. [Run UC-006](solutions/disclosure/uc006/README.md) to preview, approve and deliver exact content to a synthetic recipient, with receipt recovery. [Run UC-008](solutions/replacement/uc008/README.md) to replace one of two Knowledge instances and rebuild through public APIs. [Run UC-009](solutions/managed-items/uc009/README.md) to admit a selected source email as an individually governed managed copy. [Launch UC-010](solutions/interactive/uc010/README.md) for the first interactive owner/consumer journey. Verify all 115 tests and nine demos with `.venv/bin/python scripts/verify.py --with-local-model`; omit the flag to run without the real-model prerequisite.

The [minimum integration foundation](contracts/v0.1-draft/README.md) now provides a runnable structural validator and outlines the common technical profile. Start with the draft [working method](docs/working-method.md), [delivery queue](docs/delivery-backlog.md) and [UC-001 controlled local memory](solutions/core/use-cases/UC-001-controlled-memory.md). Contracts, security and implementation evolve together per slice; deployment across all target environments follows proven module needs.

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

This repository holds shared architecture, draft interoperability contracts and narrow reference implementations. Contributors may maintain their implementations in independent repositories. Farmy should not require one vendor, one model, one storage provider or a shared internal database.

All examples are synthetic. Do not commit farm data, credentials or private endpoints.

## Licensing

Farmy’s original code, contracts and documentation are licensed under [Apache 2.0](LICENSE). Sharing improvements is encouraged, not required. See [LICENSING.md](LICENSING.md) for scope, exclusions and contribution terms.

UC-007 is **in progress**: an S3 source implementation and 11 additional local HTTP-double checks are available. [Run the local preview](solutions/s3-source/uc007/README.md); real Scaleway validation awaits an approved bucket/prefix and scoped credential reference. It is not counted among the nine verified slices (UC-001–006 and UC-008–010).
