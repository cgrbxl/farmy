# Roadmap

The [UC-001 macOS slice](../solutions/core/uc001/README.md) has a passing synthetic demo and eight runtime tests. The [draft integration foundation](../contracts/v0.1-draft/README.md) also has executable document/declared-compatibility checks. Broader runtime and deployment conformance remains pending.

## M0 — Architecture repository (this baseline)

Document vision, service boundaries, trust, composition, examples, decision process and acceptance criteria. Licensing is resolved through [ADR 0003](decisions/0003-apache-2.0.md): Apache 2.0 applies to original repository materials. This does not imply a working runtime.

## Current priority — First vertical increment

The accepted reference grouping and architecture are sufficient to scope the first small implementation. Use the draft [working method](working-method.md) and [delivery queue](delivery-backlog.md), starting with [UC-001 controlled local memory](../solutions/core/use-cases/UC-001-controlled-memory.md). Resolve only its contracts/security decisions, build the real path and demonstrate it before expanding.

The milestones below are outcome areas, not waterfall phases. Contract, implementation, security and conformance work happen together inside each use-case increment; M1 does not need to be complete for all families before M2 begins. Platform-specific packaging follows working module needs, while a reproducible local run is part of every slice.

The repository organisation is in place. UC-001 implements controlled local memory; deployment profiles and broader solution recipes remain documentation scaffolds.

## M1 — Contract foundation

Choose identifiers and version semantics, define capability descriptors and grants, publish schemas/API specifications, synthetic fixtures and conformance harness. Resolve transport, identity and key custody with decision records. Capture compatibility and dependency requirements in descriptors; detailed release manifests and landing-zone handoff implementation follow the module design and working path.

## M2 — Working document path

Implement wallet authority, local-folder and S3 connectors, ingestion, knowledge retrieval, model configuration and source-linked answers. Include authoritative/derived record separation, access enforcement, audit and controlled export.

## M3 — Prove composition

Run a wallet on a Mac with cloud ingestion; demonstrate live and staged modes. Connect two knowledge instances. Replace one ingestion or knowledge implementation with an independently implemented provider, using only bindings and declared migration. Prove that closing the dashboard does not stop execution.

## M4 — Deployment and recovery

Provide versioned core/solution and individual module packages for macOS, Windows and Linux laptops and cloud Kubernetes, following [release requirements](releases.md). Test each advertised OS/architecture and lifecycle independently. Implement and validate the first [provider landing zone on Scaleway](providers/scaleway.md), with explicit identity, secrets, network controls, operations, recovery and cost assumptions; add providers incrementally. Unverified targets remain labelled as such.

## M5 — Contributor ecosystem

Catalogue validation, deployment controller, signed/versioned releases and supply-chain checks; additional email, sensor, data-space and credential connectors; agronomic copilots with domain-specific evaluation.

## Contract areas delivered as use cases need them

- Define resource/version/provenance schema.
- Define grant and offline-revocation model.
- Specify descriptor and binding schemas.
- Define ingestion job lifecycle and duplicate handling.
- Specify knowledge evidence envelope and removal semantics.
- Design source connector protocol for offline laptops.
- Define model routing and egress policy.
- Build two-provider substitution acceptance scenario.
