# ADR 0009 — Minimum interoperable module foundation

Date: 2026-09-18
Status: Draft implementation baseline established at the maintainer's request. Structural validation is implemented; runtime security and operation APIs remain unimplemented.

## Decision

Define a small environment-independent integration foundation with versioned module, instance, binding, resource-reference and message schemas. Put target-specific trust/secret/state/network references in a separate environment descriptor. Keep actual operation semantics in capability contracts delivered with use cases.

Use JSON Schema Draft 2020-12 for these documents, strict exact contract matching during the draft phase and explicit capability features. The current connectivity profile is direct HTTPS. Propose mTLS plus online Wallet authorisation as the first common service security profile; profile declarations are not enforcement. Exact enrollment, credential lifecycle and delegation need runtime design/verification in UC-001.

See the [foundation](../../contracts/v0.1-draft/README.md) and [runnable validator](../../conformance/foundation/README.md).

## Alternatives and limits

One cloud-specific protocol would couple semantics to deployment. A universal message bus or plugin platform would add machinery before the first use case. A single generic payload cannot establish semantic compatibility. Therefore the foundation stays small, with typed capability contracts to follow and no mandatory broker, SDK or shared private database.

The checker proves document shape and declared compatibility only. It does not prove identity, grant enforcement, operation semantics, reachability, migration, provider compatibility or support for any target. Untested declarations stay explicitly untested. No infrastructure is provisioned.
