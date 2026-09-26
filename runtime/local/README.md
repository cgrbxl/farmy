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
