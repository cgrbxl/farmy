# UC-011 upload contract — 0.11-draft

`farmy.folder-upload` advertises `folder.upload`, a mutation with purpose `uc011.folder.upload`, using the existing authenticated request envelope and idempotency key. See [schemas](operations.schema.json) and [operation metadata](operations.json).

Input: source ID, owner ID, original filename and base64 content. Output: connector entry, SHA-256 digest and byte count. The current profile accepts UTF-8 txt/md/csv/eml up to 16,384 bytes, names up to 120 characters and at most 100 source entries. An identical filename/content reuses its generated entry; different content gets a distinct entry. Retrying an identical key returns its receipt; changing its payload returns conflict.

The Connector must explicitly enable uploads. The authenticated owner must match the source owner and Wallet source append authority must succeed. The operation neither admits an item nor grants read permission. Unsupported types/limits return unsupported; malformed names/encoding return invalid_request; caller/policy failures return denied; conflicting keys or target bytes return conflict. Uncertain transport failures require retry with the same key.

[Implementation, recovery limits and evidence](../../solutions/uploads/uc011/README.md).
