# UC-006 — Controlled exact-document disclosure

Experimental contract `0.6-draft`, using the existing foundation envelope and mutually authenticated TLS profile. See [operation schemas](operations.schema.json), [operation metadata](operations.json) and [OpenAPI routes](openapi.json). No credential issuance/signing standard is implemented here.

| Operation | Receiver | Required authority and outcome |
| --- | --- | --- |
| `disclosure.prepare` | Exchange | Authenticated bootstrap owner plus an exact-version Connector read grant issued to Exchange. Return and persist exact base64 bytes and an immutable manifest |
| `disclosure.approve` | Exchange | Owner with a separate Wallet capability grant for this operation/version/purpose. Persist approval for the exact manifest hash, expiring within ten minutes |
| `disclosure.deliver` | Exchange | Authenticated caller with its own delivery capability grant; current source-read and original approval grants must also remain valid. Send the stored exact preview to the pinned recipient |
| `disclosure.receive` | Synthetic recipient fixture | Enrolled Exchange sender and configured-sender marker; verify recipient identity/certificate, manifest hash, source, size and content digest. Deduplicate by disclosure ID and return a durable receipt |
| `receipt.inspect` | Synthetic recipient fixture | Bootstrap owner only; inspect received bytes/receipt for demonstration evidence. This is not a general external recipient API |

Manifest fields bind disclosure ID, exact Wallet/resource/version reference, recipient identity and TLS certificate fingerprint, fixed `synthetic.review` purpose, byte count and SHA-256 digest. Its hash uses UTF-8 JSON with sorted keys and separators `(',', ':')`, matching the published Python reference helper. This narrow profile uses ASCII identifiers and at most 16 KiB of bytes. Base64 is transport encoding, not encryption. Transport encryption is TLS; local development databases remain unencrypted.

Prepare, approve and deliver are distinct operations. Reading does not grant export authority. The owner previews bytes before approving; the demo/seed automatically approves only its known synthetic fixture. There is no implicit approval from a model or from a monitor token. Approval stores the manifest hash, not a cryptographic credential or portable signature.

The receiver validates the envelope before application logic: subject/certificate binding, wallet namespace, target, schema/version, purpose, deadline and mutation key. Changed content/recipient/version/hash cannot be substituted under an existing approval. Changing the configured recipient certificate invalidates that preview; prepare and approve a new disclosure. A later source update does not rewrite an approved old version.

## Persistence, retry and uncertainty

Exchange owns its private SQLite preview/approval/receipt records, operation-key bindings, audit and delivery intents. Recipient owns its independent receipt/content state. Neither reads another database. Preview content is retained locally with restrictive development filesystem permissions; use synthetic data only.

Before sending, Exchange durably records `unconfirmed`. A transport failure, invalid receipt or process interruption can leave that state even if the recipient already saved the document. Retrying the same disclosure rechecks all current grants and expiry, sends only the same manifest/bytes and recovers the recipient's existing receipt. Different operation payloads cannot reuse a successfully retained operation key. Concurrent duplicate sends converge at the recipient's unique disclosure ID; this does not claim exactly-once network delivery or support arbitrary recipient protocols.

Approval/delivery mutations use separate grants. Revoking the approval grant, delivery grant or source-read grant blocks subsequent delivery and cached receipt replay through Exchange. If authority is unavailable, delivery fails closed. Expired/revoked approval after an uncertain transfer may prevent automatic reconciliation; the fixture's owner inspection can demonstrate what it retained. No background retry, generic compensation or downstream copy recall is implemented. Checks authorise the send at that moment; a later revocation cannot undo bytes already sent.

A receipt means the synthetic recipient committed bytes to its local store. It is neither a signed receipt nor proof of human review, future deletion or compliance with usage conditions. Production protocols, cross-wallet governance, selective disclosure and wallet credentials remain separate work.

The [acceptance suite](../../conformance/uc006/test_runtime.py) exercises live service boundaries, outages, restart, lost acknowledgements and denials. See [run instructions](../../solutions/disclosure/uc006/README.md).
