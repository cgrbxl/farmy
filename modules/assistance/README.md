# Assistance

Status: [UC-004](../../solutions/assisted-answer/uc004/README.md) implements a bounded crop-answer service with independently checked citations and retained answers. The [0.4-draft interface](../../contracts/uc004/README.md) is experimental; broader family capabilities remain unimplemented.

## Responsibility and state

Task interpretation, evidence synthesis, citations, scoped conversation and constrained tool proposals.

Owned state: Conversation/task state with source dependencies and derived answer provenance.

Boundary: Not the sole client of capabilities, a job engine or an unchecked action executor.

## First increment

Answer a question from permitted evidence, validate references and reject document-driven privilege escalation.

Required contract areas: Knowledge evidence, Model access, Registry and authorised Workflow/tool requests.

Change-locality test: Changing knowledge/model instances should use compatible bindings; specialised user interaction may evolve independently.

## Integration and environment obligations

Scoped session storage, selected capability endpoints and identity; no requirement that the dashboard stay open.

Follow the common [integration profile](../../docs/module-integration.md), [communication/security design](../../docs/module-communication.md) and [conformance plan](../../conformance/README.md). Advertise implemented features, dependencies and limits. Missing grants, incompatible contracts and unreachable authority fail according to the public profile, not silently.

Supply configuration with secret references, owned persistence/migrations, health/readiness, bounded retries/cancellation where relevant, audit and backup/restore/removal behaviour. Environment-specific mechanisms belong in [deployment profiles](../../deployments/README.md); capability meaning and permission requirements remain common. Per-target support is untested until evidence exists.

## Operational monitoring

[UC-005](../../solutions/operations/uc005/README.md) adds an optional, receiver-authorised [summary API](../../contracts/uc005/README.md). This implementation owns its count queries and exposes only metadata/recent outcomes to an explicitly enrolled monitor. Existing compositions keep monitoring disabled; no private database is shared.
