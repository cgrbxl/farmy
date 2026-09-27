# Deployable Farmy — agreed implementation plan

Agreed 2026-09-26. Farmy remains an evolving modular prototype whose components require real permission, persistence and failure handling. Sample farm data is an optional exploration fixture, not a core dependency.

## Fixed requirements

- A selected solution must run locally without a Farmy-operated cloud login, registry, coordinator, gateway or storage service.
- Hosted modules, external sources and trust infrastructure are explicit dependencies chosen by the solution/operator. Document online requirements and unavailable/offline behaviour per dependency.
- Cloud exploration uses a dedicated Farmy **project in the existing Scaleway account**. No onmygarage resources, credentials, deployment lifecycle or platform services are dependencies.
- Participants can deploy the same module artifacts in their own projects/accounts/infrastructure. The shared test environment is optional.
- Infrastructure rights never imply Wallet data grants. Package installation does not grant source access; the operator explicitly selects the source at initialisation.
- Kubernetes is an optional deployment profile, not the base runtime or prerequisite for participation.

## Delivery order and acceptance

| Milestone | Deliverable | Acceptance before claiming completion |
| --- | --- | --- |
| L1 — Persistent local runtime | Operator-selected directory, durable Wallet/Connector/client state; CLI lifecycle and isolated local identities | Restart retains exact copies and revocations; duplicate start rejected; service failure stops the composition; credentials rotate without changing resource identities; no cloud needed |
| L2 — Installable Mac release | Versioned self-contained artifact and user installation; then Homebrew distribution and login service integration | Run outside checkout; explicit data location; install/upgrade preserves state; backup/restore verified; uninstall retains data; supported OS/architecture recorded |
| L3 — Functional composition | Copilot, Wallet, Library and Connect views | One bounded question uses selected source evidence and an authorised model; evidence and destination visible; components remain independently replaceable |
| C1 — Optional cloud processor | One versioned stateless processing module and Scaleway project provisioning recipe | Reviewed project/region/budget/IAM plan; Mac initiates bounded request; authentication, denial, timeout, retry and retention tested; local provider remains usable |
| C2 — Independent deployment | Repeat C1 in another separately configured project or participant account | Same artifacts/contracts; no shared test-environment credentials or hidden endpoints required |
| C3 — Optional participant environment | Reviewed module onboarding, isolated identities/state/secrets, quotas and teardown | Deployment access confers no Wallet authority; isolation and recovery verified before broader participant hosting |

L1 and L2 begin now. Complete the persistent installable baseline before expanding Copilot. Do not represent an installer draft or local-source install as a published Homebrew release. A packaging milestone is not production readiness.

## Local lifecycle choices

The initial local composition retains the tested Wallet and generic read-only directory Connector, with a replaceable browser client. Source bytes remain outside the runtime's data directory. Managed copies and private service state live in a dedicated operator-owned workspace, never under the installed software tree.

A local process supervisor owns the service processes and binds only to loopback. It must stop children on orderly termination and detect an unexpectedly exited service. Independent local runtime identities are regenerated at startup and periodically while running; this replaces transport credentials, not source/resource identities or user grants. Browser owner access is a local operator credential and must remain separate from consumer access.

Owner source-reading authority is explicit at initialisation. It may be maintained while the operator's local composition runs. Consumer grants are never silently renewed. Persistent operation must not depend on a demo's import-time owner-read expiry. Backups are stopped, consistent copies of service-owned state; restoration targets a new empty workspace and creates fresh transport/browser credentials.

## Cloud design to resolve at C1

Serverless Containers are a candidate for the first HTTP processing module; Functions may suit event handlers. Current SQLite/snapshot state cannot live on ephemeral serverless filesystems. Stateful cloud modules require a separately tested storage profile, not a filesystem assumption or one shared writable database.

Select connectivity and offline semantics explicitly. A sleeping Mac is not a reachable server. Begin with outbound, bounded requests from the Mac; do not expose the local Wallet or source directory publicly to make the demo work.

No infrastructure is provisioned by this plan. Prepare the concrete resource and cost plan before applying cloud changes.

## Progress recorded 2026-09-26

L1 has a tested persistent runtime with eight lifecycle tests. L2 has a standalone offline installer, a real user-level Mac installation/login service and a verified compatible development-build replacement. Homebrew install verification is blocked by this Mac’s Xcode prerequisite; the formula is prepared but not published. See the [Mac profile](../deployments/profiles/macos/README.md) for exact evidence and remaining lifecycle/security work. L3 and cloud milestones remain pending.

### L3 interface foundation — 0.1.1

The installed persistent client now separates Drive, Copilot, Hub and Control. Drive retains the real preview/admission/read/grant/revoke journeys. Copilot offers two bounded, refreshed workspace-record questions: inventory and recorded consumer grants. These are deterministic client summaries, not AI answers or document analysis. Grant receipts are explicitly not live authorisation decisions and may have expired. Hub describes the configured composition, not continuous health; Control explains actual authority and storage boundaries without implying editable configuration.

L3 acceptance is **not complete**. Next implement an explicit processing/model permission for one selected immutable managed copy, with destination confirmation, bounded evidence, revocation checks before release, and provider replacement tests. Existing owner read authority must not silently become processing-module authority. Then connect that vertical slice to Copilot. No cloud infrastructure is needed for this step.

Validation for 0.1.1: eight local lifecycle tests passed; JavaScript syntax checked; standalone build installed and login service restarted; browser verified all four views, 57 source entries / 53 preview-eligible entries and three retained managed copies. Both bounded workspace questions refreshed their records successfully. Homebrew and cloud status remain unchanged.

### Identity and sharing prerequisite — 0.2.0

Prioritised following the owner's feedback: editable managed-copy policies and a separate local consumer application with persistent keys, pinned public identities and its own receipt store. See [identity and sharing](identity-and-sharing.md). The existing TLS profile performs real key-possession authentication; the UI does not claim that local pairing verifies a person or organisation. Browser credentials remain bearer links. L3 model-backed acceptance, QR disclosure and public registry integration remain pending.

### Navigation revision — 0.2.1

Current navigation is **Copilot · Wallet · Library · Connect**, replacing the earlier Drive/Hub/Control labels described in historical progress above. See [four-view organisation](functional-workspace.md) for responsibilities, module placement and implemented/planned boundaries. Wallet and Library use the same policy actions; they are not separate stores or authorities.

### Messaging draft iteration — 0.3.0

Connect now hosts local channel profiles, exact sender/recipient lists and a persistent draft-only scheduler. This is a reusable embedded Workflow component, not a claim of live email/SMS/WhatsApp/Signal integration. No message body ingestion, automatic document read, model generation or external sending occurs. See [messaging scope and responsibilities](messaging.md). L3 model-backed acceptance and cloud deployment remain pending.
