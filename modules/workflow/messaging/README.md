# Local messaging draft planner

Experimental component introduced in 0.3.0. It owns its own SQLite state and exposes an embedded Python interface (`snapshot`, `check_sender`, `change`, `tick`). The local supervisor hosts it; it is not yet a separately deployable service or a provider connector. It imports no networking or model SDK and cannot read Library documents, send messages or expand Wallet grants.

## Implemented boundary

Channel profiles: email, SMS, WhatsApp and Signal. Profiles are local configuration categories, not installed/live integrations. Sender and recipient identifiers match exactly and case-sensitively; no wildcard or display-name inference. Sender checks receive only owner-supplied metadata and return a decision without retaining message bodies. A future provider adapter must authenticate/normalise identifiers before applying filtering.

Owner-authored, fixed-text recurring rules require an approved recipient. A topic is a label, not an enforceable semantic restriction. Rules create local drafts only, never release information externally. They have no Library source scope because they read no documents. Automatic summaries and actual delivery require separately bounded Wallet authority and reviewed provider bindings.

Intervals are elapsed 1, 24 or 168 hours, anchored to the first timestamp. UTC timestamps avoid ambiguous stored local times; DST may shift the displayed local hour. On recovery, only the latest due interval is drafted, not every missed interval. The schedule advances and draft insertion commit atomically. Unique `(rule_id,due)` plus an immediate transaction prevents duplicate drafts from concurrent ticks. Pausing preserves prior drafts; removed recipients cause rules to pause and reapproval does not automatically resume them.

Changes are idempotent and channel/pause updates check revisions. Browser retries keep their original key in session storage and have an explicit retry button. The planner retains the latest 200 drafts, shows 50, retains 500 audit events, supports 50 rules and 50 identifiers per list. After 10,000 mutation receipts it refuses new changes pending maintenance rather than discarding replay protection. There is not yet a rule deletion or edit interface; pause and replace a rule within the limit.

State schema version 1 uses `PRAGMA user_version`; unknown versions are refused. No destructive migration runs. Runtime backups include `state-messaging`; source data and consumer capabilities are unchanged.
