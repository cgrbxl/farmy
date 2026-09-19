# UC-003 — Source-scoped synthetic observations

Status: ready for implementation; no runtime or acceptance evidence yet.

## Outcome

An owner grants a named consumer access to one synthetic sensor source. The consumer retrieves multiple observations under that source permission, without per-observation approvals. A separately identified source remains inaccessible. Revocation stops subsequent reads, and delivery records identify the consumer and exact observations delivered.

This tests a non-document path while retaining the nine-family architecture. It precedes model integration in the delivery queue.

## Fixture and boundaries

Use two clearly distinct synthetic sources with stable source identities and an explicit owner. Populate timestamped observations with declared units and identifiers. Add an observation after granting access and verify it is covered by the same active source permission. Split data requiring different permissions into separate logical or physical sources; enforce source membership at the serving boundary.

Wallet owns sources, ownership and source/owner/consumer grants. A narrowly scoped Connector owns synthetic observations and source membership, serving through authenticated public contracts. The client remains thin. Add Processing or Knowledge only if the outcome requires them; no new module family is needed.

Exact delivered observation/batch references support provenance and audit, independently of grant granularity. The runtime must distinguish observed access/delivery from unknowable downstream consumption.

## Acceptance requirements

- One source grant permits multiple observations, including a subsequently added observation, without issuing another grant.
- A grant for source A never permits source B, including a falsely relabelled observation or altered request.
- Unknown/wrong consumers, wrong owner/source scope and expired/revoked permissions are denied.
- Restart preserves source identities, observations and permission enforcement.
- Each successful delivery has an audit record linking authenticated consumer, source, applicable permission and exact delivered observation/batch references. Denied operations are recorded without content leakage.
- Unavailable authority fails closed; no claim of offline permission support.
- UC-001 and UC-002 still pass. Record actual module changes against the predicted Wallet/Connector/client impact.

## Deferred

Physical devices, high-volume streaming infrastructure, dynamic consumer groups, offline authorisation, general terms evaluation, external credential wallets, watermarking, model invocation, production security and other deployment targets.

Define the narrow schemas, delivery semantics and reproducible demo during implementation, following the [working method](../../../docs/working-method.md). These are acceptance requirements, not claims that source-level permissions already exist.
