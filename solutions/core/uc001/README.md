# UC-001 runnable local slice

Experimental, synthetic-data development build. Verified on macOS arm64 with Python 3.14.6 and OpenSSL 3.6.3. Windows, Linux and Kubernetes packages are not provided or verified. Python 3.11+ and an OpenSSL CLI supporting EC certificates are prerequisites; other versions are untested.

## Run the demonstration

From the repository root, install the pinned Python dependencies once:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r conformance/foundation/requirements.txt
```

Run:

```sh
.venv/bin/python solutions/core/uc001/run.py demo
```

The runner creates temporary synthetic files and development certificates, starts two separate loopback HTTPS processes, demonstrates register/read/move/update/restart/revoke and unavailable-authority rejection, then stops its own processes and removes its temporary state. Success prints five `PASS` lines and `Demo complete`. It neither reads personal folders nor provisions cloud resources. Local listening ports must be permitted by the execution environment.

## Start the modules independently

Create a fresh, private development directory; bootstrap refuses a nonempty directory:

```sh
.venv/bin/python solutions/core/uc001/run.py bootstrap --directory .farmy/uc001
```

In separate terminals, from the repository root:

```sh
.venv/bin/python solutions/core/uc001/run.py serve --directory .farmy/uc001 --service wallet
```

```sh
.venv/bin/python solutions/core/uc001/run.py serve --directory .farmy/uc001 --service connector
```

Use a third terminal to register the fixture:

```sh
.venv/bin/python solutions/core/uc001/run.py request --directory .farmy/uc001 --operation resource.register --payload '{"path":"record.txt"}' --key key.first-registration
```

This prints the resource/version IDs and revision. Repeating that command returns the same registration. The CLI also accepts `--identity`, `--refs` (a JSON array), `--grant` and `--revision`; payloads and permission semantics are in the [operation contract](../../../contracts/uc001/README.md). The automated demo provides a complete client example.

Stop each service with Ctrl-C. Restart with the same command to retain its state. Each service owns its own SQLite database and audit table; only the Connector owns content snapshots. The Registry contribution is a revisioned configuration-file binding adapter, not a running catalogue service. No module opens another module's database.

Bootstrap certificates expire after two days. There is no credential rotation or state migration tool yet: use a new empty development directory for a fresh fixture. After both services are stopped, the `.farmy/uc001` directory can be deleted to discard all synthetic content, history, grants and keys. Preserve the entire directory if you want to rerun within the certificate lifetime; partial state deletion is not a supported recovery procedure. No crash/power-loss recovery claim is made.

## Verify

```sh
.venv/bin/python -m unittest discover -s conformance/uc001 -v
.venv/bin/python -m unittest discover -s conformance/foundation -v
.venv/bin/python conformance/foundation/check.py
python3 scripts/check_docs.py
```

The eight runtime tests cover actual HTTPS requests, separate process restarts, exact version history, duplicate/conflicting operations, stale revisions, permission scope/revocation/expiry, caller impersonation, missing and unenrolled certificates, wrong server pin, traversal/symlinks, size limits, source mutation during capture, corrupt snapshots, and missing dependencies. One deterministic capture-race test injects a source change during a real file read. The rest exercise running services. These are slice acceptance checks, not a security audit or universal platform certification.

## Limits

- Mutual TLS 1.3 verifies the development CA; exact enrolled certificate fingerprints identify peers and pin service endpoints. The Wallet authenticates its owner management policy separately from content-read grants. Grant IDs are references, not bearer credentials.
- Each read requires online Wallet approval for the caller, exact resource/version, connector audience, purpose, expiry and binding revision. The Connector checks again before returning bytes. A revocation cannot recall bytes already delivered or cancel a response already authorised and in flight.
- Source paths stay beneath an approved root with symlinks rejected. Capturing reads twice and checks file metadata, rejecting observed concurrent changes. This is not a filesystem snapshot transaction against a malicious concurrent writer.
- Files and private keys use local filesystem permissions; snapshots/databases are not encrypted at rest. All processes run as the same OS user, who can read or alter state and credentials directly. This proves service boundaries, not isolation from that user or a compromised host. Use synthetic data only.
- The Python development server has bounded requests/timeouts but no production availability hardening. Bodies are limited to 64 KiB and snapshots to 1 MiB. Snapshot retention, grant/idempotency/audit growth and garbage collection are unbounded across requests.
- Identities, one wallet, one connector and their delegation rules are intentionally fixed for UC-001. Live trust reload, certificate rotation/revocation, multi-tenant identity, deployment installers, cloud networking and cross-provider portability remain future work. Ports are assigned during bootstrap; a later collision fails startup instead of stopping another process.

See [ADR 0010](../../../docs/decisions/0010-uc001-local-runtime.md) and the [acceptance case](../use-cases/UC-001-controlled-memory.md).
