# UC-002 — Extract and retrieve exact-source evidence

Status: done for the synthetic macOS development scope, verified 2026-09-19. Owner: Carlos.

## Outcome and fixture

The owner registers `Farmy synthetic report\ncrop: wheat\n`, authorises a fixed extraction/indexing workflow and retrieves `crop = wheat` as a permitted reader. The result cites the exact source version/digest, quoted line and byte offsets. Repeated execution produces one accepted derived index entry. A later report with `crop: barley` produces evidence for its new version while the original remains identifiable.

No PDF/OCR/model, authoritative farm-record acceptance, semantic search, export, external provider, cloud packaging or cross-platform support is included. The derived index is not a second resource authority.

## Module map and expected changes

Wallet keeps source identities and adds generic scoped service permissions. Connector continues serving exact snapshots without source changes. Processing owns the bounded text-field parser/proposals. Workflow owns two-step job state and recovery, with no crop logic. Knowledge owns derived evidence and permission-checked retrieval. Explicit bootstrap configuration enrolls the three new services; no Registry server is needed.

The optional transport learns the new versioned contracts; its existing envelope and UC-001 APIs remain compatible. Shared local persistence helpers contain no module domain schema or parser logic. Each service has separate startup and state.

## Acceptance

- Exact value, source/version/digest and UTF-8 quote offsets; unknown and denied readers get no evidence.
- Duplicate, concurrent and redelivered jobs converge on one accepted entry; altered inputs with the same key conflict.
- Changed source creates independently addressable evidence; an old grant cannot disclose the new version.
- Independent source, transfer, indexing and query grants are enforced; expired/revoked/wrong-subject/wrong-audience/wrong-wallet requests fail.
- Revoked query permission suppresses retained evidence; unavailable authority never bypasses checks.
- Missing/duplicate/invalid fields and oversized/invalid UTF-8 reports fail without indexing partial results.
- Workflow restart after extraction resumes indexing; lost step acknowledgements can be retried without duplicate acceptance.
- Restart retains proposals/jobs/evidence; additive Wallet upgrade preserves UC-001 resources and grants.
- UC-001 regression suite continues passing; no Connector source change is required.

See [contracts](../../../contracts/uc002/README.md), [run instructions](../uc002/README.md) and [acceptance tests](../../../conformance/uc002/test_runtime.py). Record actual results at completion; identify the delivery revision with `git log -1 -- conformance/uc002/test_runtime.py`.

## Delivery evidence and actual changes

Verified on macOS arm64, Python 3.14.6, OpenSSL 3.6.3: nine UC-002 tests, eight UC-001 regression tests, 19 foundation tests, both five-stage demos and structural/documentation checks passed via `.venv/bin/python scripts/verify.py`.

Actual changes match the predicted boundaries: three new service implementations, generic Wallet permissions/read-subject configuration, optional shared transport/state helpers, and reusable bootstrap configuration. Connector and Registry implementation source remained unchanged. Wallet gains an additive table; the existing-state upgrade test verifies resources and grants are preserved. No existing development directory is silently enrolled into UC-002.

The next queued outcome is a source-cited answer through an explicitly selected model, with denied egress tested. No model integration has been selected or provisioned by this slice.
