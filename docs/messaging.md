# Connect: channels, filters and recurring drafts

In the installed **Connect** view, choose a channel profile, enter exact approved sender and recipient IDs (one per line), and save. An empty list approves nobody. Use **Check sender filter** to test an identifier against the saved list. Unsaved list edits are not used. This is a metadata rehearsal; no account is connected, no messages are fetched, and provider identity authenticity is not established.

To create a recurring draft, select an approved recipient, enter a topic and the exact text, choose an elapsed interval and first time, then select **Create draft rule**. Inspect the rule and use Pause/Resume. Refresh to see newly created drafts. All drafts are marked **NOT SENT**. A topic labels the rule; it does not independently constrain the meaning of text.

The scheduler operates while Farmy is running, including when the browser is closed. It cannot run while the Mac is asleep or Farmy is stopped. Recovery coalesces missed runs into the latest due slot. Fixed elapsed intervals are not timezone-aware calendar recurrence; DST can move the visible local hour. Removing an approved recipient pauses their rules. Existing drafts remain historical content and are never automatically sent when a recipient is reapproved.

## Responsibilities

- **Connect:** configure channel profiles, sender filters, recipients, intervals and pause/resume; inspect local draft history.
- **Wallet:** remains the authority for actual Library reads and external disclosure. This planner does neither, and its local recipient list is not a Wallet access grant.
- **Library:** does not ingest message bodies in this increment. A future connector must apply sender policy before admitting content.
- **Copilot:** does not generate text in this increment. Future summaries require exact authorised source scope and an approved model destination; incoming message text must never expand authority.

Email/SMS/WhatsApp/Signal live integrations each need provider-specific feasibility, authentication and identity checks. No claim is made that they expose equivalent APIs or filtering. Actual delivery also needs explicit approval/automation grants, a delivery ledger, uncertain-outcome reconciliation and provider idempotency support; local draft deduplication is not an exactly-once delivery guarantee.

See [component contract and limits](../modules/workflow/messaging/README.md). These features extend Connect without adding a fifth tab.

## Verification — 0.3.0

Ten planner tests, fifteen local lifecycle tests and twelve browser-bridge tests passed (37 distinct focused checks); the final owner-boundary/scheduler/backup integration check was rerun successfully. The full unrelated model/cloud-demo suite was not rerun for this increment. Documentation links and JavaScript syntax checks passed.

Browser verification in an isolated workspace saved fictional email IDs, denied an unknown sender, allowed the configured sender, created a timed draft, confirmed it was marked NOT SENT, paused the rule and confirmed refresh did not duplicate the draft. The test workspace was stopped afterward. The installed workspace retained its existing information and starts with no channel approvals or draft rules.
