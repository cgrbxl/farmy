# Deployment profiles and packages

Status: profile requirements only. No installer, container package, Helm chart or infrastructure-as-code implementation is supplied.

| Profile | Role | Current state |
| --- | --- | --- |
| [macOS](profiles/macos/README.md) | Laptop service lifecycle, identity, secrets and filesystem integration | Design-only / untested |
| [Windows](profiles/windows/README.md) | Laptop service lifecycle, identity, secrets and filesystem integration | Design-only / untested |
| [Linux](profiles/linux/README.md) | Laptop distribution/runtime/service integration | Design-only / untested |
| [Kubernetes](profiles/kubernetes/README.md) | Workload packaging and cluster capability requirements | Design-only / untested |
| [Scaleway](providers/scaleway/README.md) | First provider mapping and landing-zone implementation | Selected / unimplemented |

Modules expose environment-independent contracts. These profiles provide the mechanisms needed to meet them. Cloud deployments combine a Kubernetes workload profile with a validated provider foundation; Kubernetes alone is not the landing zone. A hybrid solution assigns a profile to each instance and explicitly configures communication between them.

The eventual profile contract must declare supported versions/architectures, service identity, secret/key references, storage paths/capabilities, secure endpoints, dependency reachability, health, startup/shutdown, backup/recovery, upgrade/removal and operational responsibilities. Changes to network or deployment privileges must not create farm-data grants.

Keep module release artifacts separate from environment configuration and provider infrastructure. Each owns independent versions and compatibility declarations. Implement tooling after module needs are known; do not promise native installers, container dependencies or a specific IaC tool prematurely.

See [deployment requirements](../docs/deployment.md), [landing-zone requirements](../docs/cloud-landing-zones.md) and [release acceptance](../docs/releases.md). No account access, infrastructure changes or spending are authorised by these documents.
