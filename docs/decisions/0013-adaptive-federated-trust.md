# ADR 0013 — Adaptive interfaces, source governance and wallet trust networks

Date: 2026-09-21
Status: accepted conceptual direction from the maintainer; implementation profiles deferred.

## Decision

Make three connected concepts explicit in Farmy's vision and reference architecture:

1. AI supports module plasticity as well as content analysis, embeddings and ontology work. A suitably designed implementation can generate/admit a new source mapping or isolated adapter extension without redeploying the host or the whole solution. Admission, versioning and authority remain explicit.
2. Independent sources govern consumption under their own disclosure policies while participating in common data-space governance. Federation does not merge owners or wallet authority namespaces.
3. Wallets support attributable owner claims and third-party contributions through issuer/holder/verifier relationships and referenced chains or graphs of signed evidence. Trust acceptance and disclosure permission are distinct from signature verification.

Retain the nine module families. Generation, admission, source access, governance, credential operations and disclosure remain separated by responsibility and privilege, even when an implementation packages several capabilities. This extends [ADR 0012](0012-source-permissions-and-wallet-complements.md), including source-level observation permissions and complementary external wallets.

## Consequences and limits

“Without an update” applies where the host already supports the necessary extension runtime and contract. Generated artifacts still have versions, provenance, constrained privileges, tests and rollback. Automatic activation is possible within an explicitly delegated admission policy; generated code cannot grant itself that authority.

Data-space participation is not blanket read permission. Combining sources requires each applicable authority and defined conditions for resulting information. Downstream consumer duties cannot be replaced by a promise of complete technical control.

A signature supports attribution and integrity of a claim; verifier policy and supporting evidence determine what the claim proves. Trust is not automatically transitive, and a signed ownership declaration is not itself conclusive ownership evidence. Neither an attestation nor data-space membership grants content access.

No general self-modifying runtime, external data-space protocol, wallet product, credential standard or cryptographic suite is selected. These concepts are not implemented by the current five local slices. The clarification changes documentation and future acceptance criteria, not the running system or delivery order.

See [the three core concepts](../core-concepts.md) for examples, family ownership and candidate demonstrations.
