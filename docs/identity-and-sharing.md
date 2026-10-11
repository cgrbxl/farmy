# Local identity and sharing — iteration 0.2.0

## Try it

Open the installed owner workspace with `farmy open`. In **Wallet**, inspect the local owner and paired consumer public-key fingerprints. In **Library**, choose an existing private item and press **Allow paired consumer**. The original managed copy remains the same; the policy now makes the locally paired consumer eligible. Press **Grant consumer access**, then **Open demo consumer**. In that separate view, refresh and open the shared document. Revoke in the owner view, then try a new read as the consumer: the Wallet denies it.

**Make private** also revokes existing consumer grants. Reallowing the consumer does not revive them. The grant button is disabled for private copies. A failed receipt delivery can be retried with Refresh without creating another grant.

## What is real

- Owner and consumer have persistent, distinct P-256 keys, separate private-key directories and pinned SHA-256 public-key fingerprints.
- The consumer runs in a separate supervised process with its own receipt database and browser origin (owner port + 1; normally 54801).
- The owner sends a typed grant receipt through an authenticated service connection. The consumer never queries the owner's client database and does not use the owner's private key to read.
- Each consumer service connection proves possession of its private key through TLS 1.3 mutual authentication. The Connector checks current Wallet authority before releasing bytes.
- Certificates and browser credentials rotate on the existing runtime lifecycle. Persistent public-key identity is retained. Substituting a pinned key causes startup to fail closed.
- Policy changes are transactional, revision-checked and idempotent. Existing source-reader ceilings remain binding. Backups include both identity stores, public-key pins and consumer receipts.

## What this does not establish

Both applications still run as the same Mac user. The supervisor provisions the demo keys and can access their files; process separation is not OS-user or hardware security isolation. Browser access still uses private bearer links, so possession of a consumer link gives control of that local consumer application. It is not a browser-held signing key or verified human identity.

The initial pairing is a locally provisioned test relationship, not a public registry lookup or an independently attested organisation. No fake public key is used. Private keys are file-protected, not Keychain-backed or application-encrypted. They never appear in the browser or QR codes.

TLS protects transport against captured-message replay. Application-level duplicate offers and policy requests are handled idempotently; a legitimate repeated read remains permitted while its grant is valid. There is no bespoke signed challenge protocol, offline credential presentation or claim of general replay-proof transferable documents.

Key replacement/recovery and pairing with arbitrary participants are not yet UI features. Restore the original keys from a protected backup if they are lost; do not silently accept a replacement. This iteration deliberately refuses key substitution rather than claiming to implement a complete rotation/recovery protocol.

## Next

Explicit participant enrolment and controlled key rotation, then JSON field-selection disclosure with a reviewable exact output. Recipient-bound QR retrieval needs a reachable endpoint; offline disclosure needs recipient encryption if confidentiality is required. Public trust-registry resolution remains optional and replaceable. Model-backed Copilot integration remains pending.

## Verification record

The full regression run passed 158 tests and 12 existing demos. After the final startup/receipt changes, 13 local tests passed; an additional source-ceiling test and a consumer-descriptor/persistent-identity recheck passed separately. This covers 160 distinct tests across the final checks, not a single 160-test run. Documentation links and browser JavaScript syntax were checked.

Installed browser verification used the existing `reference/farm_profile.json`: private → eligible consumer → explicit grant → separate consumer read succeeds → revoke → next read denied. The item was restored to private afterward. The upgrade retained the workspace; a stopped pre-upgrade backup was taken. The local identity fingerprints were checked across the final compatible build replacement.
