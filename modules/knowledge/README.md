# Knowledge

Status: family guidance; no reference runtime or stable public API is implemented yet.

## Responsibility and state

Indexing, retrieval, optional graph queries, freshness and removal.

Owned state: Derived indexes and exact source/version mappings.

Boundary: Not a second resource authority; no implicit disclosure to every querier.

## First increment

Retrieve a known fact with exact evidence; suppress revoked scope and rebuild from accepted inputs.

Required contract areas: Evidence/query/index lifecycle, source schema features and Wallet authorisation.

Change-locality test: Replace the implementation through binding and declared index rebuild/migration; do not require another provider’s private schema.

## Integration and environment obligations

Service-owned index storage, authorised source access and permission checking; scaling does not change access rules.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.
