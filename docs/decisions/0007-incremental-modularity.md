# ADR 0007 — Incremental delivery and evidence-based module boundaries

Date: 2026-09-18
Status: Accepted MVP approach and broad capability coverage; exact module grouping remains proposed for review.

## Context

The maintainer accepted broad abstract capability coverage with incremental implementation through concrete use cases. The main concern is a useful balance: additions should not routinely require changes throughout the system, and no module should accumulate every capability.

## Decision

Use small, concrete end-to-end use cases as implementation and architecture tests. Expand or improve capabilities based on those results. Treat modularity as an outcome measured by independent change/replacement, state ownership and explicit security/connectivity contracts, not by maximising or minimising process count.

The proposed [nine-family grouping and change scenarios](../module-architecture.md) are the next review target. Broad capability coverage does not mean every capability needs its own module or belongs in the first implementation. Use cases may compose several instances.

## Consequences

Record which implementations, contracts, configurations and migrations each increment changes. Existing-capability extensions should normally stay within one implementing family plus composition changes. Genuinely new semantics may require coordinated contract evolution; zero cross-module changes is not a credible universal promise.

Do not build a general plugin execution platform, arbitrary workflow language or provider catalogue before the first use case requires it. Keep trust, state and public contract boundaries testable even when components ship together. Revisit boundaries using evidence from actual changes, failures and substitution tests.

Scaleway and platform-specific deployment remain deferred until the module design and working path justify them.
