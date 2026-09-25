# UC-009 — connected sources and managed items

Runnable synthetic macOS slice: one source permission covers a local folder of email exports; explicit admission creates an immutable copy governed individually by Wallet. No real email account is accessed.

From the repository root:

```sh
.venv/bin/python solutions/managed-items/uc009/run.py demo
.venv/bin/python solutions/managed-items/uc009/run.py launch
```

`demo` exercises both boundaries, restart and authority failure, then stops its two services. `launch` seeds two external emails and one managed item and opens no browser automatically: follow the printed private local URL to the read-only monitor. It shows Wallet and Connector counts/dependencies; admission is currently an API action, not an interactive upload screen. Ctrl-C stops the owned services. Both commands use disposable synthetic state and fresh development identities. A busy default dashboard port falls back to a free port; `--port 0` requests one explicitly.

## Observable result

1. Register and attach one source; one reader grant lists and reads both synthetic emails.
2. The owner selects an exact digest and admits one copy, recording source/owner/entry, title, classification, permitted readers and admission time.
3. A separate exact-version item grant reads the copy. Source and item grants cannot substitute for each other; the inherited reader ceiling cannot be broadened.
4. Changing/deleting the original preserves the admitted version. A stale-digest new admission fails.
5. Revoking source access stops future source reads; revoking item access stops copy reads. Restart preserves both boundaries; an unavailable Wallet denies access.

See the [membership model and limitations](../../../docs/sources-and-managed-items.md) and [wire contract](../../../contracts/uc009/README.md).

## Module changes and continuity

Expected and actual affected families: Wallet and Connectors. Wallet adds opt-in admission metadata, durable request receipts and managed-item grant restrictions. The new Managed Folder implementation reuses the optional safe local-read and immutable-snapshot helpers. Registry's existing binding adapter selects `folder.capture`; its domain code is unchanged. Monitoring reuses UC-005's authenticated bridge without owner credentials. Processing, Knowledge, Workflow, Model access, Assistance and Exchange domain implementations are unchanged.

This is a separate composition; existing UC-001–008 keep their established contracts. Managed items deliberately reject legacy move/update and capability/export grants until those operations can preserve inherited conditions. Database additions are additive; no existing tables are rewritten. An admission key replays the historical owner receipt, including after source revocation; it neither rereads the source nor issues access.

## Evidence

Implementation revision: [f4703c4](https://github.com/cgrbxl/farmy/commit/f4703c4).

Verified on 2026-09-25 using macOS 26.6.2 arm64 and Python 3.14.6: all 114 selected tests and nine demos passed, including the installed local Qwen model and optional S3 HTTP double. The static walkthrough and live two-service monitor were checked in the browser.

Twelve real-process acceptance tests cover collective source access, explicit admission, grant separation, private/narrowed readers, independent revocation and source expiry, immutable copies, concurrent idempotency, owner-only metadata, caller identity, path/symlink/scope rejection, restart, fail-closed reads, blocked legacy mutation/export, descriptors and monitoring. Run:

```sh
.venv/bin/python -m unittest discover -s conformance/uc009 -v
.venv/bin/python scripts/verify.py --with-local-model --with-s3-fixture
```

The full selected verification includes 103 completed-baseline tests plus 11 pending UC-007 HTTP-double checks and nine demos when both optional prerequisites are available. Local fixture evidence does not establish real Scaleway compatibility. Windows, Linux and Kubernetes remain unverified for this composition.
