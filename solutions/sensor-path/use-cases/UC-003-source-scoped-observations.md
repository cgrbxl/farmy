# UC-003 — Source-scoped synthetic observations

Status: done for synthetic macOS development, verified 2026-09-19. [Run instructions](../uc003/README.md).

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

The [versioned contract](../../../contracts/uc003/README.md), [runner](../uc003/README.md) and [nine acceptance tests](../../../conformance/uc003/test_runtime.py) implement and exercise these requirements for the stated development scope.

## Evidence and actual module impact

Verified on macOS arm64, Python 3.14.6 and OpenSSL 3.6.3: nine UC-003 acceptance tests, the prior 36 tests, structural/documentation checks and all three demos passed. Run `.venv/bin/python scripts/verify.py`; identify the delivery revision using `git log -1 -- conformance/uc003/test_runtime.py`.

Actual changes: Wallet 0.3.0 adds generic source ownership and grants through two additive tables; the new Synthetic Sensor Connector 0.1.0 owns observation storage, membership and release records. Client/bootstrap and optional transport dispatch include the new contract. Local Folder Connector, Processing, Knowledge, Workflow and Registry implementation sources remain unchanged. The UC-002 runner advertises the upgraded Wallet version.

The composition retains the existing Local Folder Connector to satisfy Wallet's document dependency; only Wallet and Sensor participate in source reads. Splitting optional readiness dependencies can be considered later. No new family is introduced.

Release records are committed before the response and identify exact authorised output, not proof of receipt or downstream consumption. Earlier resources and grants survive the additive Wallet upgrade. No physical hardware, signed audit trail or production deployment claim follows from these results.
