# Module integration profile

Status: proposed requirements for review; no machine-readable schema or conformance harness exists yet. Applies to independently supplied Farmy modules, regardless of language or hosting environment.

## What a module must declare

| Contract area | Required declaration |
| --- | --- |
| Identity and capabilities | Implementation/publisher, immutable release, instance identity, supported capability operations and exact contract versions; independent binding versus inseparable bundling |
| Meaning of data | Accepted/output types and schema versions, units/time/reference systems where relevant, source version and provenance semantics, limits and supported optional operations |
| Dependencies | Required/optional capabilities and compatible versions/features, endpoint bindings, identity/secret/storage dependencies, hardware or co-location requirements; no hidden private database coupling |
| Connectivity | Endpoint/protocol, inbound versus outbound-initiated mode, reachability, permitted routes, proxy/relay requirements, maximum transfer size, deadlines and offline behaviour |
| Trust and permissions | Trusted identity profile, issuer/enrollment, credential lifecycle, wallet grant enforcement, necessary actions/scopes, processing locations, onward destinations and retention; secret references only |
| State and lifecycle | State ownership, configuration schema, readiness/degraded state, start/drain/stop, job/cancel behaviour, retry/idempotency rules, backup/restore, migration, removal and credential revocation |
| Accountability | Audit envelope and delivery, health/metrics with appropriate access controls, operator/contact, deletion acknowledgements and known limits |
| Compatibility evidence | API, semantic and migration compatibility separately; positive and negative conformance results, validated security profile and supported targets |

Authenticated/encrypted connectivity is necessary, not sufficient. Two JSON APIs may disagree on units, freshness, authority, idempotency or deletion; those are contract failures too. Unknown optional operations fail explicitly. Additional private endpoints do not become trusted Farmy capabilities automatically.

## Connectivity without a public endpoint on every laptop

Support direct authenticated calls where both sides are reachable. For a laptop behind NAT/firewalls, define an outbound-initiated polling/session or approved staging/relay profile before claiming remote operation. A module must advertise the modes it actually implements; protocol details are still to be specified.

In outbound work pickup, the worker authenticates to its Coordinator and obtains only work scoped to that instance. Input transfer still requires version-bound permission and reachable storage or an authorised snapshot. A relay is an additional trust boundary: document whether it can see plaintext, where it queues data, credentials, retention and who operates it. No silently opened inbound ports or fallback through unapproved infrastructure.

Registration must separate instance identity from endpoint address. Reject untrusted endpoint changes/redirects and verify the peer after reconnection. Connection loss causes declared retry, pause, expiry or failure; it must not remove security checks. Location transparency cannot make an offline source readable.

## Joining an installation

1. Validate the descriptor, provenance, declared capabilities and dependencies; determine compatibility with the intended workflow.
2. Enrol the instance through the authorised installation/trust process and provision its own credentials by reference. A self-supplied descriptor cannot establish its own trust.
3. Verify authenticated connectivity, peer identity and required operations against the advertised contract/security profile. Dependency outage and denied-access behaviour are part of these checks.
4. Register the instance and create an explicit binding. Issue only the wallet grants needed for that binding/workflow, under an authorised wallet decision. These steps remain distinct even if a UI presents them together.
5. Activate after readiness and policy checks. Pin binding/release/configuration revisions for running work. Monitor health without granting operational monitors general farm-data access.

For replacement, check readiness and compatibility, migrate or rebuild declared state, cut over the binding, drain/reconcile jobs, revoke old authority and record copy/deletion outcomes. Switching a binding cannot transfer private databases or make incompatible indexes portable. Retirement retains only explicitly permitted audit/backup data.

## Required conformance scenarios

- Independently implemented client/provider exchange valid data without a shared internal library, database, filesystem or UI process.
- Unknown identity, wrong wallet/audience, expired credentials, missing grants, delegation escalation and unapproved data destinations are denied.
- Schema/semantic mismatch and unsupported features fail explicitly; a compatible provider returns verifiable source/version and producer references.
- Duplicate requests, interrupted transfers, stale updates, cancellation, dependency loss and late replies follow declared behaviour without duplicate accepted mutations.
- Policy revocation blocks future protected disclosure even if old bytes remain indexed; retention/deletion tests distinguish requested, acknowledged and verifiably completed operations.
- Binding substitution preserves resource identity, records migration/rebuild and never silently changes running jobs or grants.
- A separate-host test proves the boundary; macOS/Windows/Linux/Kubernetes package tests come later for each advertised target.

Conformance establishes interoperability for tested profiles, not universal compatibility or proof that a hostile provider will honour retention promises. Registering an external processor remains a trust decision; code review, supply-chain verification and operational assessment complement protocol tests.

## Keeping integration small

Provide a shared specification, synthetic fixtures, contract tests and optional SDKs. Do not require one programming language, framework, cloud account, certificate vendor or private registry implementation. Exact interoperable security profiles still need to be selected: permitting alternatives without a common tested profile would move complexity to every integration.

The first profile should cover the document path and online wallet authorisation. Event streams, offline grants, physical actions and credential issuance need additional profiles; advertise these as unavailable until specified and verified. A common base plus explicit capability extensions is more realistic than one universal protocol claiming to handle all behaviours.
