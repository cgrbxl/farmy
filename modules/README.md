# Module families

Status: reference grouping and contributor guides, plus narrow experimental implementations for [UC-001](../solutions/core/uc001/README.md) and [UC-002](../solutions/document-path/uc002/README.md). No family is complete and no production deployment package is supplied.

The [technical architecture](../docs/module-architecture.md) defines ownership and change scenarios. A family can have several independently supplied implementations; it is not one universal process. Each guide defines what belongs inside, what stays outside and the first useful increment.

| Family | Guide |
| --- | --- |
| FarmWallet | [Authority and resource memory](wallet/README.md) |
| Registry | [Discovery and binding](registry/README.md) |
| Workflow | [Durable coordination](workflow/README.md) |
| Connectors | [Storage and source access](connectors/README.md) |
| Processing | [Extraction and computation](processing/README.md) |
| Knowledge | [Index and retrieval](knowledge/README.md) |
| Model access | [Model integration and routing](model-access/README.md) |
| Assistance | [Copilot and evidence synthesis](assistance/README.md) |
| Exchange | [Controlled disclosure](exchange/README.md) |

Future reference implementations may live under their family directory; external repositories are equally valid. Each implementation owns its build, persistence/migrations, configuration and release lifecycle. Public contracts remain in [contracts](../contracts/README.md), optional shared helpers in [sdk](../sdk/README.md), composition in [solutions](../solutions/README.md), and environment packaging in [deployments](../deployments/README.md).

Do not create nine compulsory server processes merely to match this directory layout. A core distribution may bundle independently runnable components while preserving their public boundaries and owned state. Identity infrastructure and model runtimes may be external; audit is required at every producing boundary, with an optional collector. Physical actions, credentials and deployment administration remain later specialised boundaries.
