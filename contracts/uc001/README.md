# UC-001 operation contract — experimental

Version `0.1-draft`, implementation `0.1.0`. [OpenAPI 3.1](openapi.json) describes operation routes; [JSON Schema](operations.schema.json) supplies strict input/output shapes. POST `/farmy/v0/<operation>` uses the [foundation request envelope](../v0.1-draft/foundation.schema.json). The payload schema URI is `urn:farmy:uc001:<operation>.input`; JSON results use the corresponding `.output` URI. Unknown fields are rejected. This is a narrow use-case contract, not the full API for each family.

| Service / operation | Authority and semantics |
| --- | --- |
| Wallet / `resource.register` | Enrolled owner, bootstrap management policy; capture a relative `path`, create stable resource ID and first immutable version |
| Wallet / `resource.inspect` | Owner only; return current version, digest, size, location and revision |
| Wallet / `resource.move` | Owner; exact current input reference and expected revision; capture new path and require identical digest, retain resource/version, increment revision. Caller relocates the source first. |
| Wallet / `resource.update` | Owner; exact current input reference and expected revision; capture current path, create new version when bytes differ, retain resource ID. Identical bytes are a no-op. |
| Wallet / `grant.issue` | Owner; exact input reference matching payload; grant an enrolled subject read access to that resource/version for `uc001.read`, up to one hour, pinned to Connector and binding revision |
| Wallet / `grant.revoke` | Owner; grant ID and expected grant revision; revoke and increment revision |
| Wallet / `authorize.read` | Connector only, authenticated on its service certificate; check forwarded subject and exact input reference against current grant state; return snapshot metadata only if allowed |
| Connector / `snapshot.capture` | Wallet only, forwarding owner under its explicit capture policy; bounded approved-root read and immutable digest-addressed snapshot |
| Connector / `read.version` | Enrolled caller must equal subject; exactly one input reference, explicit scoped grant, online Wallet approval; binary bytes with version and SHA-256 headers |

`farmy.wallet` covers the six Wallet management operations, `farmy.authorization` covers authorisation, and `farmy.storage` covers Connector operations. Each uses exact version `0.1-draft`. Capture/management purpose is `uc001.manage`; reads/authorisation use `uc001.read`. The authenticated actor must match the request. The target and wallet must match configuration. Deadlines must be in the next 60 seconds; clients default to 20 seconds and a three-second socket timeout.

Management uses `grant.owner-bootstrap`, enforced only for the enrolled owner. Wallet-to-Connector capture uses `grant.wallet-capture`, enforced only for the enrolled Wallet forwarding that owner. These names alone convey no authority. Resource read grants are random Wallet-managed IDs; none permit management operations or other versions.

Mutations require an idempotency key. Scope is actor + operation + key. Wallet atomically records successful results with its state changes. Retrying identical logical inputs returns the original result; differing payload, reference, revision, subject, purpose, grant or binding revision conflicts. A failed request has no accepted result. Capturing before a failed Wallet transaction may leave an unreferenced snapshot; garbage collection is deferred. This does not promise distributed exactly-once execution.

JSON success and errors for structurally valid requests use foundation response envelopes. Errors have no result/output references. Invalid envelopes and pre-request authentication failures receive only a generic `error` object; TLS rejection can occur before HTTP. Codes map to HTTP 400 invalid request, 401 unauthenticated, 403 denied, 404 not found, 409 conflict, 408 expired, 422 unsupported, 503 unavailable and 500 internal. Dependency readiness failure returns HTTP 503 with `status: degraded`. Binary read success is HTTP 200 `application/octet-stream`, at most 1 MiB, with `X-Farmy-SHA256` and `X-Farmy-Version`; clients verify both. Binary transfer is a UC-001 transport extension, not a foundation JSON response.

Operator-only GET routes: `/farmy/v0/health/live`, `/farmy/v0/health/ready`, `/farmy/v0/descriptor`. Descriptor returns an object containing foundation `module` and `instance` records. Instance status is registration state; live readiness is queried separately. Liveness checks no dependency; readiness checks the peer's liveness, avoiding recursion. These development management routes are described here, outside the operation-only OpenAPI file.

The [runner](../../solutions/core/uc001/README.md) and [tests](../../conformance/uc001/test_runtime.py) are executable usage examples. Equivalent clients can be written in other languages without the optional Python helper.
