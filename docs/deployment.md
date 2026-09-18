# Deployment boundaries and profiles

These are target designs, not installation instructions for a working application.

| Component | Independent deployment | Multiplicity | State or location constraint |
| --- | --- | --- | --- |
| Wallet authority | Yes | Many wallets; one coherent authority per wallet | Consistent policy/resource versions; replicas possible |
| Storage connector | Yes | Many per wallet/provider | Must reach source; local connector needs filesystem access |
| Ingestion | Yes | Many by type/purpose | Must be authorised to receive plaintext and write derived results |
| Knowledge | Yes | Many collections/providers | Index, versions, permission metadata and provenance stay consistent |
| Model endpoint/gateway | Yes | Many | Data-routing policy and secret handling |
| Copilot runtime | Yes | Many | Scoped execution and tool permissions |
| Exchange connector | Yes | Many ecosystems | Recipient and onward-transfer policy |
| Workflow coordinator | Yes | Many | One coordinator per job and durable job state |
| Dashboard | Yes | Many | No requirement to stay open for execution |
| Registry/catalogue | Yes | Many | Installation registry is distinct from public offerings |
| Identity provider | Yes | Many trusted issuers | Wallet determines trust and delegation |
| Audit collector | Yes | Many | Producers durably record before asynchronous delivery |
| Deployment controller | Yes | Many targets | Privileged installation rights separate from data access |

## Mac wallet with cloud ingestion

A local connector initiates an authenticated outbound session or stages an approved snapshot. The worker receives a short-lived, audience-bound grant for the particular document version. It returns extracted data and provenance. The wallet validates and accepts the output, then dispatches indexing.

Live access requires the Mac to remain connected. Staging allows offline processing but creates another copy with a declared retention policy. An offline wallet cannot instantly distribute revocation; grant expiry and reconnection checks bound the accepted delay. Fail closed when fresh authorisation is required and unavailable.

## Deployment profiles

- Laptop: macOS or Windows, local dashboard binding by default, managed metadata and optional local AI. Container packaging is an initial candidate, not a committed dependency.
- Hybrid: laptop connector/wallet plus selected remotely deployed services. Explicit staging, offline and routing policies.
- Kubernetes: independently packaged services, persistent state, secrets integration, authenticated ingress and service communication; remote laptop connectors where needed.

Installation packages must eventually document supported OS/CPU versions, resource requirements excluding/including model inference, network reachability, initial admin setup, keys, backup, restore, upgrades and removal. No Compose file or Helm chart is supplied until runnable components exist.

## Co-location and bundling

Enforcement belongs at the resource/execution boundary. Plaintext processing must occur in an authorised trust boundary. Neither requires all services on one host. Databases may be remote, but their consistency and access responsibilities remain owned by the service. Bundles must declare which capabilities cannot be deployed separately and why.
