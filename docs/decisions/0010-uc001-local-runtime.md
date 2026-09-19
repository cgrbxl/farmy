# ADR 0010 — UC-001 local trust and immutable snapshots

Date: 2026-09-19
Status: Implemented for the experimental synthetic macOS slice only.

## Decision

Use separate Wallet and Local Folder Connector processes and private SQLite state. Exchange the draft foundation envelope and narrow operation contracts over loopback HTTPS with mutual TLS 1.3. Bootstrap a short-lived development CA, individual certificates and explicit fingerprint enrollment; remove the CA signing key after bootstrap. Configuration grants connectivity trust, not content access. Owner management and Wallet capture permissions are explicit development policies. Content reads require a separate scoped, online-checked Wallet grant.

Retain immutable content-addressed snapshots in the Connector. Wallet owns logical IDs, versions, source locations, grant state and mutation deduplication. A move verifies identical content; an update produces a new version. Read authorisation checks exact subject/resource/version, audience, purpose, expiry and binding revision, with a second check just before returning content. The Registry starts as a pinned binding file adapter. No broker, Workflow runtime, cloud service or shared private database is needed for this case.

Use strict schema validation, expected revisions, bounded source capture, symlink rejection and generic error responses. Keep audit events in each module's own state without content or credentials in logs. Optional Python transport helpers do not own domain policy or persistence.

## Consequences and limits

This delivers an executable instance of the proposed mTLS-online profile; it does not complete production credential lifecycle, portable secret storage, OS process isolation or all environment profiles. All identities run under the same local OS user with unencrypted development keys and state. A compromised user/host can bypass service checks. The server is a development server and snapshots/audit/grant history have no retention policy. No private farm data is supported yet.

Two-pass capture detects observed concurrent changes; it is not an atomic filesystem snapshot against a malicious writer. Old registered bytes remain available independently of source mutation. Failed Wallet mutations can leave orphan snapshots. Read revocation takes effect on the next authorisation; already delivered or in-flight authorised bytes cannot be recalled. Restart persistence is tested, power-loss recovery is not.

See [run instructions and limits](../../solutions/core/uc001/README.md), [contracts](../../contracts/uc001/README.md) and [acceptance tests](../../conformance/uc001/test_runtime.py). Windows/Linux/Kubernetes packaging and Scaleway remain deferred.
