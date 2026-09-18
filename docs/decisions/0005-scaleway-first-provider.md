# ADR 0005 — Scaleway as first cloud provider

Date: 2026-09-18
Status: Accepted provider selection; landing-zone implementation remains planned.

## Context

ADR 0004 requires independently validated cloud provider landing zones. The maintainer selected Scaleway first because it is already familiar.

## Decision

Develop and validate the first Farmy cloud landing zone on Scaleway. Begin with the [Scaleway service mapping and validation plan](../providers/scaleway.md), using the common security, release and recovery requirements. Kapsule is the proposed managed Kubernetes service; exact configuration and supporting integrations remain subject to validation.

## Alternatives

Starting on another provider would add unfamiliar operational work. Implementing multiple providers simultaneously would expand the validation burden before the first profile works. Both are deferred, not excluded.

## Consequences

Prioritise Scaleway documentation and acceptance evidence. Preserve provider-independent contracts and isolate provider-specific infrastructure. Account/project, region, budget, tenancy, operational ownership and tooling remain unresolved. Provider selection does not authorise provisioning, access changes or spending and does not constitute a support claim.
