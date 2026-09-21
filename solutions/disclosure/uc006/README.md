# UC-006 — Preview, approve and deliver

Status: runnable synthetic macOS development slice. Three Farmy services (Wallet, Local Folder Connector and Exchange) plus one separate synthetic recipient communicate over mutually authenticated TLS. Each owns its SQLite state. Registry remains a binding-file adapter. No cloud account, external customer or AI service is contacted.

## Run the demonstration

From the repository root, with the existing Python environment and OpenSSL prerequisites from [UC-001](../../core/uc001/README.md):

```sh
.venv/bin/python solutions/disclosure/uc006/run.py demo
```

The runner creates temporary identities/state, prints the exact preview, demonstrates rejection without approval/export authority and with changed content/recipient, interrupts delivery, restarts Exchange, recovers a stable receipt and demonstrates revocation/unavailable-authority denial. All four processes stop and temporary state is removed when the demo exits.

The included document is `Farmy synthetic record v1`. The recipient is a local fixture with its own process and persistence, not a real third-party service. Demo approval is automatic for this synthetic document; interactive browser approval remains future work.

## Inspect the running slice

```sh
.venv/bin/python solutions/disclosure/uc006/run.py launch
```

This starts and seeds the four processes, then opens a read-only monitoring bridge through the access link printed in the terminal. Open that link yourself. The bridge prefers port 8766 and falls back to a free port if occupied; `--port 0` explicitly chooses a free port. Ctrl-C stops the runner and its owned processes; closing the browser does not.

Select **Controlled Exchange** to see prepared, approved, acknowledged and unconfirmed disclosure counts and recent audit outcomes. This composition monitors Wallet, Connector and Exchange; the synthetic recipient appears as a declared dependency outside the monitored inventory. Other families are not deployed in this small composition. No raw document bytes or signing authority enter the monitoring browser.

## Independent processes and command-line operations

```sh
.venv/bin/python solutions/disclosure/uc006/run.py bootstrap --directory .farmy/uc006
```

Run each service in a separate terminal:

```sh
.venv/bin/python solutions/disclosure/uc006/run.py serve --directory .farmy/uc006 --service wallet.local
.venv/bin/python solutions/disclosure/uc006/run.py serve --directory .farmy/uc006 --service connector.local
.venv/bin/python solutions/disclosure/uc006/run.py serve --directory .farmy/uc006 --service exchange.local
.venv/bin/python solutions/disclosure/uc006/run.py serve --directory .farmy/uc006 --service recipient.local
```

Then seed a synthetic approved transfer and inspect it:

```sh
.venv/bin/python solutions/disclosure/uc006/run.py seed --directory .farmy/uc006
.venv/bin/python solutions/disclosure/uc006/run.py dashboard --directory .farmy/uc006
```

The independent bridge does not own or stop those services. Stop each service with Ctrl-C. Bootstrap requires an empty directory and never overwrites existing state. Development certificates expire after two days; rebootstrap into a fresh empty directory for a fresh run. No certificate rotation or state migration tool is supplied.

For individual operations, `request --directory … --operation … --payload '{…}' --refs '[…]' --grant … --key …` calls Exchange (or the fixture for receipt operations). Use the [contract](../../../contracts/uc006/README.md) for exact fields. Resource registration and Wallet grant issuance remain available through UC-001's `request` command against the same directory. The Python functions in [run.py](run.py) give a complete prepare → approve → deliver example through public APIs; no direct database editing is needed.

## Verification and limits

```sh
.venv/bin/python -m unittest discover -s conformance/uc006 -v
.venv/bin/python scripts/verify.py --with-local-model
```

Fourteen new checks exercise exact bytes, immutable manifests, separate grants, actor identity, revoked authority, service outages, recipient acknowledgement loss, concurrent duplicates, restart, version preservation, expiry, size limits and authorised monitoring. Repository total: 80 tests (19 foundation + 61 slice checks). The full runner includes six demos with the model flag, or five without the local-model prerequisite.

Verified on 2026-09-21: macOS 26.6.2 arm64 / Python 3.14.6. All 80 checks and six demos passed, including installed Qwen through Ollama. Browser inspection confirmed the three-node live inventory, Exchange counts/activity and project walkthrough. Windows, Linux, Kubernetes and Scaleway remain unverified. Local state and keys are unencrypted development material with restrictive permissions. This is a 16 KiB exact-document export profile, not generic large-file streaming, production custody, remote recipient compatibility, document credential issuance or a writable dashboard. The lost-acknowledgement fault switch exists only in the synthetic recipient fixture.

Implementation revision: [`403577c`](https://github.com/cgrbxl/farmy/commit/403577c).

See the [use-case evidence and module impact](../use-cases/UC-006-controlled-disclosure.md). A recipient receipt records acceptance of exact bytes; it does not promise control over later copies or usage.
