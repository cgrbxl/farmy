# Roadmap

No runtime work is marked complete.

## M0 — Architecture repository (this baseline)

Document vision, service boundaries, trust, composition, examples, decision process and acceptance criteria. Licensing is resolved through [ADR 0003](decisions/0003-apache-2.0.md): Apache 2.0 applies to original repository materials. This does not imply a working runtime.

## Current priority — Architecture consolidation

Following [ADR 0006](decisions/0006-architecture-first.md), review capabilities and module ownership, communication contracts, security boundaries and each module’s technical design before deployment. Review drafts: [abstract capability coverage](capability-review.md), [module integration profile](module-integration.md), [module architecture](module-architecture.md) and [communication](module-communication.md). Resolve the proposed minimal core, identity/trust bootstrap, grant/delegation model, persistence/key protection and offline semantics. Scaleway setup is deferred.

## MVP delivery rule

Use concrete end-to-end cases to test a small subset of capabilities, then extend based on evidence, following [ADR 0007](decisions/0007-incremental-modularity.md). Review the proposed [module grouping and change scenarios](module-architecture.md). For every increment, record changed implementations, contracts, configuration and migration, and prove that unaffected modules can remain on their existing versions.

The [repository structure](repository-structure.md) now separates family guides, public profiles, solution recipes, deployment adapters, conformance and optional SDKs. These are documentation scaffolds; runtime and deployable artifacts remain unimplemented.

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

## Initial work items

- Define resource/version/provenance schema.
- Define grant and offline-revocation model.
- Specify descriptor and binding schemas.
- Define ingestion job lifecycle and duplicate handling.
- Specify knowledge evidence envelope and removal semantics.
- Design source connector protocol for offline laptops.
- Define model routing and egress policy.
- Build two-provider substitution acceptance scenario.
