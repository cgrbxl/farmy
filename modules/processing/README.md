# Processing

Status: family guidance; no reference runtime or stable public API is implemented yet.

## Responsibility and state

Extraction, normalisation, validation, calculations, transformations and rendering through specialised implementations.

Owned state: Algorithm/configuration version, attempt state and proposed result/provenance references.

Boundary: Cannot commit Wallet records, own every algorithm or perform unapproved external effects.

## First increment

A Document Extraction implementation handles synthetic text, proposes version-linked outputs and contains malformed inputs.

Required contract areas: Job envelope, typed input/output schemas, provenance and authorised storage transfers.

Change-locality test: Add a parser or independent processor; keep its domain rules outside Coordinator and Wallet.

## Integration and environment obligations

Bounded execution, parser isolation and temporary/output storage; model use, if needed, is an explicit additional dependency.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.
