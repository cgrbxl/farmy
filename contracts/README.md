# Capability contracts

Status: a [minimum 0.1-draft foundation](v0.1-draft/README.md) now supplies schemas, examples and executable structural/declared-compatibility checks. [UC-001 operation APIs](uc001/README.md), [UC-002 extraction/evidence/permissions/job APIs](uc002/README.md), [UC-003 source/observation APIs](uc003/README.md), [UC-004 selected-model/answer APIs](uc004/README.md), [UC-005 read-only monitoring API](uc005/README.md), [UC-006 controlled-disclosure API](uc006/README.md) and their narrow runtime checks are implemented; broader capability APIs and full conformance remain future work. Earlier examples below remain illustrative.

The [module interaction map](../docs/module-communication.md) assigns callers, receivers, operation semantics and authority checks. It is a review draft, not a published wire API.

Review the broader [capability catalogue](../docs/capability-review.md) and [module integration profile](../docs/module-integration.md) before expanding the document-path operations below. Connectivity and authentication alone do not establish semantic or migration compatibility.

The [common profiles entry point](profiles/README.md) links integration and security requirements. Implementations follow [family guides](../modules/README.md); environment-specific mechanisms belong in [deployment profiles](../deployments/README.md), not divergent copies of the wire contracts. [Conformance](../conformance/README.md) will verify implementations independently of their language or SDK.

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

A descriptor identifies the implementation and contract versions, supported deployment modes, capability multiplicity, dependencies, configuration schema, data destinations, retention assumptions, health/lifecycle operations and portability. An offering is not a deployment and a descriptor is not an access grant. Future release manifests must also declare per-target artifacts, compatibility, dependencies, migrations and required landing-zone capabilities; see [release requirements](../docs/releases.md). The foundation implements a minimal descriptor subset; complete release manifests, configuration schemas and lifecycle evidence remain requirements to deliver with runtime modules.

See [implementation.json](examples/implementation.json) and [installation.json](examples/installation.json). All endpoint names and identifiers are fictional. The JSON is illustrative, not validated by a formal schema.

## Compatibility and change

Specify required fields and extension namespaces, version negotiation, units, time representation, pagination, limits and errors before publishing a stable contract. Breaking semantic changes require a new major contract version. Substitution tests must include two independently implemented services, not two configurations of the same service alone.

ADR 0002 selects HTTP/JSON, OpenAPI/JSON Schema and initial polling for the reference path. Open choices include precise contract versions and schemas, identity/delegation protocol, later event-broker necessity and external standards mappings. Choose these through architecture decision records, without imposing a particular internal programming language.
