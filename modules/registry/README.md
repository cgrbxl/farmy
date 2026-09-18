# Service registry

Status: family guidance; no reference runtime or stable public API is implemented yet.

## Responsibility and state

Implementation and instance registration, compatibility declarations, configuration references and binding revisions.

Owned state: Installation composition metadata and binding history.

Boundary: Does not issue wallet grants, execute jobs or trust self-advertised issuers.

## First increment

Bind a compatible connector/processor and reject an unsupported feature or untrusted endpoint change.

Required contract areas: Descriptor, instance and binding contracts; administrator identity/trust profile.

Change-locality test: A new provider should register a descriptor rather than require registry source changes.

## Integration and environment obligations

Persistence, authenticated endpoint resolution and health observation; monitors receive no automatic content grants.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.
