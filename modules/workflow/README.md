# Workflow coordinator

Status: family guidance plus a narrow experimental [UC-002 implementation](../../solutions/document-path/uc002/README.md). It does not implement this whole family or a stable public API.

## Responsibility and state

Durable jobs, steps, triggers, approval state, retries, cancellation and reconciliation.

Owned state: Job/step state, pinned input/binding revisions and idempotency records.

Boundary: No domain calculation or provider SDK; no automatic permission expansion.

## First increment

Run a fixed extraction/indexing workflow and recover from duplicate delivery or worker interruption.

Required contract areas: Job lifecycle, capability operations, Wallet policy decisions and Registry bindings.

Change-locality test: An additional workflow using existing operations should change a reviewed workflow definition, not add domain branches to the engine.

## Integration and environment obligations

Durable service-owned state, clocks/deadlines, worker reachability and scoped credentials; one owner per job.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.
