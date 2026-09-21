# UC-008 composition profile — Knowledge replacement

This slice adds no public operation or schema version. It composes [foundation bindings/descriptors](../v0.1-draft/README.md), [UC-002 operations](../uc002/README.md) and [UC-005 summaries](../uc005/README.md).

A Knowledge binding selects `farmy.knowledge`, exact contract `0.2-draft`, `evidence.index` and `evidence.query`. The configured endpoint and certificate fingerprint are operator-controlled. Admission checks authenticated instance identity, endpoint, environment, implementation/version consistency, security/connectivity profile, local target declaration, operations and required features. Declarations do not prove semantics; the [acceptance suite](../../conformance/uc008/test_runtime.py) supplies bounded runtime evidence. Admission is currently macOS/direct-HTTPS only.

Workflow captures the entire binding in the durable request digest. Changing instance, binding revision or requirements with the same job key produces `conflict`; a new job key explicitly requests new work. A running process holds its startup binding. A query client resolves its binding per query; a missing or wrong audience grant is still denied by the receiver and Wallet.

Replacement retains an explicitly trusted enrolled instance identity, starts a new implementation-owned store, and rebuilds through Processing's current authorised proposal API. There is no database migration contract, automatic replay, state portability guarantee, grant transfer between identities, dynamic discovery or cross-environment admission in this profile.
