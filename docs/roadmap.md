# Roadmap

No runtime work is marked complete.

## M0 — Architecture repository (this baseline)

Document vision, service boundaries, trust, composition, examples, decision process and acceptance criteria. Licensing is resolved through [ADR 0003](decisions/0003-apache-2.0.md): Apache 2.0 applies to original repository materials. This does not imply a working runtime.

## M1 — Contract foundation

Choose identifiers and version semantics, define capability descriptors and grants, publish schemas/API specifications, synthetic fixtures and conformance harness. Resolve transport, identity and key custody with decision records. Define release manifests, compatibility declarations and the non-secret landing-zone handoff contract.

## M2 — Working document path

Implement wallet authority, local-folder and S3 connectors, ingestion, knowledge retrieval, model configuration and source-linked answers. Include authoritative/derived record separation, access enforcement, audit and controlled export.

## M3 — Prove composition

Run a wallet on a Mac with cloud ingestion; demonstrate live and staged modes. Connect two knowledge instances. Replace one ingestion or knowledge implementation with an independently implemented provider, using only bindings and declared migration. Prove that closing the dashboard does not stop execution.

## M4 — Deployment and recovery

Provide versioned core/solution and individual module packages for macOS, Windows and Linux laptops and cloud Kubernetes, following [release requirements](releases.md). Test each advertised OS/architecture and lifecycle independently. Implement and validate the first [provider landing zone](cloud-landing-zones.md), with explicit identity, secrets, network controls, operations, recovery and cost assumptions; add providers incrementally. Unverified targets remain labelled as such.

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
