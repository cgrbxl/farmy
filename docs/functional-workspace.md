# Four views: Copilot · Wallet · Library · Connect

This is the agreed navigation order. Copilot is the default entry point. The tabs organise user tasks, not backend services; modules may contribute views and actions to one or more tabs without adding top-level navigation.

| View | User question | Scope |
| --- | --- | --- |
| Copilot | What can I understand or do? | Conversations, analysis, dashboards, reports and proposed actions using explicitly permitted information and tools. |
| Wallet | Who am I, what can I prove and what am I authorising? | Identities, key fingerprints, grants, policy, provenance and disclosure. Credential verification and presentations are planned. |
| Library | What information do I have? | Browse, preview, retain and organise information without AI; exact versions, storage and backup. |
| Connect | What can Farmy communicate with? | Sources, recipients, storage services, APIs, sensors and model providers; configuration, authentication and testing as those capabilities become available. |

## Working local installation

- **Copilot:** two refreshed workspace-record questions. No model-backed document analysis yet.
- **Wallet:** owner/consumer fingerprints, actual authority boundaries and managed-item authorisations. Allow a paired consumer, grant access, revoke it or make the copy private.
- **Library:** source browsing, bounded previews, managed copies, provenance and owner reads. Contextual policy/grant controls remain beside each item.
- **Connect:** source/recipient/provider overview plus [local channel profiles, sender-filter checks and recurring draft rules](messaging.md). No live messaging provider, message ingestion or external delivery is connected. Provider enrolment and AI-assisted connection setup are not implemented.

Wallet and Library invoke the same actions and refresh the same Wallet records. They do not maintain separate policy settings or duplicate document stores. Private information can live in Library; Wallet is not a second private-file folder. Changing eligibility is not issuing a grant.

The consumer remains a restricted separate application, without owner navigation. Failed refresh hides the owner views; names render as text, and refresh invalidates previous Copilot summaries. Installed software and data remain separate.

## Phone simulation

The annotated phone demo uses the same navigation. Copilot contains the conversation and expandable dashboard (maps, charts and simulated device actions). Wallet holds disclosure policies and the simulated audit. Library holds documents and messages. Connect holds sources and sender filters, with the selected simulated model route visible in the header. These are fictional browser interactions, not added production capabilities. The supplied original mockup is preserved as historical input.

## Module placement and AI boundaries

A weather connector contributes setup/health to Connect and observations to Library. Analysis contributes charts and reports to Copilot. A credential module contributes verification/presentation to Wallet, and optional trust-service configuration to Connect.

Permission controls stay beside the action and use a shared authority model. AI-assisted setup should propose bounded configuration and tests through restricted authority, never increase its own rights. AI-generated dashboards should first compose approved chart/map/table/report components with review and undo; arbitrary rewriting of the running application is not implied.

Global application settings should use a small settings surface rather than a fifth primary tab. Backups currently use the local runtime tools; storage-management and settings interfaces remain future work.

## Verification — 0.2.1

Installed build `0.2.1-9cde75d88d21` was opened in the browser. The navigation order and Copilot default were checked, Wallet and Library showed the same four retained copies, an owner read succeeded, and a refreshed Copilot inventory reported the current source listing. The annotated phone simulation was checked across all four tabs, its map and four chart SVGs rendered under Copilot, and no browser errors were reported. JavaScript syntax and repository documentation links passed. The external hosted simulation has not been republished as part of this local revision.
