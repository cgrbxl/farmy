# Exchange

Status: family guidance; no reference runtime or stable public API is implemented yet.

## Responsibility and state

Prepare exact disclosures, bind approval to recipient/content/purpose, deliver and record receipts.

Owned state: Disclosure manifests, delivery attempts, retention and acknowledgement uncertainty.

Boundary: Not a generic source connector, computation engine or equipment controller.

## First increment

Preview and authorise export of exact synthetic content, reject altered payload/recipient and record delivery outcome.

Required contract areas: Disclosure/receipt contract, source read and separate export authority, recipient adapter semantics.

Change-locality test: A recipient protocol adds an adapter; it should not alter Processing or Knowledge.

## Integration and environment obligations

Approved destination connectivity, output storage, narrowly scoped credentials and explicit external retention limits.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.

## Data spaces and credential disclosure

Exchange supports the target data-space model by preserving source conditions, declared recipients/purposes and accountable outward disclosure. It may present permitted owner/contributor claims through credential adapters; presentation is not an automatic consequence of holding a valid signature. Common governance supplements each participant’s authority rather than centralising it. These are design requirements, not implemented federation or credential support. See [core concepts](../../docs/core-concepts.md).
