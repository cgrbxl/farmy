# Roadmap

Six synthetic macOS slices now cover controlled memory, exact-source evidence, source permissions, a cited local-model answer and live operational monitoring and controlled exact-document disclosure. See the [delivery queue](delivery-backlog.md) for runnable evidence. Broader runtime and deployment conformance remains pending.

## M0 — Architecture repository (this baseline)

Document vision, service boundaries, trust, composition, examples, decision process and acceptance criteria. Licensing is resolved through [ADR 0003](decisions/0003-apache-2.0.md): Apache 2.0 applies to original repository materials. This does not imply a working runtime.

## Current priority — Continue vertical delivery

Use the [working method](working-method.md) and [delivery queue](delivery-backlog.md). Retain existing slices as regression evidence; controlled export is demonstrated in UC-006; UC-007 is now in progress: the S3 adapter and local HTTP-double checks run, while real Scaleway validation awaits an approved test location and credential reference. The clarified [core concepts](core-concepts.md) guide future acceptance cases without changing that order.

A [future interactive track](interactive-modules.md) adds AI configuration, document-claim issuance, holder-signed presentation and external verification through interfaces or QR requests, followed by contribution chains and other family interactions. These are candidate vertical increments, not current dashboard features or a change to the next queued outcome.

The milestones below are outcome areas, not waterfall phases. Contract, implementation, security and conformance work happen together inside each use-case increment; M1 does not need to be complete for all families before M2 begins. Platform-specific packaging follows working module needs, while a reproducible local run is part of every slice.

The repository organisation is in place. UC-001 through UC-006 establish a narrow working local composition; deployment profiles and broader solution recipes remain documentation scaffolds.

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

## Architectural proofs still ahead

The [three core concepts](core-concepts.md) are design drivers across the roadmap, not optional branding for late-stage plugins:

- Admit an AI-generated interface to a supported source without redeploying its host; demonstrate limited privileges, pinned revisions and rollback.
- Connect independently governed sources/wallets under common participation rules; demonstrate distinct disclosure policies and denied combinations.
- Present owner and third-party contribution claims through issuer/holder/verifier chains; demonstrate explicit trust decisions, status checks and rejection of unacceptable claims.

Each needs a concrete use case and a tested profile. No generic self-programming runtime, data-space standard or credential technology has been selected.

## Contract areas delivered as use cases need them

- Define resource/version/provenance schema.
- Define grant and offline-revocation model.
- Specify descriptor and binding schemas.
- Define ingestion job lifecycle and duplicate handling.
- Specify knowledge evidence envelope and removal semantics.
- Design source connector protocol for offline laptops.
- Define model routing and egress policy.
- Build two-provider substitution acceptance scenario.
