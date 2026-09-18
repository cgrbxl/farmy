# Capability contracts

Status: proposed v0.1 vocabulary and illustrative examples. No interoperable wire protocol or conformance suite is implemented yet.

## Common envelope

Requests need contract version, request/job identifier, caller identity, wallet identifier, scoped authorisation reference, purpose and input versions. Mutating requests need idempotency and expected-version semantics.

Responses need producer instance/version, result status, input and output resource references, provenance, timestamps, partial-failure details and structured errors. Confidence is optional and must identify its method; it is not automatically a calibrated probability.

## Capability operations to specify

| Capability | Operation families |
| --- | --- |
| Wallet | Resolve resources, inspect versions, propose/commit changes, inspect grants |
| Storage | List, read, inspect version, optional write/delete/change feed |
| Ingestion | Submit, inspect/cancel job, retrieve extracted result |
| Knowledge | Index/remove versions, retrieve evidence, report freshness |
| Models | Discover supported parameters, invoke, stream/cancel, report usage |
| Copilots | Describe tools and permissions, execute and inspect tasks |
| Exchange | Prepare disclosure, deliver/receive, record recipient and outcome |
| Registry | Register instance, advertise capabilities, bind, inspect health, retire |

Do not require unsupported operations such as deletion on a read-only source. Advertise feature support and reject unsupported requests explicitly.

## Descriptor

A descriptor identifies the implementation and contract versions, supported deployment modes, capability multiplicity, dependencies, configuration schema, data destinations, retention assumptions, health/lifecycle operations and portability. An offering is not a deployment and a descriptor is not an access grant.

See [implementation.json](examples/implementation.json) and [installation.json](examples/installation.json). All endpoint names and identifiers are fictional. The JSON is illustrative, not validated by a formal schema.

## Compatibility and change

Specify required fields and extension namespaces, version negotiation, units, time representation, pagination, limits and errors before publishing a stable contract. Breaking semantic changes require a new major contract version. Substitution tests must include two independently implemented services, not two configurations of the same service alone.

Open choices: transport, identity/delegation protocol, schema language, event broker necessity and external standards mappings. Choose these through architecture decision records, without imposing a particular internal programming language.
