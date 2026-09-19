# UC-005: live installation dashboard

Status: experimental synthetic macOS slice. This operational view is separate from the [project guide](../../../dashboard/README.md), which describes architecture and delivery progress. The operational UI lives in [dashboard/live](../../../dashboard/live/index.html) and requires its local API bridge; opening that HTML as a standalone file is unsupported.

## Launch

Use the Python/OpenSSL prerequisites from [UC-001](../../core/uc001/README.md), then run from the repository root:

```sh
.venv/bin/python solutions/operations/uc005/run.py launch
```

Open the **access link printed by the runner**, normally on port 8766. The link carries a random local metadata-access token in its fragment; it is not sent in HTTP URLs or committed. The browser removes the fragment and retains the key in that tab's session storage. Reopening a different browser/tab may require the access link again. Each new bootstrap creates a different key. Do not share the access link.

The launcher starts eight Farmy processes and a separate read-only browser bridge, seeds a document, evidence, a completed job, one source and three observations, and remains running. Closing the page leaves services running. Ctrl-C in this all-in-one runner stops its owned services and removes temporary synthetic state. Existing external services remain untouched.

To also populate a validated local-model answer, use the [UC-004 Ollama/Qwen prerequisites](../../assisted-answer/uc004/README.md):

```sh
.venv/bin/python solutions/operations/uc005/run.py launch --with-local-model
```

Without the flag, Model access and Assistance still run but their invocation/answer counts start at zero. The dashboard never triggers inference. It does not probe Ollama health or model quality. Use `--port 8767` if 8766 is occupied. The optional Project guide link expects the separate static guide on port 8765.

## What you can inspect

- Instance names, family, version and configured endpoint.
- Authenticated bridge-to-service reachability and service readiness results.
- Service-declared dependency arrows, explicitly not measured traffic or verified end-to-end connectivity.
- Counts of documents/versions/sources, observations, evidence, jobs, model invocations and accepted answers.
- At most six recent service outcomes with timestamps, without raw content or identities.
- Summary-denied, degraded, unavailable and stale states. Failed reads never turn into zero-count claims or preserve old counts as fresh.

Select a diagram node or inventory row to inspect it. Automatic refresh runs every ten seconds while visible; manual refresh remains available. Counts can be internally consistent per service but are not a global transaction. Retained grants include revoked/expired records. Unresolved work may be pending, interrupted or uncertain, not necessarily failed.

## Independent lifecycle

To keep modules separate from the browser bridge and retain synthetic state:

```sh
.venv/bin/python solutions/operations/uc005/run.py bootstrap --directory .farmy/uc005
.venv/bin/python solutions/operations/uc005/run.py serve --directory .farmy/uc005 --service wallet.local
```

Run `serve` in separate terminals for `connector.local`, `sensor.local`, `processing.local`, `knowledge.local`, `workflow.local`, `model.local` and `assistance.local`. Seed once, then start only the UI bridge:

```sh
.venv/bin/python solutions/operations/uc005/run.py seed --directory .farmy/uc005
.venv/bin/python solutions/operations/uc005/run.py dashboard --directory .farmy/uc005
```

Stopping this `dashboard` process leaves modules alive. Restarting it reuses its bootstrap key. Seed is explicit fixture creation, not an idempotent migration; repeating it adds another document/source. Bootstrap requires an empty directory and never overwrites existing state. Local credentials expire after two days; generate a fresh installation afterwards. Do not reuse this synthetic profile for private farm data.

## Verify

```sh
.venv/bin/python -m unittest discover -s conformance/uc005 -v
.venv/bin/python solutions/operations/uc005/run.py demo
.venv/bin/python scripts/verify.py --with-local-model
```

Nine UC-005 tests verify real contents, receiver-enforced monitoring policy, a monitor unable to mutate/read raw data, browser token/Host/Origin restrictions, static-file containment, outages/recovery, access removal, fresh counts and independent bridge shutdown. The last command retains all earlier checks and runs all five demos with local Qwen. Without its model flag, the verification runner executes all suites and four demos without requiring Ollama.

Implementation revision: [`47ff0f2`](https://github.com/cgrbxl/farmy/commit/47ff0f2). Tested on macOS 26.6.2 arm64 / Python 3.14.6. The completed baseline contains 64 tests (19 foundation + 45 slice tests). This is not Windows/Linux/Kubernetes validation.

## Security and module impact

The bridge uses its own `monitor.local` certificate, not the owner's credentials. Its configuration contains only that identity's transport credentials, a fixed endpoint inventory and the browser key. Services explicitly admit it to metadata summaries. The bridge cannot access service databases or raw content through its public API. The trusted same-host user can still access all development files; this is not OS-level isolation or encrypted-at-rest storage.

This cross-cutting capability intentionally adds a summary method to each of the eight implementations, plus a shared optional formatting helper and authenticated GET dispatch. Each implementation defines its own queries; no central component interprets another module's schema. There are no table changes or migrations. UC-005 reports Wallet 0.4.0 and other reference implementations 0.1.1 with monitoring enabled; older compositions remain monitoring-disabled and preserve their prior declared profiles. Domain operations and contract versions are unchanged. The UC-004 composition bootstrap gains an optional service-list argument to reuse its existing setup.

Monitoring access is a trusted bootstrap allowlist, removed by configuration/restart. Multi-tenant dashboards, live access administration, remote HTTP, production sessions/SSO, fleet discovery, historical metrics, alerts and detailed content inspection remain future work. See the [monitoring contract](../../../contracts/uc005/README.md) and [use-case evidence](../use-cases/UC-005-operational-dashboard.md).
