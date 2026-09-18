# Implementation kickoff

Date: 2026-09-18. Status: plan, not implemented behaviour.

## Workspace audit

The actual project root is `/Users/Shared/projects/farmy`; there is no nested `farmy` directory. The extracted baseline contained 16 project files, rather than the reported 20, plus macOS metadata. No `.git` directory or original commit was present. All local Markdown links resolve and both illustrative JSON files parse. Without an archive manifest, the identities of any missing files cannot be established. New local history must not be described as recovered history.

## Agreed foundation

FarmWallet owns a coherent resource and policy namespace independently of storage. Capabilities, implementations, offerings, instances, bindings and grants are separate concepts. Services communicate through public contracts, own their internal state, and may run independently. Bindings confer no permission. Originals and exact versions remain authoritative; derived knowledge retains provenance. Permission checks precede disclosure to workers, models and recipients. The dashboard is not a background execution dependency.

## Immediate work: one running vertical slice

Use the draft [working method](working-method.md) and ordered [delivery queue](delivery-backlog.md). The first concrete card is [UC-001](../solutions/core/use-cases/UC-001-controlled-memory.md): controlled local document memory using Wallet, Local Folder Connector, minimal binding and a thin client.

Define only the resource/version, local identity/authorisation, binding and read contracts required by that case. Implement their real boundaries, persistence and success/denial/restart tests in the same increment. No full catalogue, copilot, workflow engine or cloud setup is needed first.

The architecture-first order still applies within the slice: clarify ownership and security before implementing that boundary. It does not require finishing the entire platform design before any running outcome.

## M1 and M2 progress together

Contract specifications, synthetic fixtures and conformance checks grow with each useful case. Keep unimplemented operations clearly marked and current examples illustrative until migrated. Accept a contract through meaningful runtime tests, not schema parsing alone.

The first milestone is a reproducible local outcome with explicit limits, then a working extraction/retrieval path. Continue the broader document solution below incrementally, preserving earlier cases as regression checks.

## Next: M2 document path

Use synthetic text first, then PDF extraction. Demonstrate local-folder and versioned S3 input, authorised ingestion, searchable evidence, an explicitly selected local or remote model, source-linked answers and separately authorised export. Source relocation must preserve resource identity; content updates must yield a new identifiable version. Do not implement a broad dashboard before this path works.

Require end-to-end tests for denied retrieval, blocked unapproved model routing, export denial, repeat-job reconciliation and provenance back to exact source versions. S3-compatible local testing does not by itself establish compatibility with hosted S3. Real cloud/model integration requires selected endpoints and credentials supplied outside the repository.

M3 then demonstrates a Mac wallet with cloud ingestion, live and staged modes, two knowledge instances, independent implementation substitution and continued background operation without the dashboard. Windows, Linux laptop and each cloud Kubernetes profile remain unverified until separately tested. Versioned releases and provider landing zones follow [ADR 0004](decisions/0004-deployment-and-releases.md).

## Decisions still needed

- Licensing is resolved: Apache 2.0 for original documentation, contracts and code; see [ADR 0003](decisions/0003-apache-2.0.md).
- Reference stack is resolved: Python services, HTTP/JSON contracts and service-owned SQLite; see accepted ADR 0002.
- Identity and keys: issuer trust, human/service authentication, grant format, key storage, recovery and rotation.
- Offline policy: grant lifetimes, maximum revocation staleness and staged-copy retention per trust boundary.
- Prototype providers: S3 environment, local model and any explicitly authorised remote model.

A public documentation repository is useful now. A production agricultural intelligence platform is a much larger undertaking; production security, agronomic validity and interoperability must each be demonstrated independently.
