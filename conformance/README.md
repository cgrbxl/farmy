# Conformance and composition tests

Status: test plan only; no executable conformance suite exists. The existing repository script checks Markdown links and JSON parsing only.

| Layer | Required evidence |
| --- | --- |
| Contract | Valid/invalid fixtures, version/features negotiation, data semantics and structured errors |
| Security | Unknown identity, wrong wallet/audience, expired/revoked grants, forbidden delegation/egress and sensitive-data leakage denied |
| Module lifecycle | Duplicate jobs, partial failure, retry/cancellation, restart, migration, backup/restore and removal semantics |
| Composition | Synthetic core/document cases and independently implemented provider replacement while unaffected modules keep their versions |
| Deployment | Installation and controls verified for each claimed OS/architecture or Kubernetes/provider profile |

Create fixtures and tests alongside the first accepted contracts and module implementation; avoid tests that merely mirror a private implementation. An independently implemented provider must be able to run the suite without a shared database or mandatory Farmy SDK. Reference code is subject to the same tests.

Organise executable tests by versioned public contract/profile when those exist. Keep test data synthetic and expected results explicit. Attach results to exact implementation, contract, solution and deployment-profile versions; passing one layer does not imply the others pass.

Use [modularity change scenarios](../docs/module-architecture.md), [integration requirements](../docs/module-integration.md) and [security requirements](../docs/security.md). The initial [document recipe](../solutions/document-path/README.md) is the first composition target.
