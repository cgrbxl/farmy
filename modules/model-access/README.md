# Model access

Status: [UC-004](../../solutions/assisted-answer/uc004/README.md) implements a pinned local Ollama adapter with independently authorised evidence and invocation journal. The [0.4-draft interface](../../contracts/uc004/README.md) is experimental; broader family capabilities remain unimplemented.

## Responsibility and state

Profiles, endpoint adapters, parameter/feature validation, authorised routing and usage records.

Owned state: Endpoint/secret references, model profiles and minimal invocation metadata.

Boundary: Not the model runtime or copilot; cannot issue tool permissions or silently fall back to another provider.

## First increment

Invoke an explicitly selected endpoint and reject unauthorised routing or unsupported parameters.

Required contract areas: Model invocation/features plus destination, data-category and source-authority checks.

Change-locality test: A compatible provider adds an adapter/profile without changing Assistance; new model features may need contract negotiation.

## Integration and environment obligations

Local/remote model reachability, secret resolution, allowed egress and bounded request/stream lifetime.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.

## Operational monitoring

[UC-005](../../solutions/operations/uc005/README.md) adds an optional, receiver-authorised [summary API](../../contracts/uc005/README.md). This implementation owns its count queries and exposes only metadata/recent outcomes to an explicitly enrolled monitor. Existing compositions keep monitoring disabled; no private database is shared.

## Future interactive modes

See the [interactive module backlog](../../docs/interactive-modules.md) for staged user interfaces, family ownership and acceptance criteria. These modes are planned; the current monitoring interface remains read-only.
