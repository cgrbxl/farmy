# Core solution recipe

Status: core recipe remains a design baseline. [UC-001](uc001/README.md) provides an experimental, independently runnable Wallet and Connector plus a file-based binding adapter on macOS; this is not a packaged core release.

Purpose: establish resource authority and controlled service composition. Proposed members are FarmWallet, Registry and durable per-producer audit, integrated with an identity/trust provider. Select a Connector to make the core useful with a real source. Workflow is added when durable background jobs are needed; it is not hidden inside Wallet.

The first implementation card is [UC-001](use-cases/UC-001-controlled-memory.md), following the draft [working method](../../docs/working-method.md).

First case: register a synthetic local document, inspect its version, move its location without changing identity and deny an unauthorised read. A CLI is sufficient; identity and audit checks are part of the case.

Before release, pin implementations/artifacts, required operations, configuration, secret references and per-instance deployment profiles. Make trust enrollment, binding creation and grant issuance distinct. Core bundling must preserve separately runnable components and owned state. The core must not silently include every optional module.

See the [grouping and MVP cases](../../docs/module-architecture.md), [module guides](../../modules/README.md) and [target profiles](../../deployments/README.md). Only the UC-001 synthetic macOS runtime has been exercised; deployment profiles and other targets remain unverified.
