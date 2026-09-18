# Document-path solution recipe

Status: design-only; not deployable.

Purpose: Local Folder and S3 sources → authorised Document Processing → Knowledge → explicitly selected model → source-linked answer → controlled export.

Build on the [Core recipe](../core/README.md), adding Workflow, Document Processing, Knowledge, Model access, Assistance and Exchange. Select individual Connector implementations and an independent model runtime or external endpoint. Do not embed source-provider credentials into processors.

Use the [delivery queue](../../docs/delivery-backlog.md) for current ordering and the [working method](../../docs/working-method.md) for each slice. The cases below describe solution outcomes, not separate up-front design phases.

Incremental cases:

1. Extract and retrieve a known field from a synthetic report with its exact source/version; duplicate ingestion produces one accepted result. No model is needed yet.
2. Add a source-linked model answer and an approved exact-content export. Reject unauthorised egress, wrong-wallet access and changed export recipients.
3. Add S3 through a Connector and repeat the path without changing unrelated modules.
4. Run two Knowledge instances and substitute an independently implemented Processing or Knowledge provider with declared migration, keeping unaffected module versions unchanged.

Before release, define concrete fixtures and expected results, pin workflow/binding/configuration revisions and artifacts, declare data destinations/retention, select security and target profiles and attach lifecycle/conformance evidence. The diagram is not permission to export; each boundary enforces its own grant.

For mixed laptop/cloud operation, declare reachability, authorised snapshots, copy retention and wallet availability; bounded offline authority needs an explicit profile. Deployment selection follows implementation, not the reverse. See [communication flows](../../docs/module-communication.md).
