# ADR 0008 — Repository deliverables and environment profiles

Date: 2026-09-18
Status: Accepted repository direction and nine-family reference grouping; detailed contracts, tooling and deployment implementations remain open.

## Decision

Organise Farmy into reference architecture, public contracts/security profiles, module-family guides and reference implementations, solution compositions, environment/provider deployment profiles, conformance evidence and optional SDKs. See [repository structure](../repository-structure.md).

Maintain one common semantic/security baseline across targets. Environment profiles adapt lifecycle, identity/secrets, networking and persistence mechanisms; they cannot silently weaken common requirements. A solution may compose instances on different profiles.

The nine-family reference grouping is the current agreed baseline, subject to revision using MVP change evidence. Physical actions and other future specialised boundaries are not forced into the nine families.

## Consequences

Provide a contributor guide for each family and design recipes for core and the document path now. Add executable artifacts only when runnable implementations exist. Label current profiles and recipes design-only; this is not a claim of deployability.

Retain existing document paths as canonical references to avoid breaking published links. Independent implementations may live in other repositories. Version contracts, modules, solutions and profiles independently and test their compatible combinations.

Infrastructure planning/provisioning remains later work. Repository organisation does not select platform packaging tools, create cloud resources or approve expenditure.
