# UC-010 — use the Wallet through a real interface

**First interactive journey**, using the existing UC-009 Wallet and Connector APIs. These are real local service calls over mutual TLS, with synthetic email exports and two test identities. This is not the simulated phone mockup.

```sh
.venv/bin/python solutions/interactive/uc010/run.py launch
```

Open the private local URL printed by the runner. A free port is chosen automatically; `--port` can choose a specific port. Keep the runner running. Closing a browser tab does not stop services; Ctrl-C stops this runner and discards its temporary state. Development grants last up to one hour; restart for a fresh session.

## Try it in two views

1. **Owner:** preview `inspection.eml` in the connected folder. Choose “Owner and demo consumer,” then **Add to my Wallet**. The immutable item appears with individual provenance and exact version. **Open managed copy** reads that version through Wallet authorisation.
2. **Open demo consumer** in a separate tab. **Try to open Demo document 1**: access is denied. Admission did not grant access.
3. Return to Owner and **Grant consumer access**. Retry the consumer read: the actual email is returned.
4. Owner: **Revoke access**. Retry the consumer read: access is denied and the view clears previously displayed content.
5. Optionally admit `supplies.eml` with **Only me (private)**. The owner can open it; trying to grant it to the consumer is rejected by Wallet.

The demo consumer catalogue deliberately exposes generic entries, including entries without grants, so denial is demonstrable. It reveals no filenames, provenance or source credentials. This is a test harness, not a production discovery policy. Revocation cannot recall already delivered bytes. The interface clears displayed read content when refreshed, hidden or before another attempt; there is no claim of immediate remote erasure.

## Boundaries and recovery

Owner and consumer have different random browser bearer tokens. Opening the owner's link delegates control of this **synthetic** composition and allows opening the consumer view. The consumer token cannot invoke owner actions. Both tokens remain in their own tab's session storage; URL fragments are removed after loading. Service certificates and keys remain server-side. The read-only monitoring token has no interactive authority.

The bridge binds to loopback, checks Host and Origin, requires explicit JSON POSTs and bearer credentials, bounds request bodies, serves a restrictive CSP and sets `no-store` and `no-referrer`. It exposes only fixed preview/admit/grant/revoke/read actions—not an arbitrary service proxy, path picker or credential editor. Contents are rendered as text. This local trusted bridge is a demonstration of two service identities, not production human authentication, multi-tenant isolation or a cloud-ready security profile.

The bridge owns a small SQLite catalogue and request ledger; it never reads another module's private database. Mutation intents are committed before calling a service. A lost response keeps the exact original request for retry, including grant expiry and revocation revision. Pending mutations block new mutation keys until reconciled. Repeated grant clicks cannot create multiple live consumer grants. **Retry pending action** reuses the recorded operation; bridge restart preserves its receipts within the current runner's lifetime. No new service capability or wire contract was needed.

The owner copy-read action obtains an idempotent owner-only grant through the public Wallet API, expiring one hour after admission. Consumer grants remain separately issued and revoked. No real upload, mailbox, signing, AI configuration, persistent user workspace or remote deployment is included.

## Verification and module impact

Verified 2026-09-25 on macOS 26.6.2 arm64 with Python 3.14.6: all 126 selected tests and ten demos passed, including the installed local model and optional S3 fixture. Browser checks confirmed denied → grant → allowed → revoke → denied, and owner-only managed-copy reads with rejected consumer grants.

Expected and actual changes: a replaceable browser client and local client bridge, using Wallet, Connector and the existing binding adapter. **No service-domain code changed.** This increment makes established capabilities usable rather than counting them as new backend capabilities.

Twelve real HTTP/mTLS tests cover the whole journey, separate credentials, consumer restrictions, origin/authentication/input checks, stale previews, private items, idempotency, lost admission/grant/revocation replies, bridge restart, regrant and fail-closed service outages.

```sh
.venv/bin/python -m unittest discover -s conformance/uc010 -v
.venv/bin/python solutions/interactive/uc010/run.py demo
.venv/bin/python scripts/verify.py --with-local-model --with-s3-fixture
```

The full selection comprises 115 baseline tests, 11 optional UC-007 S3-fixture checks and ten demos. Local S3 evidence is not real Scaleway validation. Browser verification includes the actual owner/consumer denial → grant → allowed → revoke → denied journey. The [project guide](../../../dashboard/README.md) now distinguishes usable interfaces, API-tested foundations and planned work.
