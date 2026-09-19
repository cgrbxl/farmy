# UC-005 — Read-only operational summaries

Experimental monitoring contract `0.5-draft`. Each service optionally exposes `GET /farmy/v0/monitor/summary` over its existing mutually authenticated TLS boundary. The [OpenAPI declaration](openapi.json) documents the route. The response follows [monitoring.schema.json](monitoring.schema.json). This is an operator GET interface like health/descriptor, not a content operation in the common POST envelope. POST `monitor.summary` is unsupported.

The receiver requires the authenticated certificate identity to appear in its explicit `monitorSubjects` configuration. Earlier compositions have no such entry and deny this API. UC-005 enrolls `monitor.local` with summary and existing health/descriptor access only; it receives no raw-content or mutation grants. The owner and ordinary reader do not automatically gain summary access. This is an installation-level monitoring policy, not per-user farm-data authorisation. Removing the entry and restarting the receiver revokes summary access; live policy administration is not implemented.

The response includes instance ID, observation time, named integer counts, declared dependency instance IDs and at most six recent audit outcomes (`at`, `event`, `outcome`). It excludes filenames, source IDs, actors, source values, evidence text, prompts, answers, grant IDs, credentials and database paths. Counts are installation-wide metadata: access must remain restricted even though content is omitted. Retained grant counts include expired/revoked records and must not be read as active permissions.

Each module owns its summary queries. One service-local read transaction provides internally consistent counts and activity; the whole-installation snapshot is not an atomic cross-service transaction. The bridge calls public APIs and never reads another service's private database. Public descriptors advertise `farmy.monitoring` / `0.5-draft` only when monitoring is enabled.

## Module metrics

| Module | Summary |
| --- | --- |
| Wallet | Documents, immutable versions, sources and retained grant records |
| Local Folder | Snapshots and total snapshot bytes |
| Synthetic Sensor | Observations, sources with observations and release records |
| Processing | Extraction proposals |
| Knowledge | Evidence entries |
| Workflow | Total, succeeded and incomplete jobs |
| Model access | Total, validated and unresolved invocations |
| Assistance | Accepted answers |

Incomplete jobs and unresolved invocations are not automatically failed: they may be in flight, interrupted or awaiting explicit recovery. Registry is a binding-file adapter, not a running server. Exchange is not deployed. These two families are labelled separately, not given fabricated health checks.

## Browser bridge

The local bridge exposes only a fixed static asset allowlist and `GET /api/snapshot`. It aggregates configured service instances using its own mTLS certificate. It cannot choose targets from browser input, execute arbitrary operations, read file paths or issue grants. Its per-target connection timeout is three seconds; independent probes run concurrently. Summary failures remove counts/activity for that instance. A successful descriptor probe establishes monitor-to-service reachability/authentication; readiness is the service's existing dependency health check. Edges remain declared dependencies, never verified traffic. Ollama availability is not probed.

The browser API requires an unpredictable bootstrap token in the Authorization header, an exact loopback Host, and a matching Origin if supplied. No CORS, cookies or cross-origin access is enabled. Responses disable caching; CSP restricts scripts/assets and framing. The runner prints a local access link whose fragment the browser consumes into tab session storage and removes from the address bar. The token permits metadata access only, but should not be shared. Service keys stay behind the bridge. Plain HTTP is loopback-only development transport, not remote/dashboard authentication suitable for production.

The browser refreshes every ten seconds while visible, or manually. A bridge failure hides counts; snapshots older than 30 seconds are marked stale. The read-only bridge has no persistence or process-control API. Stopping it does not stop independently running modules.

See [solution instructions](../../solutions/operations/uc005/README.md) and [acceptance tests](../../conformance/uc005/test_runtime.py).
