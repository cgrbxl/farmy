# Conformance and composition tests

Status: [foundation document/compatibility checks](foundation/README.md) are executable. [UC-001 runtime acceptance tests](uc001/test_runtime.py) exercise the synthetic macOS slice; broader security, operation and deployment conformance remain a test plan. [UC-002 tests](uc002/test_runtime.py) add extraction, disclosure, duplicate/recovery and Wallet upgrade checks. [UC-003 tests](uc003/test_runtime.py) add source permissions, immutable observation membership and release auditing. [UC-004 tests](uc004/test_runtime.py) add model-route denial, citation validation, independent grants and uncertain-invocation recovery. [UC-005 tests](uc005/test_runtime.py) cover authorised monitoring and independent UI lifecycle. [UC-006 tests](uc006/test_runtime.py) cover exact approved export, separate authority and receipt recovery. Run all 91 checks and seven demos with `.venv/bin/python scripts/verify.py --with-local-model`; see [model prerequisites](../solutions/assisted-answer/uc004/README.md). Omit the flag for all tests and the six model-independent demos, without a real-model dependency. The separate repository documentation script checks Markdown links and JSON parsing only.

| Layer | Required evidence |
| --- | --- |
| Contract | Valid/invalid fixtures, version/features negotiation, data semantics and structured errors |
| Security | Unknown identity, wrong wallet/audience, expired/revoked grants, forbidden delegation/egress and sensitive-data leakage denied |
| Module lifecycle | Duplicate jobs, partial failure, retry/cancellation, restart, migration, backup/restore and removal semantics |
| Composition | Synthetic core/document cases and independently implemented provider replacement while unaffected modules keep their versions |
| Deployment | Installation and controls verified for each claimed OS/architecture or Kubernetes/provider profile |

Create fixtures and tests alongside the first accepted contracts and module implementation; avoid tests that merely mirror a private implementation. An independently implemented provider must be able to run the suite without a shared database or mandatory Farmy SDK. Reference code is subject to the same tests.

Organise executable tests by versioned public contract/profile when those exist. Keep test data synthetic and expected results explicit. Attach results to exact implementation, contract, solution and deployment-profile versions; passing one layer does not imply the others pass.

Use [modularity change scenarios](../docs/module-architecture.md), [integration requirements](../docs/module-integration.md) and [security requirements](../docs/security.md). The initial [document recipe](../solutions/document-path/README.md) is the first composition target.

Optional in-progress [UC-007 checks](uc007/test_runtime.py) require [S3 dependencies](../modules/connectors/s3/requirements.txt). Add `--with-s3-fixture` to the verification runner for 11 additional local HTTP-double checks and one demonstration (91 total checks; seven demos with both optional flags). These do not establish real Scaleway compatibility.

## UC-008 Knowledge replacement

Run `.venv/bin/python -m unittest discover -s conformance/uc008 -v`. Eleven tests exercise two domain implementations, target-specific authority, descriptor mismatch, exact-source evidence, concurrent idempotency, restart, outage, job-binding conflicts and explicit replacement/rebuild. See [scope and evidence](../solutions/replacement/uc008/README.md). The default aggregate verification now includes 91 tests and six demos; `--with-local-model` adds a seventh demo. `--with-s3-fixture` adds eleven HTTP-double checks and an additional demo (102 tests total), without claiming real-provider validation.

[UC-009](../solutions/managed-items/uc009/README.md) adds twelve real-process checks for source/item boundaries, admission, policy narrowing, idempotency and recovery.
