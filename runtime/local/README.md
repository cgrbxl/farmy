# Persistent local composition

Owns process lifecycle and configuration only. Reuses Wallet, directory Connector and interactive client contracts; no Farmy-hosted service is required. `farmy.py` is the lifecycle CLI; `guard.py` stops an owned module if its supervisor disappears.

Source workspace launch (development only):

```sh
.venv/bin/python runtime/local/farmy.py --home .farmy/local init --source docs/data_v2
.venv/bin/python runtime/local/farmy.py --home .farmy/local start
.venv/bin/python runtime/local/farmy.py --home .farmy/local status
.venv/bin/python runtime/local/farmy.py --home .farmy/local stop
```

For an installed application, use the [Mac release profile](../../deployments/profiles/macos/README.md). The [deployment plan](../../docs/deployment-plan.md) records local independence and optional Scaleway hosting.

### 0.2.0 local identities and consumer

The consumer now runs separately on the next loopback port (normally 54801), with its own browser link and receipt store. Both ports must be available. Owner-only actions are refused on the consumer endpoint, and consumer credentials are refused on the owner endpoint. Persistent P-256 keys and pinned fingerprints live under `identities/owner`, `identities/reader` and `identities/pairing.json`; consumer receipts live in `state-reader`. Stopped backups include these directories. Keep backups private because they contain private keys. See [identity and sharing](../../docs/identity-and-sharing.md).

### 0.3.0 messaging drafts

The supervisor ticks the embedded draft-only Workflow planner once per second while running. It owns `state-messaging`, included in stopped backups/restores. Scheduler/storage errors stop the composition rather than claim success. See [messaging](../../docs/messaging.md) for retention, time semantics and explicit no-delivery boundaries.
