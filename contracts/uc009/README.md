# UC-009 managed-copy profile — 0.9-draft

Uses the existing mTLS online-authorisation envelope, pinned peer identities, deadlines and structured faults. [Operation schemas](operations.schema.json) and [operation declarations](operations.json) define exact inputs/outputs; [solution scope](../../solutions/managed-items/uc009/README.md) defines the current composition.

| Capability | Operations | Authority |
| --- | --- | --- |
| `farmy.folder-source` | `folder.attach` | Source owner bootstrap authority; one root bound to one source/owner |
| `farmy.folder-source` | `folder.list`, `folder.read` | Current source/owner/consumer grant |
| `farmy.folder-source` | `folder.capture` | Enrolled Wallet acting for source owner, with current source grant |
| `farmy.managed-items` | `item.admit`, `item.inspect` | Owner bootstrap authority |

`folder.list` returns at most 100 eligible flat regular-file basenames. `folder.read` returns at most 16 KiB, base64 encoded with its SHA-256 digest. Symlinks, paths outside the root and nested paths are rejected. Grant coverage is collective, including future eligible files.

`item.admit` sends the selected source/owner/entry and expected digest, source grant, title, classification and allowed-reader list. Wallet requests `folder.capture`; Connector rechecks current source authority and exact bytes, stores an immutable snapshot and returns its inherited reader ceiling. Wallet checks that the item list is a subset and atomically records identity/version/provenance and its durable receipt. `private` requires owner-only readers. Admission does not issue an item grant; existing `grant.issue` and `read.version` enforce exact-item consumption.

The owner+idempotency-key admission record converges for concurrent identical payloads and rejects a changed payload. Receipt replay is historical metadata and does not require renewed source access. Folder attachment converges on the same source/root tuple; a different tuple conflicts. Capture converges by content digest, reauthorises on each attempt, and may retain an unreferenced snapshot after downstream failure. These two Connector operations use intrinsic identity, not a separate request-key ledger.

The inherited ceiling is a bootstrap configuration snapshot, not a live policy federation. The reference profile admits only owner-controlled synthetic files; it does not infer third-party retention/redisclosure rights from a read grant. Source and item revocation act independently. Metadata inspection is owner-only. Managed-item update/move, derived processing and export are deliberately unsupported in this increment.
