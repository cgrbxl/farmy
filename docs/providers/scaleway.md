# Scaleway landing-zone plan

Status: first provider selected by the maintainer on 2026-09-18. Service mapping is a design proposal, not a deployable or validated profile. No account access, resources or costs have been authorised by this selection.

Scaleway is the first implementation target because the maintainer already knows the provider. The [common landing-zone requirements](../cloud-landing-zones.md) still apply; Farmy contracts remain provider-independent.

## Initial service mapping to validate

| Requirement | Proposed Scaleway mapping | Evidence needed before support |
| --- | --- | --- |
| Kubernetes | Managed Kubernetes Kapsule | Selected region, supported cluster version, node size/architecture, quotas, upgrade and recovery tests |
| Network | VPC and Private Network; explicit ingress and outbound routing | Control-plane access restrictions, private node connectivity, enforced workload policy, approved egress and laptop access tests |
| Operator access | Scaleway IAM plus Kubernetes RBAC | Named administrator/deployer/read-only roles, minimum permission sets, federation/MFA, audit and revocation tests |
| Runtime secrets | Secret Manager with a supported Kubernetes integration | Per-workload access scope, bootstrap credentials, rotation, deletion, failure behaviour and secret-copy inventory |
| Data and artifacts | Evaluate Object Storage for source/staging/backups, Block Storage for required volumes and Container Registry for artifacts | Regional availability, access scope, encryption, retention, backup restoration and portability; no automatic subscription to all services |
| Key custody and operations | Evaluate Key Manager, logging/monitoring integrations and billing controls | Supported integrations, encryption boundaries, key recovery, redaction/retention, incident owner and cost estimate |

Kapsule and its Private Network integration are documented by Scaleway; a private network must not be treated as proof of restricted application egress or private-only API access. Test the selected topology. [Scaleway network guide](https://www.scaleway.com/en/docs/kubernetes/reference-content/secure-cluster-with-private-network/)

Scaleway documents IAM integration with Kubernetes RBAC. FarmWallet grants remain a third, independent authorisation layer. Do not give workloads deployment credentials or infer data access from cluster access. [IAM and RBAC guide](https://www.scaleway.com/en/docs/kubernetes/reference-content/set-iam-permissions-and-implement-rbac/)

Secret Manager has documented Kubernetes integrations: External Secrets creates Kubernetes Secret objects, while the Secret Manager CSI provider can mount secret content as files without intermediary Secret objects. Select one after checking workload needs, credential delivery and rotation behaviour. Do not assume Kubernetes service accounts automatically obtain short-lived Scaleway credentials; establish the supported mechanism and document any scoped API-key exception. [CSI provider guide](https://www.scaleway.com/en/docs/secret-manager/api-cli/deploying-secret-manager-csi-provider-kubernetes/), [External Secrets guide](https://www.scaleway.com/en/docs/secret-manager/api-cli/external-secrets)

The provider manages parts of the platform; Farmy operators still own workload security and cluster policy responsibilities. Record the operational split against [Scaleway's shared responsibility model](https://www.scaleway.com/en/docs/kubernetes/reference-content/kubernetes-shared-responsibility-model/).

## First validation sequence

1. Select an existing or dedicated project, region, environment purpose, tenancy model, operational owner and monthly budget. Inventory existing resources read-only when access is authorised.
2. Produce a versioned infrastructure design and costed change plan, with exact service versions, IAM scopes, network routes and bootstrap requirements. Choose infrastructure tooling before implementation.
3. Provision only after the concrete plan is authorised. Validate network and identity controls using synthetic data, including denied access and secret rotation.
4. Install the first runnable Farmy module independently; test its wallet binding, explicit grants, restart, backup/restore and upgrade. Exercise Mac-wallet/cloud-ingestion connectivity when the document path exists.
5. Publish a tested profile and compatibility evidence only after the common acceptance checks pass. The first development profile must not be presented as a production or high-availability deployment.

No region, cluster size, budget, runtime secret integration or infrastructure tool is selected by this plan. Managed databases and model services remain optional needs-driven choices. Local reference SQLite does not imply a shared or replicated cloud database design.
