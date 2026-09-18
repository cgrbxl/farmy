# Implementation kickoff

Date: 2026-09-18. Status: plan, not implemented behaviour.

## Workspace audit

The actual project root is `/Users/Shared/projects/farmy`; there is no nested `farmy` directory. The extracted baseline contained 16 project files, rather than the reported 20, plus macOS metadata. No `.git` directory or original commit was present. All local Markdown links resolve and both illustrative JSON files parse. Without an archive manifest, the identities of any missing files cannot be established. New local history must not be described as recovered history.

## Agreed foundation

FarmWallet owns a coherent resource and policy namespace independently of storage. Capabilities, implementations, offerings, instances, bindings and grants are separate concepts. Services communicate through public contracts, own their internal state, and may run independently. Bindings confer no permission. Originals and exact versions remain authoritative; derived knowledge retains provenance. Permission checks precede disclosure to workers, models and recipients. The dashboard is not a background execution dependency.

## First milestone: M1 contract foundation

Deliver a small, executable contract validation and conformance harness using synthetic plain-text documents. This milestone does not claim a working wallet, secure deployment or model integration.

1. Record decisions for resource identity/versioning, transport, authentication, delegation, key custody and bounded offline authorisation. Use the accepted reference stack in ADR 0002.
2. Define versioned schemas for resources, immutable source versions, provenance, implementation descriptors, instances, bindings, grants, jobs and evidence. Keep existing examples illustrative until explicitly migrated.
3. Specify the minimal document path: resolve/read an authorised version, submit and inspect an ingestion job, propose/accept derived output, index/retrieve evidence, invoke an approved model and prepare/authorise export. Define errors and idempotency per mutation.
4. Supply positive and negative fixtures plus a runnable harness. Exercise wrong-wallet/audience/purpose/action, expired/revoked authority, stale versions, duplicate requests, unsupported operations and content attempting to expand permissions. Clearly distinguish schema checks from runtime enforcement tests.
5. Define the independent-provider substitution scenario before implementing either provider: readiness, rebuild from authorised originals, binding cutover, old-grant revocation, rollback and evidence equivalence. Two instances of one implementation do not prove substitution.

M1 is complete when the decisions are accepted, schemas and operation specifications agree, and the harness reproducibly accepts valid fixtures and rejects invalid ones. Runtime security claims require subsequent tests against running implementations.

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
