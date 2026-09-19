# UC-002: exact-source extraction and evidence

Experimental operation version `0.2-draft`, using the unchanged `farmy.integration/0.1-draft` envelope. Existing UC-001 operations retain `0.1-draft`. [OpenAPI](openapi.json), [strict input/output schemas](operations.schema.json) and the [operation catalogue](operations.json) define this slice. The optional Python transport reads that catalogue; other implementations need not use it.

All operations are POST `/farmy/v0/<operation>`, JSON over mutually authenticated HTTPS. `payloadSchema` is `urn:farmy:uc002:<operation>.input`; successful `resultSchema` ends in `.output`. The catalogue pins capability, purpose and mutation requirements. Unknown fields, wrong versions, wrong purposes and mismatched authenticated actors/targets/wallets fail before execution. HTTP errors and operator-only health/descriptor routes follow [UC-001](../uc001/README.md).

| Operation | Receiver / authority | Result |
| --- | --- | --- |
| `access.issue` | Wallet; owner management policy | Grant ID/revision, bound to exact source resource/version, subject, audience, operation, purpose, expiry and composition revision |
| `access.revoke` | Wallet; owner, expected grant revision | Revoked grant and new revision |
| `access.check` | Wallet; authenticated receiving service is the grant's audience, forwarding the subject it authenticated | Current allow decision/revision, or denial; never content |
| `extraction.compute` | Processing; enrolled Workflow acting for owner under fixed extraction policy; separate source-read grant for Processing | Stable proposal ID; source bytes are fetched from Connector |
| `extraction.get` | Processing; caller equals subject with separate disclosure grant | Exact-source proposal with extracted value and provenance |
| `evidence.index` | Knowledge; Workflow with indexing grant, plus separate Processing disclosure grant for Knowledge | Accepted proposal ID; Knowledge fetches the proposal itself from authenticated Processing |
| `evidence.query` | Knowledge; caller equals subject with exact-source query grant | One evidence record for `crop`, or error |
| `job.run` | Workflow; owner management policy, exactly one source/version | Durable job ID, phase and proposal ID, or error |
| `job.inspect` | Workflow; owner management policy | Saved job phase/receipt; no extracted content |

`farmy.permissions` is the Wallet's generic scope-checking capability. It has no crop/parser rules. Bootstrap explicitly permits three audience/operation/purpose combinations: Processing/extraction.get/uc002.index; Knowledge/evidence.index/uc002.index; Knowledge/evidence.query/uc002.query. Only the owner may issue them. Grants expire within one hour; demo grants last ten minutes. `access.revoke` is distinct from UC-001 `grant.revoke`, which controls Connector reads.

## Data and provenance

The synthetic UTF-8 report contains exactly one lowercase `crop: <value>` line. The parser is limited to 16 KiB and accepts a value matching `[a-z][a-z -]{0,63}`. It rejects missing, duplicate, malformed or undecodable fields. It executes no document instructions and calls no model. Quote positions are zero-based UTF-8 byte offsets, end-exclusive; line numbers start at one. Evidence includes the source wallet/resource/version, source SHA-256, extractor version `farmy.text-field/0.1.0`, value, quote and offsets. A proposal ID hashes the canonical full result excluding its own ID.

Knowledge stores one accepted derived entry per exact source version for this fixed extractor. “Accepted” means accepted into this derived index under an explicit indexing grant. It does not create or approve an authoritative Wallet farm record. Processing remains a producer of proposals. Provenance identifies the source and producer; it does not establish that the source's agronomic claims are true.

## Authority and retained copies

The owner issues four independent grants: Connector source read for Processing; proposal disclosure from Processing to Knowledge; indexing by Workflow at Knowledge; query disclosure by Knowledge to the reader. Each disclosure receiver checks caller/subject identity. Processing and Knowledge recheck online permission immediately before returning derived content; Knowledge rechecks indexing permission before committing. Binding a service or knowing a grant ID gives no access by itself.

Revoking a query grant immediately denies the next query even while evidence remains indexed. Revoking a source-read grant prevents future captures by Processing; it does not revoke separately authorised, already retained derived copies. Revoke their disclosure/query grants separately. This explicit separation is not cascading revocation. Already delivered/in-flight authorised content cannot be recalled. A Wallet outage denies new disclosures, including cached evidence.

## Duplicates and recovery

Every mutation has an idempotency key. Workflow scopes a job to owner + key and pins input references, grant references and composition revision. Changed inputs with the same key conflict. Phases are `pending`, `extracted`, `succeeded`. Workflow persists a phase only after the receiver accepts its step; no database transaction spans a network call. Retries use stable per-job step keys. A lost response can repeat computation/requests but converges on the same proposal and one accepted index entry. This is not exactly-once execution.

Processing derives a deterministic proposal from exact source bytes and extractor version; it deduplicates actor/key and rejects changed inputs. Knowledge deduplicates actor/key and enforces one immutable accepted proposal per exact source; a conflicting proposal fails instead of overwriting history. A new source version receives its own entry. Query requires an explicit version and never silently substitutes “latest”. There is no removal/rebuild API yet.

Workflow retries are owner-driven: re-submit the same job after correcting an unavailable dependency. A restart retains phases. There is one executing job per Workflow process, bounded synchronous calls, no automatic background retries, cancellation or scheduler. Terminal content errors remain failed requests with a saved pending job; changing its inputs needs a new key. Successful-job replay returns an owner-visible receipt without re-disclosing content; queries still recheck current grants.

The five [reference services](../../solutions/document-path/uc002/README.md) use private SQLite state and public HTTPS only. Tests deliberately inspect synthetic index state to count duplicate entries; runtime services never read each other's databases.
