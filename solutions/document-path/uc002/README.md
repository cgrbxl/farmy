# UC-002 runnable document-to-evidence slice

Experimental synthetic macOS build. Five separate services demonstrate the first extraction/retrieval path: Wallet, unchanged Local Folder Connector, Processing, Workflow and Knowledge. No model, cloud service or private farm data is used.

## Run

Use the same Python environment as [UC-001](../../core/uc001/README.md). From the repository root:

```sh
.venv/bin/python solutions/document-path/uc002/run.py demo
```

If the environment does not exist yet:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r conformance/foundation/requirements.txt
.venv/bin/python solutions/document-path/uc002/run.py demo
```

The demo bootstraps its own temporary source, credentials and five state directories, starts all services and prints five passing stages:

1. Extract `crop = wheat`, tied to the exact source version, SHA-256 and quoted byte range.
2. Repeat jobs and converge on one accepted derived evidence entry.
3. Restart the new services and retain their state.
4. Interrupt indexing, restart Workflow, then resume the job successfully.
5. Reject denied/revoked readers and refuse disclosure when Wallet is unavailable.

It stops its own processes and removes temporary files when finished. Local listening ports must be permitted. Verification was performed on macOS arm64, Python 3.14.6 and OpenSSL 3.6.3. Other platforms and dependency versions remain unverified.

## Independently run each module

Create a fresh synthetic setup:

```sh
.venv/bin/python solutions/document-path/uc002/run.py bootstrap --directory .farmy/uc002
```

Start each service in its own terminal, using one of `wallet`, `connector`, `processing`, `workflow`, `knowledge`:

```sh
.venv/bin/python solutions/document-path/uc002/run.py serve --directory .farmy/uc002 --service wallet
```

Repeat with the other four service names. Ctrl-C stops that service; the same startup command retains its state. The `request` subcommand accepts `--operation`, `--payload`, `--refs`, `--identity`, `--grant`, `--revision` and `--key`. Registration uses the existing Wallet API:

```sh
.venv/bin/python solutions/document-path/uc002/run.py request --directory .farmy/uc002 --operation resource.register --payload '{"path":"report.txt"}' --key key.report
```

The result supplies the IDs for subsequent requests. [Contracts and grant flow](../../../contracts/uc002/README.md) define their payloads; the runner's `permissions`, `demo` and `query` functions provide a complete executable client example. A UI and one-command persistent orchestration are not included.

Certificates expire after two days. Use a new empty development directory after expiry; there is no credential rotation command. After all five services are stopped, delete `.farmy/uc002` to discard its synthetic state and credentials. Do not partially reset a service while expecting cross-service history to remain coherent.

## Verify and inspect

```sh
.venv/bin/python scripts/verify.py
```

This runs the 19 foundation tests, eight UC-001 tests, nine UC-002 tests, nine UC-003 tests, structural fixture checks, documentation checks and all three demos. Individual new acceptance tests:

```sh
.venv/bin/python -m unittest discover -s conformance/uc002 -v
```

Tests exercise real HTTPS boundaries, concurrent duplicate submissions, exact version history, revoked/expired/mis-scoped grants, denied transfer/indexing, malformed text, persisted restart state, additive Wallet upgrade, interrupted indexing and redelivery after an accepted response is treated as lost. The lost-response case pre-delivers steps over the public API; it is not a network fault injector or proof for every crash timing.

For the source revision use `git log -1 -- conformance/uc002/test_runtime.py`. No provider substitution or cross-platform claim follows from these tests.

## Boundaries and limits

- Processing alone understands the `crop` line. Knowledge owns the derived index; Workflow records the fixed two-step job; Wallet only checks generic permissions. No service opens another service's database.
- Evidence is an accepted derived index entry, not an authoritative Wallet farm fact. Knowledge fetches it from authenticated Processing; it does not accept caller-supplied replacement values. Parser provenance is not proof of agronomic truth.
- Source read, proposal disclosure, indexing and reader disclosure have separate grants. Revoke the query grant to suppress retained evidence; revoking raw-source access alone does not revoke independent derived-copy grants. Online Wallet checks gate disclosures, including cached results.
- Input is UTF-8 text up to 16 KiB with exactly one valid `crop` line. One extractor and one evidence entry per exact source version are supported. No PDF/OCR, broad search, deletion/rebuild API, multiple-field index, model invocation or export exists yet.
- A retry resumes a saved job phase; there is no automatic retry daemon. Only one job executes at a time per Workflow process. Processing/index calls can repeat; uniqueness prevents duplicate accepted entries. Grant expiry can block recovery until the owner submits a newly authorised job.
- Retained proposals/evidence/jobs/audit have no garbage collection. Keys and state remain unencrypted under one trusted OS user; that user or a compromised service host can bypass these development boundaries. No production availability or power-loss recovery is promised. The [UC-001 limitations](../../core/uc001/README.md) still apply.

## Changes and continuity

Processing, Knowledge and Workflow are new implementations at `0.1.0`. Wallet becomes `0.2.0`, adding generic permissions and configured service read subjects. Its upgrade only creates an additional table: previous resources/versions/grants are preserved and covered by an upgrade test. UC-001 Connector source and its `0.1.0` implementation version are unchanged. Existing wire operations remain `0.1-draft`; new ones use `0.2-draft`. The common foundation envelope is unchanged.

The optional transport now dispatches both operation contract sets. The development bootstrap is reused with an explicit service list. UC-002 requires fresh bootstrap configuration to enroll its services; it does not silently add trust to an existing UC-001 directory. Downgrading Wallet after issuing new permissions is unsupported. The endpoint set and composition revision are operator-owned configuration, not a dynamic Registry.

See [use-case evidence](../use-cases/UC-002-exact-source-evidence.md) and [ADR 0011](../../../docs/decisions/0011-exact-source-derived-evidence.md).
