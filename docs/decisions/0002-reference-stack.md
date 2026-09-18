# ADR 0002 — Reference implementation stack

Date: 2026-09-18
Status: Accepted by the maintainer on 2026-09-18. No runtime implemented.

## Context

The first implementation must test independent deployment and replacement without imposing one language or a shared database on contributors. A small reference implementation should minimise infrastructure while preserving service boundaries.

## Decision

Use Python for reference services, HTTP with JSON for request/response boundaries, versioned JSON Schema and OpenAPI documents for public contracts, and a separate SQLite database owned by each local reference service. Pin dependency versions when implementation begins. No service may directly read another service's database.

Use durable job records and explicit polling initially; introduce a broker only when requirements justify it. Start with deterministic text retrieval before adding embeddings or graphs. Model access uses profiles with explicit egress permissions and secret references. Service authentication, grants, encryption and key custody require their own accepted decisions before processing private data.

SQLite is a local reference-store choice, not a shared network database or a commitment for replicated/cloud deployments. Remote implementations choose their own state stores and prove compatibility through the same contracts.

## Alternatives

- TypeScript reference services: a reasonable choice for a team prioritising a shared UI/backend language, but no UI implementation is currently required.
- PostgreSQL and a message broker from the start: useful for some multi-host and concurrency requirements, but add operational dependencies before the minimal contracts are established.
- One bundled process: useful later for installation convenience, but insufficient evidence of independent deployment on its own.

## Consequences

The reference is small enough to inspect while preserving replaceable boundaries. HTTP does not solve authorisation or semantic compatibility; those require explicit contracts and executable tests. Separate processes, authenticated network boundaries and independently implemented alternatives must still be demonstrated. This ADR does not choose a licence or approve any cloud provider.
