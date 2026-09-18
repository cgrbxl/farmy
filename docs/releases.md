# Versioned solutions and module releases

Status: accepted delivery requirements; no release packages or support claims exist yet. See [ADR 0004](decisions/0004-deployment-and-releases.md).

## Release units

A module release is an immutable version of an implementation, with separately identified artifacts for its supported targets. A solution release is a tested composition of exact module releases and configuration schemas. The core is a named solution whose minimal component set must be specified before its first executable release; it must not silently include all optional modules.

Consumers must be able to install the core, a complete solution, or an individual module with its declared dependencies. An individual module may bind to compatible remote services; independent deployment does not mean absence of dependencies. Bundle membership must not require synchronised version numbers or shared private databases.

Distinguish implementation version, public contract version, package version, solution version, persisted-state schema version and landing-zone version. State compatibility explicitly; matching version numbers are not evidence of interoperability. The exact version syntax and machine-readable manifest schema remain to be defined in M1.

## Target matrix

| Target | Required release declaration |
| --- | --- |
| macOS laptop | Tested macOS versions, CPU architectures, install format, signing/notarisation procedure, permissions, background service lifecycle and secret-store integration |
| Windows laptop | Tested Windows versions and architectures, install format and signing, service identity, filesystem permissions, secret-store integration, and any explicit WSL/container prerequisite |
| Linux laptop | Tested distributions and versions, architectures, package/runtime dependencies, service manager, filesystem permissions and secret-store integration |
| Cloud Kubernetes | Tested Kubernetes versions, node OS/architectures, installation package, compatible provider landing-zone versions, required APIs/add-ons, storage and identity integrations |

These are four target environments, grouped as three laptop operating systems and cloud Kubernetes. Hybrid is a composition across targets, not a fifth operating system.

All four are delivery targets for the Farmy core and reference modules. A release must mark each target as tested, experimental, unsupported or not yet tested, with limitations and evidence. Independent contributors may offer narrower support, but consumers must see the gaps before selection. Platform-specific hardware, model requirements and genuine co-location constraints must be disclosed. Do not infer Linux laptop support from a Linux container or Windows support from macOS testing.

## Consumer release manifest requirements

Each future release must provide:

- Identity, publisher, immutable version, source revision, licence, artifact locations, digests, signatures and verification instructions, plus dependency inventory and build provenance.
- Supported target matrix, public contract ranges, exact dependencies in a solution lock manifest, configuration schema versions and compatible landing-zone profiles.
- CPU, memory, disk and optional accelerator requirements, separating service overhead from model inference; required accounts, ports, endpoints and outbound destinations.
- Service identities, minimum installation/runtime privileges, secret references, data categories, processing destinations and retention requirements. No secret values belong in manifests.
- Install, configure, start, stop, health check, upgrade, migrate, back up, restore and uninstall instructions. Define whether uninstall preserves data and require explicit selection for deletion.
- Known limitations, security advisories, support owner, tested date, maintenance/end-of-support policy and accepted upgrade paths. Do not promise a support period until resourcing is agreed.

A solution release pins tested modules and package digests; deployment records capture what actually ran, with secret references only. Provider substitution requires contract conformance and declared migration, not merely an image change.

## Lifecycle acceptance

Before labelling a target supported, test installation on a clean target, least-privilege operation, authorised and denied requests, persistence across restart, and execution after the dashboard closes. Laptop tests include sleep, wake, lost connectivity, expired grants and resumed jobs; closing the dashboard does not imply work continues while the machine sleeps.

Test an upgrade from each advertised predecessor, state migration, backup restoration and interrupted-job reconciliation. State explicitly when downgrade is unsupported or requires restoring a backup; replacing an executable does not reverse a database migration. Verify artifact signatures, dependency compatibility and permissions before activation. Installation must not create farm-data grants implicitly.

Cloud releases additionally pass the [landing-zone acceptance checks](cloud-landing-zones.md). Release tests must run against each claimed provider/profile combination. No universal cloud support claim follows from a generic Kubernetes package.
