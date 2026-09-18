# ADR 0001 — Composable service ecosystem

Date: 2026-09-18
Status: Accepted conceptual baseline from project discussion; implementation decisions remain proposed.

## Decision

Farmy separates wallet authority from storage and treats each capability as independently deployable wherever dependencies permit. Contributor implementations and running instances are separate objects. Multiple instances are supported through scoped bindings and grants. Shared public contracts, not shared internal databases, establish compatibility.

One coherent authority owns each wallet namespace. Replication does not create competing authorities. Several wallets remain independently administered.

## Consequences

Hybrid installations are first-class. Offline semantics, distributed jobs, provider trust, migration and version compatibility require explicit contracts. A bundled installation remains possible; it cannot be the only supported composition. The dashboard is replaceable and not required for background work.

## Unresolved decisions

| Topic | Required decision |
| --- | --- |
| Licence | Maintainer selection of reuse/contribution terms |
| Runtime stack | Reference implementation languages and state stores |
| Protocol | API transport, events and schema tooling |
| Identity | Authentication and delegation interoperability |
| Key custody | Per-profile key holders, recovery and rotation |
| Offline authority | Grant lifetime and revocation freshness |
| Deployment | Packaging and controller privilege model |
| Data spaces | First target ecosystem and its required contracts |
| Governance | Maintainer additions, voting and release ownership |

Record follow-up decisions as numbered ADRs with context, alternatives, consequences and status. Do not silently turn an example into a normative contract.
