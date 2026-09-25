# Incremental delivery queue

Status: proposed order, not a schedule or implementation report. UC-001 through UC-006 and UC-008–009 have runnable synthetic macOS demonstrations and acceptance suites; UC-007 has local evidence but awaits real-provider validation. Follow the [working method](working-method.md); one implementation slice is active at a time; provider-blocked UC-007 is parked while independent work proceeds.

| Order | Slice and observable result | Main families | Next action / status |
| --- | --- | --- | --- |
| 1 | [UC-001 controlled memory](../solutions/core/use-cases/UC-001-controlled-memory.md): register/read/move/version a synthetic local document and deny unauthorised access | Wallet, Connector, minimal Registry | Implemented for synthetic macOS development; [run/evidence](../solutions/core/uc001/README.md); eight runtime acceptance tests pass |
| 2 | [UC-002 exact-source evidence](../solutions/document-path/use-cases/UC-002-exact-source-evidence.md): extract/retrieve one field; duplicate execution produces one accepted derived entry | Processing, Workflow, Knowledge; generic Wallet permissions | Implemented for synthetic macOS development; [run/evidence](../solutions/document-path/uc002/README.md) |
| 3 | [UC-003 source-scoped observations](../solutions/sensor-path/use-cases/UC-003-source-scoped-observations.md): one source/owner/consumer permission covers multiple observations with traceable delivery | Wallet, Connector, client | Implemented for synthetic macOS development; [run/evidence](../solutions/sensor-path/uc003/README.md) |
| 4 | [UC-004 cited model answer](../solutions/assisted-answer/use-cases/UC-004-cited-model-answer.md): explicitly selected local model, exact citation and denied unapproved routing | Model access, Assistance | Implemented for synthetic macOS development; [real Qwen/Ollama run and limits](../solutions/assisted-answer/uc004/README.md); ten runtime acceptance tests |
| 5 | [UC-005 operational dashboard](../solutions/operations/use-cases/UC-005-operational-dashboard.md): live module inventory, declared connections and authorised content/activity summaries | All implemented families; replaceable client | Implemented for synthetic macOS development; [run/evidence](../solutions/operations/uc005/README.md); eleven monitoring/launcher acceptance tests |
| 6 | [UC-006 controlled disclosure](../solutions/disclosure/use-cases/UC-006-controlled-disclosure.md): preview/approve exact bytes; reject changed recipient/content and missing export authority; recover receipts | Exchange, existing Wallet/Connector | Implemented for synthetic macOS development; [run/evidence](../solutions/disclosure/uc006/README.md); fourteen acceptance checks |
| 7 | [UC-007 S3 source](../solutions/s3-source/use-cases/UC-007-s3-source.md): select a second storage implementation and reuse extraction/disclosure | Connectors; optional snapshot helper | In progress: implementation, 11 local HTTP-double checks and demo pass; [run locally](../solutions/s3-source/uc007/README.md). Real Scaleway validation awaits approved bucket/region/prefix and credential reference |
| 8 | [UC-008 Knowledge replacement](../solutions/replacement/uc008/README.md): run two instances and replace one domain implementation | Knowledge, Registry, Workflow | Implemented for synthetic macOS: eleven acceptance tests; explicit public-API rebuild, shared optional transport SDK |
| 9 | [UC-009 managed items](../solutions/managed-items/uc009/README.md): admit a selected source email as an individually governed immutable copy | Wallet, Connectors | Implemented for synthetic macOS: twelve acceptance tests; source and item permissions stay separate |
| 10 | Reproduce the tested solution across target profiles and a mixed laptop/cloud topology | Deployment profiles and affected module adapters | Queued; choose one target per increment, Scaleway first for cloud |

Reorder based on learning; a necessary security/recovery correction outranks the next feature. Pull a small substitution experiment earlier if it is needed to validate a risky boundary. The rows are outcomes, not an obligation to implement every feature of the named families.

For each completed slice, update the dashboard and affected repository documentation, add actual demonstration evidence to its case, retain regression tests and record expected versus actual module changes. The queue is not evidence that all contracts or target environments are supported.

The [three core concepts](core-concepts.md), clarified on 2026-09-21, guide future increments: admitted AI-generated interfaces, independently governed data-space participants and wallet trust networks. Their candidate demonstrations remain unimplemented and are not silently inserted ahead of this queue.


## Future track — interactive modules

Add interactive modes gradually through the [interactive module backlog](interactive-modules.md), alongside use cases rather than as one large dashboard rewrite. These candidates are unimplemented and do not reorder the queue above:

1. **Choose and configure AI:** select an authorised model/provider, validate endpoint and secret references, then activate a versioned profile. Start locally before adding an external API.
2. **Issue:** import/register an exact document version and sign a claim as its issuer.
3. **Present:** approve a disclosure and sign the presentation as holder, bound to the intended verifier and a fresh challenge.
4. **Verify externally:** use a separate verifier interface with a link or QR request; report cryptographic validity, issuer trust and credential status separately.
5. **Extend trust and interaction:** add third-party signed contributions and other family interfaces one concrete use case at a time.

Each increment retains independent module deployment and public contracts. The current monitor remains read-only; interactive identities and action permissions must be introduced explicitly. A separate verification implementation fits the Wallet family, preserving the nine-family architecture.
