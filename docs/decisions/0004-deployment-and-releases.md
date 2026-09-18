# ADR 0004 — Versioned deployments and cloud landing zones

Date: 2026-09-18
Status: Accepted requirements from the maintainer; packages and provider implementations remain unimplemented.

## Context

Consumers need versions of the core, solutions and individual modules for macOS, Windows and Linux laptops and Kubernetes within cloud providers. Cloud deployments also need explicit secrets, platform, network security and authorisation foundations.

## Decision

Treat the four environments as explicit release targets. Publish independently versioned module releases and tested solution compositions, with per-target artifacts, dependencies, compatibility and lifecycle evidence. Keep implementation, contract, package, solution, state-schema and landing-zone versions distinct. The exact manifest schema and version syntax remain M1 work.

Define a common cloud landing-zone requirement set with separately versioned, validated implementations per supported provider. Separate infrastructure provisioning and administration from module deployment and wallet data grants. A module may depend on remote services; consumers need not install the entire solution to use it.

See [release requirements](../releases.md) and [cloud landing zones](../cloud-landing-zones.md). Native installers versus container packaging, infrastructure tooling, the minimal core bundle, supported OS/CPU versions, first cloud provider and support commitments remain open.

## Alternatives

- A single universal installer: conceals platform prerequisites and cannot establish provider-specific controls on its own.
- One release number for every module: couples independent implementations and obscures contract and migration compatibility.
- Kubernetes manifests without a provider foundation: leaves critical infrastructure and operational responsibilities unspecified.

## Consequences

Linux laptops are now an explicit target alongside macOS and Windows. Compatibility and recovery must be tested per advertised target and cloud profile. The testing and maintenance matrix grows with every supported combination, so support expands incrementally from measured evidence. A target requirement is not a current support claim.

No cloud infrastructure or chargeable resource is created by this decision. The reference stack remains as accepted in ADR 0002; local SQLite does not establish a cloud replication or high-availability design.
