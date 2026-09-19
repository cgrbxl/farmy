# UC-003 runnable source-permission slice

Experimental synthetic macOS build. One source grant permits a consumer to read existing and newly appended observations. Another source stays inaccessible. This implements the direction in [ADR 0012](../../../docs/decisions/0012-source-permissions-and-wallet-complements.md).

## Run

From the Farmy repository root, using the same environment as the earlier demos:

```sh
.venv/bin/python solutions/sensor-path/uc003/run.py demo
```

For a new checkout:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r conformance/foundation/requirements.txt
.venv/bin/python solutions/sensor-path/uc003/run.py demo
```

The runner creates isolated synthetic state and development certificates, then prints five passing stages: one permission for existing/new observations; source and consumer isolation; traceable releases; restart persistence; and revocation/unavailable-authority denial. It stops its processes and removes temporary state afterward.

Three services run: Wallet, the existing Local Folder Connector, and the new Synthetic Sensor Connector. The sensor path itself uses Wallet and Sensor; the Local Folder Connector satisfies Wallet's existing document dependency without changing the old contract. There is no Processing, Knowledge or Workflow runtime in this composition. No physical device, model or cloud service is contacted.

## Independent startup

Bootstrap once into a new empty directory:

```sh
.venv/bin/python solutions/sensor-path/uc003/run.py bootstrap --directory .farmy/uc003
```

Start services in separate terminals using `--service wallet`, `--service connector` and `--service sensor`:

```sh
.venv/bin/python solutions/sensor-path/uc003/run.py serve --directory .farmy/uc003 --service wallet
```

The `request` command accepts `--operation`, `--payload`, `--identity`, `--grant`, `--key` and `--revision`. For example, register a source:

```sh
.venv/bin/python solutions/sensor-path/uc003/run.py request --directory .farmy/uc003 --operation source.register --payload '{"connectorId":"sensor.local"}' --key key.first-source
```

Use the returned source/owner IDs in subsequent payloads. The [contracts](../../../contracts/uc003/README.md) specify append/grant/read/revoke/audit operations; the runner contains a complete executable example.

Ctrl-C stops each service. Restarting with the same configuration preserves state. Certificates expire after two days; there is no rotation command, so use a new empty development directory after expiry. Once all three services are stopped, delete `.farmy/uc003` to remove its synthetic state and credentials. Partial state deletion and downgrade are not supported recovery procedures.

## Verification

```sh
.venv/bin/python scripts/verify.py
```

This runs all four slice suites, foundation checks, documentation checks and the original three demos. Add `--with-local-model` for the [UC-004 real-model demo](../../assisted-answer/uc004/README.md). Run only this slice's nine acceptance tests with:

```sh
.venv/bin/python -m unittest discover -s conformance/uc003 -v
```

Tests use real HTTPS processes and cover ongoing source permission, pagination, wrong source/owner/consumer/audience, retries/concurrent append, malformed requests, expiry/revocation, Wallet outage, restart, exact release records, denied audit access, corrupted membership, audit-storage failure and additive Wallet upgrade preserving prior document grants. Storage fault injection and duplicate-count inspection are test-only; services never share private database access.

Verified target: macOS arm64, Python 3.14.6, OpenSSL 3.6.3. To identify the delivery revision, run `git log -1 -- conformance/uc003/test_runtime.py`. Other platforms and real sensor-provider compatibility remain unverified.

## Scope and limits

- One configured owner, individually identified consumers and two or more separately registered sources. No recipient-group administration or per-observation approval.
- Only bounded synthetic temperature observations, immutable after append. No physical-device identity, high-volume streaming, offline operation, retention/deletion, source ownership transfer or rebinding.
- Grants cover all retained and future observations while active. Source read permission is distinct from document-version grants. Observation IDs/sequences support exact evidence without making observation-level policy decisions.
- Release records identify what Farmy authorised to leave the service. They do not establish confirmed receipt, downstream use or compliance with usage conditions. No watermarking is implemented.
- The trusted OS user can access unencrypted keys and state directly. Audit is durable local storage, not tamper-evident logging. Existing [development security limits](../../core/uc001/README.md) still apply. This is not a private-data or production deployment.

Wallet is now `0.3.0`; new source operations use `0.3-draft`. The Synthetic Sensor implementation is `0.1.0`. Earlier operation versions and Local Folder Connector source remain unchanged. Wallet adds source/grant tables and generic source policy logic; temperature rules live only in the new Connector. External wallet, assurance and usage-conditions work remain deferred.
