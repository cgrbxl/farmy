# Repository structure and delivery model

Status: organisation and draft structural/compatibility validator established; module runtimes, executable deployment templates, SDKs and runtime conformance runners are not yet supplied.

## Separation of responsibilities

Shared capability meaning, resource authority and security requirements are environment-independent. Deployment profiles map those requirements to concrete identity, secret storage, service lifecycle, networking and persistence mechanisms. A profile must meet the shared requirements or declare the combination unsupported; it must not silently weaken them.

| Location | Owns | Current maturity |
| --- | --- | --- |
| [docs](architecture.md) | Reference architecture, rationale, roadmap and ADRs | Architecture/design documents |
| [contracts](../contracts/README.md) | Public operations, schemas, semantics and common integration/security profiles | Draft foundation schemas/examples; capability APIs pending |
| [modules](../modules/README.md) | Family-specific implementation guidance and future reference implementations | Nine family guides; no runtimes |
| [solutions](../solutions/README.md) | Compositions of module instances for concrete use cases | Core and document-path design recipes; not deployable |
| [deployments](../deployments/README.md) | OS/Kubernetes packages and provider landing-zone adapters | Target/profile requirements; no installers or infrastructure code |
| [conformance](../conformance/README.md) | Provider-independent contract, security, lifecycle and composition checks | Runnable foundation structural checks; runtime suite pending |
| [sdk](../sdk/README.md) | Optional integration clients and helpers | Scope defined; no library |
| [scripts](../scripts/check_docs.py) | Repository maintenance checks | Existing Markdown-link/JSON check |

Existing architecture documents remain at their published paths. New entry points link to them rather than duplicating their content. A family guide owns its implementation boundary; public wire requirements belong in contracts, and profile mechanisms belong in deployments. If guidance conflicts, resolve it through an ADR rather than maintaining divergent copies.

## How a deployable solution will be assembled

A versioned solution recipe selects capabilities, implementations, dependency features and configuration. A release resolves those selections to immutable artifacts/digests, accepted contract/security profiles and a tested lock manifest. Each instance receives a supported deployment profile; a hybrid solution can place different instances on different profiles. Bindings and separately authorised grants join them.

Deployability therefore belongs to a tested combination of solution release, module releases, contract/security profiles and environment/provider versions. A design recipe, successful schema validation or generic Kubernetes package alone cannot establish that claim. See [release requirements](releases.md).

Keep executable manifests beside the owning solution or deployment profile when real artifacts exist. Do not add placeholder Compose/Helm/Terraform files or commands that appear to install a nonexistent application. Exact tooling, manifest syntax and directories for generated artifacts remain implementation decisions.

## Contributor path

1. Read the architecture and choose the relevant module family guide.
2. Implement the required public capability contract and common security/integration profile, using optional SDKs or an independent implementation.
3. Declare dependencies, features, processing destinations, secret references, lifecycle and migration. Run public conformance checks once available.
4. Supply independently runnable artifacts for each claimed target, with profile-specific evidence and limitations.
5. Add or update a solution recipe and demonstrate an end-to-end use case, including failure/denial and replacement cases.

Independent implementations can live in external repositories and be referenced by immutable releases. This repository does not impose a language, shared private database or compulsory runtime library. No reference implementation is conformance-certified simply because it lives here.

## Maturity and versions

Label artifacts as design-only, experimental or tested with their precise scope. Current recipes and profiles are design-only. Before promotion to deployable, require executable artifacts, resolved dependencies, documented installation/secrets, positive and negative integration tests, restart/upgrade/restore evidence and supported target versions.

Version contracts, implementations, solutions and deployment/provider profiles independently. Record compatibility instead of requiring all modules to share one release number. Keep real farm data, secrets, cloud account identifiers and infrastructure state outside public examples.
