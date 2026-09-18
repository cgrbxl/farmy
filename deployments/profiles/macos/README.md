# macOS deployment profile

Status: design-only; no executable package or validated target support.

Declare tested macOS versions and CPU architectures, install format and signing/notarisation, OS permissions, background-service identity, secret/key integration and data locations. Test sleep/wake, logout/restart, path permissions and source unavailability. Packaging and service-manager details remain unselected.

The profile must map the common [integration/security requirements](../../../contracts/profiles/README.md) to concrete mechanisms without changing permission or capability semantics. Supply secret references, never credentials in examples. Declare approved communication routes, state protection, recovery, upgrade and uninstall behaviour.

Before a supported release, demonstrate a clean installation of real module artifacts, authenticated permitted operations, denied unauthorised operations, background execution without the dashboard and the advertised lifecycle paths. Record exact tested versions and compatibility evidence under the [release requirements](../../../docs/releases.md).

See [deployment organisation](../../README.md). A solution may mix this profile with other independently verified instance profiles.
