# Knowledge

Status: family guidance plus a narrow experimental [UC-002 implementation](../../solutions/document-path/uc002/README.md). It does not implement this whole family or a stable public API.

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

## Operational monitoring

[UC-005](../../solutions/operations/uc005/README.md) adds an optional, receiver-authorised [summary API](../../contracts/uc005/README.md). This implementation owns its count queries and exposes only metadata/recent outcomes to an explicitly enrolled monitor. Existing compositions keep monitoring disabled; no private database is shared.

## Replacement evidence

[UC-008](../../solutions/replacement/uc008/README.md) runs Evidence Knowledge and an alternative [Ledger Knowledge](ledger/service.py) domain implementation. Both implement UC-002 operations and use the optional transport SDK; each owns a different private schema. Replacement starts empty and requires a newly keyed, authorised public-API rebuild. This does not prove generic query equivalence or independent transport conformance.
