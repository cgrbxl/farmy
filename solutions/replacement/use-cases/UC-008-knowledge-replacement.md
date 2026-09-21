# UC-008 — Two Knowledge instances and a replaceable provider

Actor: an installation operator, with a separately authorised reader.

Need: change a Knowledge implementation without changing source identities, weakening permissions, adopting another provider's private schema or interrupting the other instance.

Fixture: one synthetic UTF-8 crop report. Two separately enrolled Knowledge instances initially use the Evidence provider. The operator replaces B with the journal implementation while A continues running.

Success: a new, explicitly authorised rebuild job yields identical exact-source evidence through the existing API; both instances expose their own monitoring summaries. B starts empty and becomes queryable after rebuild. Its original private store remains untouched. A remains available.

Denials and recovery: wrong audience/subject/version, revoked/expired authority, missing proposal-transfer permission and unavailable Wallet all prevent disclosure. Descriptor mismatch blocks selection. Changed bindings conflict with old job keys; restoring the original binding permits an interrupted job to resume. Concurrent duplicate indexing and process restarts retain accepted evidence.

Expected change: alternative Knowledge domain implementation, minimal Registry admission, optional Workflow binding, composition and client configuration. Actual change matches this boundary: Wallet, Connector, Processing, transport helper and live monitor code are unchanged. Public operation schemas are unchanged.

Evidence and limits: [runner, eleven checks, verification baseline and migration policy](../uc008/README.md). Local macOS only; shared optional transport SDK. Rebuild is deliberate, with B downtime and retained trusted identity. This is not a universal migration, search-equivalence or independent-vendor claim.

Continuation: target packaging can proceed independently. UC-007 requires real Scaleway evidence before it can be completed. Interactive module modes remain in the future backlog.
