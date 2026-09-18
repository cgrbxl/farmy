# Windows deployment profile

Status: design-only; no executable package or validated target support.

Declare tested Windows versions/architectures, install/signing approach, service identity, filesystem permissions, secret/key integration and data paths. State any WSL or container prerequisite explicitly; do not infer native support from Linux tests. Test restart, locking/path behaviour and sleep/wake. Packaging remains unselected.

The profile must map the common [integration/security requirements](../../../contracts/profiles/README.md) to concrete mechanisms without changing permission or capability semantics. Supply secret references, never credentials in examples. Declare approved communication routes, state protection, recovery, upgrade and uninstall behaviour.

Before a supported release, demonstrate a clean installation of real module artifacts, authenticated permitted operations, denied unauthorised operations, background execution without the dashboard and the advertised lifecycle paths. Record exact tested versions and compatibility evidence under the [release requirements](../../../docs/releases.md).

See [deployment organisation](../../README.md). A solution may mix this profile with other independently verified instance profiles.
