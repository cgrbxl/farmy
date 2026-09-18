# Core solution recipe

Status: design-only; not deployable.

Purpose: establish resource authority and controlled service composition. Proposed members are FarmWallet, Registry and durable per-producer audit, integrated with an identity/trust provider. Select a Connector to make the core useful with a real source. Workflow is added when durable background jobs are needed; it is not hidden inside Wallet.

First case: register a synthetic local document, inspect its version, move its location without changing identity and deny an unauthorised read. A CLI is sufficient; identity and audit checks are part of the case.

Before release, pin implementations/artifacts, required operations, configuration, secret references and per-instance deployment profiles. Make trust enrollment, binding creation and grant issuance distinct. Core bundling must preserve separately runnable components and owned state. The core must not silently include every optional module.

See the [grouping and MVP cases](../../docs/module-architecture.md), [module guides](../../modules/README.md) and [target profiles](../../deployments/README.md). All target support is currently untested.
