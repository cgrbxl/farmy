# UC-001 — Controlled local document memory

Status: implemented and verified as a synthetic macOS development slice on 2026-09-19. [Run instructions, evidence and limits](../uc001/README.md). No production installer or other platform support is provided.

## Outcome

As a wallet owner, register a synthetic local document, retrieve its exact registered version under an explicit permission, and retain its identity/history across a source move or content update. An unauthorised caller cannot retrieve it.

This proves the smallest useful connection between logical authority and physical storage before adding extraction, search, models or cloud infrastructure.

## Scope and fixture

Use one local wallet, one Local Folder Connector and a thin CLI on the current macOS development machine. Wallet and Connector must run as independently startable components, using declared interfaces and their own state; no direct reads of each other's private database. Use the smallest registry/binding implementation that supports explicit trusted endpoint configuration and a pinned binding revision. A catalogue UI and deployment controller are unnecessary.

Create a synthetic UTF-8 document during test setup with the exact content `Farmy synthetic record v1` followed by a newline. A second version contains `Farmy synthetic record v2` followed by a newline. Use a temporary approved source directory and isolated state; never inspect unrelated user folders.

Exclude parsing/PDF, search, model calls, export, S3, streaming, offline delegation, multi-user production identity and other OS/cloud packaging. The demonstration is local and synthetic, not approval for private farm data.

## Ownership and flow

1. Establish distinct authenticated owner and denied test caller identities plus the connector's own identity. Configure trust/binding explicitly; configuration alone grants no resource access.
2. The authorised owner requests registration of a permitted local source through Wallet/Connector contracts. Connector captures or verifies an exact snapshot; Wallet records stable resource ID, version/digest, location and provenance.
3. An authorised read resolves the registered version and checks authority at the serving boundary before returning exact bytes. Denied callers receive no content or protected metadata.
4. Moving the source and updating its location under authority preserves resource identity. A content update registers a new immutable version and does not relabel new bytes as the old version.
5. Restart the components and demonstrate persistence and continued enforcement. Record access/change events without copying content or credentials into ordinary logs.

## Decisions resolved within this slice

- Minimal local service/caller authentication and trust bootstrap; do not use an unverified caller-name header as authentication. Record the chosen development security profile and its limits.
- Resource/version and grant/read semantics, expected revisions, structured denial/conflict errors and narrow public schemas.
- Snapshot versus live-file version preservation. If old bytes are not retained, old-version reads must explicitly report unavailable; never return newer content as the registered old version.
- Service-owned persistence, secret/key handling, permitted-root enforcement and bounded local transfer.

Use accepted Python/HTTP/JSON reference choices. Select only the libraries needed here and pin versions. Significant lasting security decisions receive a short ADR; routine implementation details do not need a new architecture review.

## Acceptance cases

| Case | Expected result |
| --- | --- |
| Register and read | Stable resource reference and exact fixture bytes/digest under valid permission |
| Unknown or denied caller | No protected bytes or metadata disclosed, even when calling the service directly |
| Source moved | Authorised location update retains resource ID and version; stale updates rejected |
| Content changed | A new version is identifiable; an old-version read returns old bytes or explicit unavailability, never silently new bytes |
| Source changes during read | An exact snapshot is delivered or the read fails explicitly; mixed-version bytes are not accepted |
| Source escapes approved root | Path traversal and symlink escape are denied |
| Permission revoked | The next read is denied at the serving boundary |
| Component restart | Resource/grant state persists and enforcement remains active |
| Dependency unavailable | Explicit bounded failure; no unauthorised bypass or misleading success |

These cases are exercised by the [eight runtime acceptance tests](../../../conformance/uc001/test_runtime.py), including real TLS requests and process restarts. The concurrent-capture case uses deterministic mutation injection. See the [operation contract](../../../contracts/uc001/README.md) for API semantics.

## Delivery evidence

Verified on macOS arm64, Python 3.14.6, OpenSSL 3.6.3: five demo stages passed, eight runtime tests passed, and the foundation regression suite remains passing. Evidence belongs to the commit introducing this runtime and its tests; use `git log -1 -- conformance/uc001/test_runtime.py` to identify that revision. [Reproduction, independent startup, shutdown, cleanup and limitations](../uc001/README.md). [ADR 0010](../../../docs/decisions/0010-uc001-local-runtime.md) records the security and snapshot decisions.

Expected and actual family impact: Wallet, Local Folder Connector and minimal Registry/binding, with a client and common identity/audit support. Workflow, Processing, Knowledge, Model access, Assistance and Exchange should not need implementation merely to complete this case.

After completion, the proposed next slice is extraction/retrieval with exact evidence and durable duplicate handling. Follow the [working method](../../../docs/working-method.md).
