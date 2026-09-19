# ADR 0011 — Exact-source derived evidence and resumable jobs

Date: 2026-09-19
Status: Implemented for UC-002 experimental synthetic development.

## Decision

Add separate Processing, Workflow and Knowledge processes. Processing extracts one known text field, Workflow persists a fixed extract/index sequence, and Knowledge retains permission-checked exact-source evidence. Each owns private SQLite state. They exchange typed contracts over the existing loopback mTLS transport.

Extend Wallet with generic, owner-issued permissions scoped to source version, subject, receiving service, operation, purpose, expiry and composition revision. Keep source reading, proposal transfer, indexing and query disclosure as independent permissions. Neither parser rules nor index schemas enter Wallet. Existing UC-001 read grants stay compatible. The Connector source remains unchanged.

Accept proposals into the derived Knowledge index only, under explicit indexing authority. This is a smaller use case than authoritative Wallet proposal acceptance from the future document-path design. Do not describe a parsed claim as an approved farm fact. Provenance identifies a source/producer; semantic correctness and source authenticity remain distinct.

Persist job phases around HTTPS calls, never hold a database transaction across a network request. Stable step keys and deterministic proposal identities support retry after uncertain responses; unique source-version index entries prevent duplicate acceptance. Execution can repeat. Owner-driven retries are sufficient for this short synchronous case; background scheduling/cancellation are deferred.

## Consequences

Five processes now demonstrate the module boundaries, rather than completing three whole families. The parser can change without changes to Wallet/Connector or Workflow orchestration, but changing its public result contract can legitimately affect Knowledge. The current index accepts one fixed extractor per source version; multiple extractors/fields and replacement/rebuild need later versioned contracts.

Source-read revocation does not erase or revoke independently authorised derived copies. Query/transfer grants must be revoked explicitly. Knowledge checks online before disclosure, so revocation suppresses queries without requiring immediate physical index deletion. No cascading revocation or deletion/erasure claim is made.

Wallet 0.2.0 adds a permissions table without rewriting existing records or grants. New services start at 0.1.0; new operation contracts use 0.2-draft and old contracts retain 0.1-draft. No reverse migration is supplied. UC-002 uses fresh development bootstrap state, two-day certificates and pinned local identities/endpoints; this is not a production credential lifecycle or dynamic service catalogue.

All [UC-001 host/key limits](../../solutions/core/uc001/README.md) still apply. This is synthetic macOS validation only, with no model/cloud costs. See [UC-002](../../solutions/document-path/use-cases/UC-002-exact-source-evidence.md).
