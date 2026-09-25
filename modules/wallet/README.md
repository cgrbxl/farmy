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

## Accepted extensions

[ADR 0012](../../docs/decisions/0012-source-permissions-and-wallet-complements.md) scopes ongoing-data permissions to source, owner and consumer. Observation identifiers remain evidence references, not individual approval requirements. External credential wallets complement FarmWallet through adapters; they do not automatically replace its authority role. Source permissions are implemented narrowly in [UC-003](../../solutions/sensor-path/uc003/README.md); external-wallet integration remains a requirement, not an implemented feature.

## Operational monitoring

[UC-005](../../solutions/operations/uc005/README.md) adds an optional, receiver-authorised [summary API](../../contracts/uc005/README.md). This implementation owns its count queries and exposes only metadata/recent outcomes to an explicitly enrolled monitor. Existing compositions keep monitoring disabled; no private database is shared.

## Trust networks and independent source authorities

Wallet responsibilities extend to scoped signed ownership/control declarations, third-party certifications, confirmations, reviews and markings over exact evidence. Participants can issue, hold, present and verify claims, then issue new claims referencing earlier ones. A verifier evaluates each issuer and statement explicitly; signatures establish attributable claims rather than automatic truth, ownership or transitive trust. Access grants and credential assurance remain separate.

Wallet instances cooperate in data spaces without merging their authority namespaces. Source policies and common governance both apply. Signing/key custody and credential-format operations may use attached wallet/adapters; this does not automatically replace FarmWallet. These target capabilities remain unimplemented. See [core concepts](../../docs/core-concepts.md).

## Future interactive modes

See the [interactive module backlog](../../docs/interactive-modules.md) for staged user interfaces, family ownership and acceptance criteria. These modes are planned; the current monitoring interface remains read-only.

[UC-009](../../solutions/managed-items/uc009/README.md) adds opt-in managed-copy metadata, inherited reader ceilings and individual read restrictions. Wallet membership is logical, independent of storage location.
