# Module communication and security

Status: proposed protocol/security design for architecture review. HTTP/JSON with versioned OpenAPI/JSON Schema and durable polling are accepted in ADR 0002; authentication, credential binding and offline grant details below need their own accepted security ADRs. No controls are implemented yet.

This draft specifies the first document path. The broader [capability review](capability-review.md) reserves additional acquisition, processing, inference and action contracts; they must not be claimed as supported by these document operations. All implementations also need the [module integration profile](module-integration.md).

Names in the document walkthrough identify responsibilities: Ingestion is the Document Processing specialisation, Model gateway is Model access, and Copilot is Assistance in the current [grouping proposal](module-architecture.md). These names do not create additional deployment requirements.

## Interaction contracts

Operation names describe required semantics, not final URLs or a stable API. Callers authenticate and supply explicit wallet-scoped authority; a row is not an automatic permission.

| Caller → receiver | Operations and result | Authority checked by receiver |
| --- | --- | --- |
| Client → Wallet | Register/inspect versions, request/revoke grants, accept proposed changes | Human/service identity plus explicit management or resource action permission |
| Client → Registry | Register trusted instances, inspect/change bindings | Installation administration scope; binding changes do not issue grants |
| Client/Copilot → Coordinator | Submit/status/cancel job; receive durable job ID | Workflow action, wallet, inputs and downstream authority limits |
| Coordinator/Copilot → Registry | Resolve capability binding and compatible instance | Access to binding metadata; pin revision and endpoint identity |
| Protected module → Wallet | Authorise exact action or inspect scoped grant; resolve allowed metadata | Authenticated enforcing service; request describes real initiating subject, executing actor, resource/version, destination and purpose |
| Coordinator → Ingestion | Submit/poll/cancel extraction; receive proposal references | Input read/processing and output-proposal scope, expiry and approved processor |
| Ingestion/Knowledge/Exchange → Storage | Read exact snapshot; write permitted derived/staged artifact | Specific input/output location, version, action and receiving instance; source credentials are never handed to the worker |
| Coordinator → Wallet | Submit/accept derived record referencing job, inputs and output digest | Distinct proposal and commit authority; expected-version and provenance validation |
| Coordinator → Knowledge | Index/remove accepted versions; receive per-version status | Read/index/remove scope and approved processing destination |
| Copilot → Knowledge | Retrieve evidence; receive permitted snippets and version references | Initiating user's effective access plus executing service scope; filter before returning content or sensitive metadata |
| Copilot → Model gateway | Invoke selected model with evidence references and bounded context | Model invoke permission and permitted transmission of every included data category/source to that endpoint |
| Coordinator → Exchange | Prepare disclosure / deliver approved manifest | Read for preparation, distinct export for delivery, exact recipient/purpose/content and validity |
| Producers → Audit collector | Append event batch and acknowledge IDs | Producer identity and permitted event namespace; collector cannot rewrite producer history |

External model and recipient APIs may not support Farmy contracts. The gateway or exchange adapter is the enforcing boundary before data leaves Farmy, and explicitly records the resulting trust/retention limits.

## Transport, messages and failures

Use HTTPS for network APIs with peer validation. JSON carries metadata and bounded structured results; source bytes use authenticated streaming/storage operations with size limits and digest/version verification. Do not embed large documents or credentials in job queues or event payloads. A returned transfer URL is not automatically trusted: restrict schemes/hosts/redirects and bind any transfer credential to its recipient and expiry.

Requests carry contract version, request/correlation ID, wallet ID, initiating subject and executing actor, action/purpose, input references and scoped authority. Caller-supplied identity fields are assertions to verify, not authentication. Mutations carry an idempotency key and expected state revision where applicable. Responses identify producer instance/version, accepted input versions, output references, freshness, structured errors and partial outcomes. Exact formats, size limits, pagination and deadlines remain schema work.

Scope idempotency by wallet, actor and operation; reuse with a different payload is a conflict. Bind retries to the same pinned inputs and instance unless an explicit recovery transition changes them. Re-evaluate authority before a retry; stored success does not justify disclosing a cached result to a now-unauthorised caller. Distinguish terminal denial/conflict from retryable unavailability and ambiguous external delivery.

Long operations return a durable job handle; initial clients poll. A worker tracks its execution attempt, while one Coordinator owns the overall workflow. Persist intent/outcome and reconcile after interruption; transport is not exactly-once. Cancellation is requested and acknowledged separately and cannot recall already disclosed bytes. Before committing results, recheck job validity, input revisions and authority. Late results are rejected or quarantined according to retention policy.

## Proposed authentication and authorisation model

Use three separate checks: authenticate the caller, evaluate the wallet grant, and enforce the actual operation/data destination. An approved certificate, cloud role, binding or model response is never sufficient farm-data authority by itself.

**Humans:** integrate an established OpenID Connect provider rather than implementing identity from scratch. Map issuer/subject to wallet roles; for browser/desktop sign-in, propose an authorisation-code flow with PKCE and appropriate redirect/session protections. Identity login is not a resource permission. [OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html), [OAuth security best practice](https://www.rfc-editor.org/rfc/rfc9700).

**Services:** propose mutually authenticated TLS with unique instance identities and explicit trust enrollment. Validate server identity, client identity, credential expiry and permitted trust roots; never share one administrative API key among modules. Certificate-bound OAuth credentials are an established option when an OAuth issuer is used; a client certificate and a certificate-bound token are distinct controls. Exact trust bootstrap, issuer, certificate rotation/revocation and token profile remain decisions to test. [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705).

**Grants:** propose an online-first Wallet policy API for the first implementation, with no cached positive decisions beyond the authorised operation. Each receiving module checks authority before accessing or returning protected data. Scope grants to wallet, subject/actor, action, exact resources or collection policy, input versions where needed, purpose, receiver/audience, approved processing/export destinations and expiry. An authenticated service presents the initiating delegation; it cannot supply an arbitrary user ID to gain that user's rights. Further delegation is denied unless explicitly allowed and attenuated.

Wallet policy state is authoritative. Registered enforcing services can ask for decisions without needing farm-content grants; the decision API must be bounded and disclose only necessary metadata, avoiding a circular grant-validation dependency. The trusted issuer/service mapping is bootstrap configuration, not data fetched from an untrusted request URL.

A coordinator receives only the delegation needed to execute the approved workflow; it asks Wallet for narrower per-hop authority where permitted. It cannot mint broader rights. Each recipient verifies that authority is bound to the presenting service and intended operation, rather than forwarding a user's unrestricted credential through the chain.

**Local and offline behaviour:** same-machine calls keep the same semantic checks. An authenticated OS-local transport may be a later alternative to network TLS, but localhost alone is not authentication. The initial online-first proposal fails closed when the wallet authority is unreachable. A laptop can operate without internet when its wallet and required local services remain reachable. Cloud processing while the wallet is offline requires a separately designed bounded offline credential, expiry/revocation-staleness policy and staged-copy lifetime; it is not silently covered by this proposal.

**Revocation and copies:** check at operation start, disclosure, result acceptance and bounded checkpoints for streams/long jobs. There is an in-flight race; record the decision revision/time and define maximum checkpoint delay. Already delivered plaintext cannot be recalled. Indexes, staging, model context and conversation caches must track source permissions and retention; deletion acknowledgement is not proof of erasure by an external provider.

## Walkthrough: source to searchable evidence

1. An authorised client selects a source connector and collection. The connector inventories permitted locations and the Wallet registers stable resource IDs and exact source versions. For mutable local files, materialise or verify a snapshot; refuse mixed-version reads.
2. The Coordinator records an approved job with one owner, exact inputs, binding revisions, output destinations and authority limits. Wallet authorises the selected processor and the separate propose/commit actions.
3. Ingestion obtains authorised bytes through Storage, parses within its execution limits and writes proposed derived artifacts to an approved output location. Temporary copies have explicit retention. It returns hashes and provenance; it cannot commit authoritative Wallet records.
4. The Coordinator submits the proposal to Wallet under separately granted acceptance authority, or leaves it pending for an authorised human if automatic acceptance is not permitted. Wallet validates schema, inputs, producer and job provenance and commits metadata with its audit event. Source authenticity is not inferred merely from a parser's signature.
5. The Coordinator asks each bound Knowledge instance to index accepted versions. Each instance reads authorised derived artifacts and records its own freshness/status. Partial index failure does not undo an accepted source version or pretend all indexes succeeded.

## Walkthrough: question to answer and export

1. Copilot receives a scoped user query, resolves approved Knowledge instances and asks for evidence under the intersection of initiating-user and executing-service authority.
2. Knowledge enforces permission before returning snippets, filenames, counts or other protected metadata. Indexing permission does not imply permission to reveal the index to every querier. Revoked scope is excluded even before physical index deletion completes.
3. Copilot preserves source/version references and identifies contradictions. Before invoking a model, the gateway checks the entire proposed disclosure, including user text, evidence, derived answers and reused conversation context, against the chosen endpoint and data-routing policy. External processing is a declared grant condition; it is not hidden behind ordinary resource read access.
4. The model returns untrusted text/tool proposals. Copilot validates citations and invokes only allowed tools with separate action checks; consequential writes or export follow their own authorisation path. Save any answer as a derived record only with proposal/acceptance authority and source dependencies. Disclose the answer only to an authorised caller.
5. For export, Exchange prepares an immutable preview/manifest of exact content, versions, recipient and purpose. A human approval or explicit pre-authorised policy binds to that manifest. Delivery rechecks export authority and content digest, records intent and outcome, and reports uncertain receipt honestly. Changing content or recipient invalidates the prior approval.

## Security and conformance gates

Tests must cover unknown/expired peer credentials, wrong audience, cross-wallet access, expired/revoked grants, delegation escalation, malicious retrieved instructions, unapproved model egress, stale input commits, duplicate/late jobs, secrets in logs, tampered transfer references, index removal and cached-answer revocation. Each implementation must pass these at its own boundary; a central gateway test alone is insufficient.

A service's internal persistence and credential references are private. Policy checks, audit outbox and contract validation may share implementation libraries, but independently implemented providers must be able to pass public conformance tests without importing those libraries or reading Farmy's private database schema.
