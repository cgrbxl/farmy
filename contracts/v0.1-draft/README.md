# Minimum integration foundation — 0.1-draft

Status: executable document-shape and declared-compatibility validation. Network services, authentication, grant enforcement, capability-operation APIs and deployment packages are not implemented. This is a draft contract, not a stable standard or security certification.

## Three layers

1. **Common foundation:** identity references, descriptor, instance, binding, version references, request/result envelope and lifecycle/security semantics. This layer is shared by all nine families.
2. **Capability contracts:** actual operations, input/output payload schemas and semantics for a family specialisation. Add only the operations needed by a vertical use case.
3. **Environment mapping:** service startup, secret/trust resolution, state storage and network routes on macOS, Windows, Linux or Kubernetes/provider infrastructure. These mechanisms cannot redefine the first two layers.

An implementation is free to use another language or private storage design. It must own its state and communicate through these public boundaries, without direct access to another module's database. Multiple implementations/instances may coexist. FarmWallet remains authoritative for each wallet's resources and policies.

## Machine-readable documents

[foundation.schema.json](foundation.schema.json) uses [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12). Select the named `$defs` entry for a document; the root also accepts the public document forms. Use the bundled validator to enforce additional cross-document constraints.

| Definition | Purpose | Does not establish |
| --- | --- | --- |
| `module` | Implementation/release, family, capability versions/operations/features, dependencies, permission needs, target declarations and state portability | Publisher trust, verified support or automatic permissions |
| `instance` | Stable instance identity, implementation release, HTTPS endpoint, peer identity and environment | Trust merely because an endpoint advertises itself |
| `binding` | Exact instance/capability/version/operations/features selected for a wallet scope, with a revision | A grant, a deployment action or proof of readiness |
| `environment` | Target, common security/connectivity profile and references to platform trust, credentials, state, audit and allowed outbound endpoints | Provisioned infrastructure, secret values or complete provider configuration |
| `resourceRef` | Exact wallet/resource/version identity independent of physical location | Availability of bytes or permission to read them |
| `request` | Correlation, target/capability/operation, actor/subject, purpose/grant reference, deadline, inputs and typed payload reference | Authentication of the asserted actor or validation of a capability payload |
| `response` | Producer/release, request reference, outcome, input/output references and typed result or structured error | Correctness or authorised disclosure of a producer's claims |

Fields are closed for this draft to catch typos and undeclared extensions. IDs are opaque, case-sensitive identifiers; do not derive them from paths, personal data or endpoints. Versions must match exactly during the draft phase; no implicit major/minor compatibility is inferred. A changed contract requires a new advertised version and fixtures, including for additive fields that old strict validators reject. Implementation and contract versions are distinct.

Capability-specific `payloadSchema`/`resultSchema` identifiers are resolved from an approved, locally pinned contract set, never automatically downloaded from untrusted requests. Envelopes accept object payloads structurally; full validation MUST validate the actual operation schema and semantics too. The example payload identifiers are illustrative and deliberately have no operation schema yet. There is no generic “execute arbitrary payload” API.

The foundation represents one capability contract version per capability per descriptor; publish another descriptor/release profile rather than duplicate ambiguous entries. Target `tested` is a declaration needing separately attached evidence, not something this validator certifies. The module's dependency closure and implementation digests belong to a later resolved solution release; this check reports required dependencies as unresolved.

## Common communication outline

Use authenticated HTTPS and JSON for bounded metadata, with UTF-8 and exact contract/profile identifiers. Use separate authenticated streaming operations for file bytes; do not embed farm content in descriptors, grants, job queues or general logs. Resolve resource references through the owning authority and connector, never by passing another module a local filesystem path.

Proposed common endpoints for the first runtime:

| Endpoint | Semantics |
| --- | --- |
| `GET /farmy/v0/descriptor` | Authenticated installation client receives the module/instance descriptions; metadata may be sensitive |
| `GET /farmy/v0/health/live` | Authenticated monitor receives minimal process liveness, without farm data |
| `GET /farmy/v0/health/ready` | Authenticated monitor receives readiness/degraded status for declared dependencies, without secrets or source details |

These are the endpoint outline, not executable routes or a completed OpenAPI specification. Capability routes and their [OpenAPI](https://spec.openapis.org/oas/v3.1.1.html) definitions arrive with UC-001. Health access is an operator permission, not a wallet content grant. Lifecycle transitions include registered, ready, degraded, draining and stopped; each module must later implement graceful drain and bounded shutdown for operations it supports.

The initial request/response envelope covers synchronous outcomes only. Durable job IDs, accepted/pending results, polling and cancellation schemas are added with Workflow; do not encode a pending job as succeeded. Events, stream replay, cross-wallet requests and offline authority need explicit extensions.

Require request deadlines and bounded server limits; enforce actual expiry at runtime. UTC timestamps use RFC 3339 with `Z`. The static validator verifies syntax, not whether a request is still timely. Mutating operation contracts must require idempotency keys and expected revisions where applicable; the server derives mutation semantics from the registered operation, never from a caller-controlled flag. Retrying may not bypass reauthorisation.

Common error codes are invalid_request, unauthenticated, denied, not_found, conflict, unsupported, expired, unavailable and internal. Map them respectively to 400, 401, 403, 404, 409, 422, 408, 503 and 500 for the capability API unless its explicit contract refines the mapping. Avoid revealing existence or metadata to unauthorised callers; sanitise messages/input references and use a consistent denial policy. A retryable indicator never overrides deadlines, authority or side-effect reconciliation. Transport-level failures before a request envelope can be parsed may use a minimal HTTP error without pretending to have a validated request ID.

## Minimum service security profile

`farmy.mtls-online/0.1-draft` is a proposed runtime profile; the schemas only require its explicit declaration. It specifies:

- TLS with server and client certificate verification and a distinct instance identity. Trust is enrolled out of band through authorised configuration; no self-advertised trust roots, shared administrator key or automatic HTTPS downgrade.
- A configured binding from the verified certificate identity to the Farmy actor/instance. A claimed body `actorId`, `subjectId`, peer URI or grant reference cannot authenticate itself. Delegated subject authority must be verified with Wallet; absent valid delegation, deny impersonation.
- Online Wallet authorisation for the exact actor, initiating subject, wallet, resource/version, operation, purpose, receiver and permitted destination. Grant references identify authority but are not bearer secrets or independently sufficient proof. Each protected receiver enforces the decision before disclosure or effects.
- No positive-decision cache beyond the authorised operation in this initial profile. Deny protected work if the authority cannot be reached; recheck before disclosure/commit and at bounded checkpoints for longer work. Revocation cannot recall bytes already delivered.
- Separate service credentials from deployment credentials, resolve secrets locally, rotate/revoke trust material, and durably record required audit. No secrets in examples, URLs, request bodies or ordinary logs; authorised application data remains classified even if sent over TLS.

This profile does not implement a CA, token issuer, OIDC client or encryption-at-rest system. Exact enrollment, certificate lifecycle, human-to-service delegation and Wallet decision API are UC-001 security design work. OAuth certificate-bound tokens may be a later concrete credential profile; [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705) distinguishes that mechanism from mTLS client authentication. Do not claim a mere certificate gives farm permissions.

## Deployment portability

| Target | Same foundation | Environment-specific work still needed |
| --- | --- | --- |
| macOS laptop | HTTPS identity, contracts, grants, versions and lifecycle | OS service identity, protected trust/secrets, data paths, permitted roots and sleep/restart behaviour |
| Windows laptop | Same | Windows service identity, secret integration, permissions and explicit native/WSL/container choice |
| Linux laptop | Same | Distribution/runtime prerequisites, service manager, secret integration and filesystem permissions |
| Cloud Kubernetes | Same | Workload identity/trust delivery, namespace/RBAC, enforced network policy, persistent volumes, and provider landing-zone mapping |

The four [environment examples](examples/environment-macos.json) differ only in platform bindings; they do not prove those platforms work. Kubernetes additionally names a provider/landing-zone profile. The Scaleway identifier is intentionally labelled unimplemented. A real profile needs verified versions, resource settings and the requirements in [deployments](../../deployments/README.md).

The only connectivity mode defined here is `direct-https`: peer reachability must be explicitly arranged. This can operate locally or across approved networks, but does not solve NAT/firewalls by itself. Outbound pickup, relay and staging profiles remain deferred; do not claim arbitrary laptop/cloud integration before they exist. An environment egress list declares intended destinations; network enforcement and private-data destination permission are separate runtime checks. An opaque state/audit/secret reference is resolved by an environment adapter, never by querying a shared private module database.

## Admission and verification sequence

Validate documents → check exact capability/version/features → resolve dependency closure → establish trusted peer connectivity → exercise operation and security conformance → register/bind → obtain separate wallet grants → activate after readiness.

The runnable checker performs only the first two steps and structural environment matching. It always reports `runtimeVerified: false` and `accessGranted: false`, plus unresolved required dependencies. It must not be used as a production admission/authorisation service.

See [validator instructions and scope](../../conformance/foundation/README.md). The original [architecture examples](../examples/implementation.json) remain historical illustrations, not silently migrated executable configurations.
