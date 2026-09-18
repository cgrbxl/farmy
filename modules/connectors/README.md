# Connectors

Status: family guidance; no reference runtime or stable public API is implemented yet.

## Responsibility and state

Version-aware storage access and external-source acquisition, as separately advertised operations.

Owned state: Provider credential references, source cursors, location/version mappings and staging retention records.

Boundary: No parsing, domain analytics or authority to approve disclosure.

## First increment

Separate Local Folder and S3 implementations using the same supported storage profile.

Required contract areas: Resource/version references, storage operations and later acquisition/stream extensions.

Change-locality test: A new source should add an implementation or adapter, not change Wallet or Knowledge. Streaming semantics require a separate extension.

## Integration and environment obligations

Filesystem/device or provider reachability, platform permissions and secret integration; disclose real co-location constraints.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.
