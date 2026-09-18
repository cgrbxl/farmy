# Common integration and security profiles

Status: design entry point, not a published protocol or certification standard.

The baseline must specify common identity/trust enrollment, secure transport, audience-bound authority, error handling, audit, time/expiry and lifecycle requirements. Capability extensions add their own data semantics, operations and limits. The first profile targets the document path with reachable Wallet authority; streams, offline grants, physical actions and credentials remain later work.

Current design sources:

- [Module integration requirements](../../docs/module-integration.md)
- [Per-hop communication and security](../../docs/module-communication.md)
- [Trust model](../../docs/security.md)
- [Release and compatibility requirements](../../docs/releases.md)

HTTP/JSON and schema tooling are accepted reference choices. Exact authentication/delegation profiles, credential lifecycle and wire schemas still need decisions and executable tests. Do not label a module compliant until a versioned profile and conformance evidence exist.

Keep these requirements common across environments. [Deployment profiles](../../deployments/README.md) identify concrete secret stores, service identities, network routes and lifecycle mechanisms; those mappings do not replace Wallet grants or alter contract semantics. SDKs can assist enforcement but do not establish conformance by themselves.
