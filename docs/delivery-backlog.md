# Incremental delivery queue

Status: proposed order, not a schedule or implementation report. All slices remain unimplemented. Follow the [working method](working-method.md); only one implementation slice should be active at a time.

| Order | Slice and observable result | Main families | Next action / status |
| --- | --- | --- | --- |
| 1 | [UC-001 controlled memory](../solutions/core/use-cases/UC-001-controlled-memory.md): register/read/move/version a synthetic local document and deny unauthorised access | Wallet, Connector, minimal Registry | Proposed; resolve the narrow local trust and version contracts, then implement and run |
| 2 | Extract a known field and retrieve it with its exact source version; duplicate execution produces one accepted result | Processing, Workflow, Knowledge | Queued; write its small case from UC-001 learning |
| 3 | Use an explicitly selected model for a cited answer; unapproved model egress is denied | Model access, Assistance | Queued; select a model integration only when needed |
| 4 | Preview and deliver exact approved content; altered recipient/payload and missing export permission are rejected | Exchange | Queued; local synthetic export first |
| 5 | Add a second source through S3 and reuse the working path without changing unrelated module source | Connectors | Queued; verify actual provider semantics, not just an emulator |
| 6 | Run two knowledge instances and replace one provider with an independently implemented alternative | Knowledge or Processing, Registry/Workflow configuration | Queued; declare rebuild/migration and keep unaffected versions unchanged |
| 7 | Reproduce the tested solution across target profiles and a mixed laptop/cloud topology | Deployment profiles and affected module adapters | Queued; choose one target per increment, Scaleway first for cloud |

Reorder based on learning; a necessary security/recovery correction outranks the next feature. Pull a small substitution experiment earlier if it is needed to validate a risky boundary. The rows are outcomes, not an obligation to implement every feature of the named families.

For each completed slice, add actual demonstration evidence to its case, retain regression tests and record expected versus actual module changes. The queue is not evidence that all contracts or target environments are supported.
