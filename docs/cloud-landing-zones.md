# Cloud provider landing zones

Status: requirements only. Scaleway is selected as the first provider in [ADR 0005](decisions/0005-scaleway-first-provider.md). No infrastructure is provisioned or cloud security certified.

A Farmy landing zone is the versioned infrastructure foundation required to run a declared solution or module safely within a cloud environment. Each supported provider needs an explicit implementation mapping these requirements to named services, settings, permissions and tests. A Kubernetes application package alone is not a landing zone.

Implementation is deferred until capabilities, communication/security and module technical design are consolidated; see [ADR 0006](decisions/0006-architecture-first.md).

## Layers and ownership

1. Provider foundation: account/project/subscription boundaries, region, network, identity, keys, secrets, logging, state and budgets.
2. Kubernetes platform: cluster, node pools, access controls, enforced network policy, storage integration and required add-ons.
3. Farmy workload: versioned modules, service identities, bindings, model profiles and independently issued wallet grants.

The cloud operator owns the first two layers; module operators deploy workloads within granted boundaries; the wallet owner controls Farmy access grants. Document the actual people or teams responsible, including incident response, upgrades and recovery. Infrastructure administrators can have technical access to underlying systems: separation of application permissions does not make the hosting operator unable to read plaintext.

## Required provider profile

| Area | Explicit requirements and deliverables |
| --- | --- |
| Scope and ownership | Named provider and supported regions, account/project boundaries, environment separation, tenancy model, responsibilities, residency constraints and prerequisites |
| Provisioning | Versioned infrastructure-as-code package, pinned tool/provider versions, reviewed plan, minimal bootstrap permissions, protected and locked state, drift detection, resource ownership and teardown policy |
| Network | Address ranges, subnet/routes, private/public endpoints, restricted cluster administration, ingress/TLS/DNS, firewall rules and approved egress paths; declare required internet access and laptop connectivity |
| Cluster | Supported Kubernetes versions and upgrade policy, node types/architectures, quotas, patching, admission controls, workload isolation and compatible add-ons with their owners |
| Human access | Federated identity, MFA policy, least-privilege cloud roles and Kubernetes RBAC, audited emergency access and revocation process |
| Workload access | Per-service identities mapped to provider roles using short-lived credentials where supported; minimum access to named secrets, keys, storage and APIs; document any exception and rotation path |
| Keys and secrets | Named key-management and secret services, key ownership/recovery, encryption coverage, runtime delivery, rotation/revocation and auditing; no credentials in repository files, images or exported configuration |
| Data services | Required versus optional databases, object stores, queues and registries, versions/features, encryption, private access, backup policy and service-owned state; no implicit shared writable database |
| Operations | Security/audit logs with access and retention controls, sensitive-data redaction, metrics, alerts and response ownership, image provenance/vulnerability policy and certificate renewal |
| Recovery and cost | Recovery objectives and tested restore, key recovery, failure assumptions, regional limitations, cost estimate with assumptions, budget alerts, scaling limits and teardown costs |

Every provider implementation must include a requirements-to-services mapping and exact role/action scopes. A required control without a supported implementation blocks that profile; do not silently weaken the common baseline. Bring-your-own infrastructure must pass the same checks and record which resources are externally managed.

## Authorisation boundaries

Cloud IAM controls cloud resources. Kubernetes RBAC controls Kubernetes API actions. FarmWallet grants control farm-resource access, purpose, audience and operations. These are distinct layers; none substitutes for the others. Permission to deploy a module must not automatically allow reading farm records or invoking an external model.

Network isolation complements these controls. Require default-deny workload ingress/egress with declared exceptions for DNS, identity, secrets, storage, telemetry and approved model endpoints. Verify enforcement using the selected networking implementation: merely creating NetworkPolicy objects is insufficient. Standard NetworkPolicy is not a complete domain-based or application-layer egress control; the provider profile must specify any additional gateway/proxy/firewall required for approved destinations. See [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/).

Kubernetes Secret objects alone do not demonstrate encrypted storage or safe access. Verify actual encryption-at-rest configuration, access rules and the selected external secret integration. See [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).

Require restricted workload privileges, an explicit tenancy/isolation design and controlled administrative access, drawing on the [Kubernetes security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/). Exceptions require a documented reason, scope and compensating controls; namespaces alone must not be presented as a complete hostile-tenant boundary.

## Bootstrap and handoff

The future deployment flow must validate provider/account/region, permissions, quotas, network conflicts and estimated costs, then present the infrastructure change plan. Applying that plan is a separate authorised infrastructure operation; this document authorises no provisioning or expenditure.

Create or validate the provider foundation, establish the cluster and its controls, then deliver a versioned non-secret environment descriptor to the module installer. It identifies endpoints, trust/identity references, secret-store references, storage capabilities, policy baseline and profile version. Bootstrap credentials stay outside workload configuration and are reduced or revoked after handoff. Farm grants are issued separately for selected bindings.

Updates must check compatibility between landing zone, Kubernetes, add-ons and deployed modules before applying changes. Preserve existing customer infrastructure unless explicitly managed; uninstalling one module must not destroy shared networking, keys, clusters or retained data.

## Acceptance evidence per provider and version

Demonstrate reproducible provisioning or validation, clean module installation, authenticated access, denied unapproved ingress/egress, rejected unauthorised secret access and denied cross-wallet retrieval. Verify a deployer receives no automatic wallet grant. Test workload identity, secret rotation, grant revocation, backup/key recovery, cluster/workload upgrade and declared rollback paths. Record time, versions, settings and results without exposing secrets.

For laptop-to-cloud workflows, test loss of connectivity, staged-copy expiry/deletion, bounded revocation delay and recovery without granting new access. Record residual risks and manual prerequisites. A passed installation test is not proof of the security requirements.

## Rollout choices still open

Scaleway is the first selected provider; see the [Scaleway plan](providers/scaleway.md). Select its project and region, plus a tenancy model, operational owner, budget and infrastructure tooling. Add subsequent providers through independently tested mappings to the same requirements. Do not claim all-provider support or publish placeholder infrastructure as deployable.
