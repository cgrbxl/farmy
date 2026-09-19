# UC-003 — Source-scoped observations

Experimental contract `0.3-draft` over the unchanged `farmy.integration/0.1-draft` envelope. [OpenAPI](openapi.json), [payload/result schemas](operations.schema.json) and [operation catalogue](operations.json) define the narrow interface. UC-001 and UC-002 operation versions remain unchanged.

POST `/farmy/v0/<operation>` uses mutual TLS and the usual actor/subject/wallet/target/deadline validation. `payloadSchema` is `urn:farmy:uc003:<operation>.input`; result schema ends in `.output`. Unknown fields and contract versions fail. `inputRefs` must be empty: source scope lives in the typed payload, not in a fabricated document-version reference. HTTP errors and operator management routes follow [UC-001](../uc001/README.md).

| Operation | Authority | Behaviour |
| --- | --- | --- |
| `source.register` | Wallet owner management policy | Assign a stable source ID and owner, bound immutably to a configured source Connector |
| `source.grant` | Source owner | Grant one enrolled consumer read access to that source, including all retained and subsequently appended observations until expiry/revocation |
| `source.revoke` | Source owner; expected grant revision | Revoke a source grant and increment its revision |
| `source.authorize` | Source's authenticated Connector forwarding the authenticated subject | Check source/owner and append, read or audit authority; return decision revision only |
| `sensor.append` | Source owner, checked online with Wallet | Append one immutable synthetic observation to its source; return assigned ID and source sequence |
| `sensor.read` | Consumer with current source grant, checked online twice | Return a bounded page from that source and a recorded release ID |
| `sensor.audit` | Source owner, checked online | Return up to ten recent release records for the source; no observation values |

The Wallet capability is `farmy.sources`; the Connector capability is `farmy.observations`. Source identity, owner and Connector binding cannot be changed by these APIs. The current owner management identity is the single enrolled `owner`; this is not multi-tenant owner administration. Grant IDs are references, not bearer credentials. The receiving Connector must match the source binding, and must authenticate its caller before forwarding that subject to Wallet. A source owner also needs an explicit read grant to use `sensor.read`; ownership separately permits appending and auditing.

## Source scope and observations

A grant covers source + owner + consumer, bound to the serving Connector. There is no per-observation approval. Observations requiring a different policy must be ingested into separately identified sources. Requests cannot relabel stored observations or supply an existing observation ID to move it elsewhere. The synthetic source append API trusts its authorised owner to label the source correctly; it does not authenticate physical hardware or prove that a sensor measurement is genuine.

Each observation has a generated ID, source/owner, per-source sequence, UTC observation time, numeric value and explicit `degC` unit. This reference implementation is a bounded synthetic temperature source: values range from -80 to 80; times are at most 40 characters. Sequence is ingestion order, not event-time order. Observations are immutable; there is no update/delete/move API or retention policy.

A read specifies `afterSequence` (exclusive, starting at zero) and `limit` (1–100). It returns observations in sequence order. Repeat a page to retrieve the same retained observations; new appends have higher sequences. Use the last returned sequence for the next page. An empty page has its own release record. There is no arbitrary observation selector, live subscription or per-grant historical cutoff.

## Permissions, retries and persistence

Source grants expire within one hour; the demo uses ten minutes. Revocation denies subsequent read authorisation; no offline or cached-positive mode exists. An already authorised in-flight response cannot be recalled. Stopping Wallet denies reads, appends and audit disclosure. Raw-source permission does not make promises about independently retained downstream copies.

Mutations require idempotency keys. Wallet reuses its transactional mutation mechanism. Sensor append scopes a key to authenticated actor and canonical payload: identical retries return the original immutable observation; a changed source, owner, timestamp, value or unit conflicts. Each append assigns its source sequence in the same transaction as the observation and deduplication record. Reads generate a new release record for each attempt; they are not deduplicated as if delivery happened only once.

Wallet persists sources/grants, and the synthetic Connector persists observations/append keys/releases in its own database. Existing document and evidence modules do not access those tables. Sources and grants survive process restart. Adding the two Wallet tables preserves existing resource/grant records; no downgrade or source-binding migration tool is supplied.

## Honest release records

Before returning a page, the Connector commits a record containing release ID, owner, consumer, source, grant ID, decision revision, time and the exact observation IDs/sequences/hashes. Hashes use SHA-256 of each complete observation encoded as UTF-8 JSON with sorted keys and separators `(',', ':')`. Record type is `release_authorized`. If recording fails, no observations are returned.

This records an authorised release attempt, not confirmed receipt or subsequent consumption. A connection can fail after the record is committed. Owner-visible audit returns recent records; neither the consumer nor another identity can use a read grant to inspect them. Denials are written to the service's generic audit table without raw observations. Audit tables are not signed, tamper-evident or immune to changes by the trusted host user.

See the [runnable solution](../../solutions/sensor-path/uc003/README.md) and [acceptance tests](../../conformance/uc003/test_runtime.py).
