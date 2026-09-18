# Abstract capability review

Status: architecture review proposal, 2026-09-18. This tests coverage against Farmy's current vision, not every possible future agricultural use. No new capability or module is implemented, and this review does not silently accept new technical decisions.

## Finding

The previous map covers the initial document solution but mixes abstract capabilities with a particular implementation decomposition. It leaves transformations/analytics, event acquisition, model execution and controlled actions implicit. Make them explicit, and treat security, lifecycle and semantic interoperability as required integration contracts.

Use cases are compositions of configured, bound module instances. Some fit one instance; others span several. A capability describes what can be done, an implementation supplies software, a module exposes a deployable contract boundary, and an instance is the running deployment. Neither one capability per process nor one use case per module is required.

## Coverage and proposed ownership

| Abstract need | Capability family | Proposed module boundary | Coverage / change |
| --- | --- | --- | --- |
| Identify and trust participants | Identity and trust | Identity provider/trust integration | Existing; humans, services and agents remain distinct principals |
| Control and remember information | Resource authority, provenance and policy | FarmWallet authority | Existing; includes structured resources, relationships and retention decisions, not just files |
| Find implementations and select running services | Discovery, configuration and binding | Registry; optional separate catalogue | Existing; offerings, implementations and instances remain distinct |
| Read/write physical information | Storage access | Storage connectors | Existing; storage location is not resource identity |
| Acquire external observations or changes | Source acquisition and subscriptions | Source adapters | Make explicit for APIs, forms, email, batches and events; need not materialise everything as a file |
| Interpret incoming information | Extraction and normalisation | Ingestion | Existing; produces proposed typed records with source provenance |
| Compute new information | Transformation, validation and analytics | Processing modules | Add explicit boundary for filtering, joins, aggregation, anonymisation candidates, rules, simulation and report rendering; an LLM is optional |
| Find and relate evidence | Indexing, graph access and retrieval | Knowledge services | Existing; several services with different query semantics may coexist |
| Execute a model | Inference | Model runtimes or external model adapters | Make explicit; a routing gateway is not the model implementation |
| Select and constrain model access | Model routing and egress control | Model gateway | Existing; enforces approved endpoint and data transmission |
| Coordinate work over time | Workflow, triggers and approval state | Coordinator | Extend beyond document jobs to schedules/events and human review; one owner per job |
| Assist a user or agent | Conversational/task assistance | Copilot | Existing; optional client of general capabilities, not the only way to invoke them |
| Carry out external effects | Controlled action execution | Action/tool adapters | Add explicit boundary for commands and business-system writes; equipment execution requires a later safety contract |
| Disclose or receive information across a boundary | Exchange and disclosure | Exchange | Existing; separates export decisions/receipts from transport and computation |
| Issue or verify attestations | Credential/signature operations | Future credential adapters | Reserve a boundary; trusted issuer and claim semantics matter independently of signature validity |
| Explain activity and operate services | Audit, health and lifecycle | Audit collector plus per-module contracts; later deployment controller | Existing; data deletion, backup and retirement responsibilities must be explicit |
| Interact with people or other applications | User/API interaction | Dashboard, CLI or external clients | Existing; background capabilities cannot depend on an open UI |

This is a capability catalogue, not a requirement to build seventeen services now. Source acquisition and controlled actions can initially be adapters in an Exchange implementation, provided their contracts and permissions remain distinct. Inference may be an externally supplied endpoint. Processing implementations may supply several functions, without a central interpreter that must understand every domain algorithm.

## Boundaries that must remain precise

- Storage provides bytes or records at a location/version; Source acquisition speaks an external protocol and tracks incoming events; Ingestion interprets content. One implementation can cover all three, but must declare any inseparable packaging.
- Processing computes proposed results; Knowledge indexes and queries them; Wallet accepts authoritative records under policy. A graph used as a derived index is not a second wallet authority.
- A Model runtime computes inference; the gateway controls routing; Copilot assembles assistance; Coordinator owns durable workflow state. A deterministic client can invoke processing without a copilot or model.
- Exchange handles disclosure to recipients. A Processing module may prepare a report or a transformed dataset, but calling a result anonymised does not grant export permission or establish a privacy guarantee.
- Action adapters enforce exact commands and permission at the effect boundary. A coordinator, trigger, approval or copilot is not permission to operate equipment. Acceptance, execution and confirmed external outcome are different states.
- An approval request/status belongs to the workflow; its authorisation meaning belongs to Wallet policy. Approval must identify the approver, operation, exact payload/version, recipient and expiry. Editing the request invalidates an earlier approval.
- Wallet defines retention/deletion policy, Coordinator tracks the work, and each storage/derived-state owner executes and acknowledges its part. Deletion is not a single central database update; exports and backup retention have explicit limits.
- Catalogues describe offerings; Registry selects instances; neither is a trust authority or grants permissions. Discovery must not silently install code or trust a new issuer.

## Resource semantics beyond documents

A resource may be a document, structured record, observation batch, dataset, model artifact, report or other typed object. Preserve stable identity, version or bounded event cursor/range, schema identifier/version, provenance, time meaning, units, coordinate/reference system where relevant, sensitivity and authority. Unbounded streams require declared retention, replay, ordering, deduplication and backpressure semantics; the initial document contract cannot simply be advertised as a stream contract.

Transformation, prediction, recommendation and official attestation are distinct output types. Every derived output records input dependencies, producing implementation/version and method/configuration reference. Proposed corrections do not mutate original evidence. Cross-wallet computation requires separate valid authority from each wallet and an explicit output ownership/disclosure policy; a multi-wallet dashboard does not merge authorities.

## Independent deployment test

Independent means a module can be installed, upgraded and replaced through declared contracts, owning its state and credentials. It does not mean dependency-free or capable of running offline. Dependencies on the wallet, source access, model endpoint or hardware must be explicit, including outage behaviour.

A module passes the architectural test only if it can run in a separate process/host, communicate without another module's private database/filesystem, authenticate through an agreed trust profile, use authorised data transfers, recover from dependency failure, and be replaced under declared migration rules. A source connector may need to run near an inaccessible device; this does not require its consumers to run there.

The [module integration profile](module-integration.md) defines the proposed admission requirements. A provider may implement several capabilities, but must say which can be independently bound and which must be co-located. The catalogue must not claim per-capability independent deployment for an inseparable implementation.

## Scope and review decisions

Retain the minimal document solution as the first implementation. The additions reserve general contracts; they do not expand the first milestone to sensors, simulators, device operation or certification.

The recommended next decisions are: accept the expanded capability families and boundaries; agree the integration profile; then specify the first small set of public contracts and conformance tests. Only after that select module frameworks and packaging. A catalogue of names alone is not proof of modularity.
