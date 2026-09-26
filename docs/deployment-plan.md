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
| L3 — Functional composition | Wallet authority behind Drive, Copilot, Hub and Control views | One bounded question uses selected source evidence and an authorised model; evidence and destination visible; components remain independently replaceable |
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
