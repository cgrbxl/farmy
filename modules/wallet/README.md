# FarmWallet

Status: family guidance plus a narrow experimental [UC-001 reference runtime](../../solutions/core/uc001/README.md). Its draft operations do not implement this entire family or a stable public API.

## Responsibility and state

Resource/collection identity, immutable version inventory, provenance acceptance, policies, grants and retention decisions.

Owned state: Authoritative resource/policy metadata and transactional acceptance/audit records.

Boundary: No parser, index engine, external provider SDK or workflow execution.

## First increment

Register and inspect a synthetic local document; preserve identity after relocation and reject unauthorised/stale operations.

Required contract areas: Resource/version/provenance and grant contracts; trusted caller/issuer profile. Source bytes remain behind connectors.

Change-locality test: New document formats must not add parsing code here. New security semantics require an explicit policy/contract decision.

## Integration and environment obligations

Identity adapter, metadata storage, key custody/recovery and durable audit; no shared database with other modules.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.
