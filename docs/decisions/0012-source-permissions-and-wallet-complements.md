# ADR 0012 — Source permissions, consumer accountability and external wallets

Date: 2026-09-19
Status: Accepted direction from maintainer clarification; source permissions are now implemented narrowly in UC-003; external-wallet and broader usage-conditions requirements remain deferred. This records the maintainer's decisions, not adoption of an external proposal.

## Product and module boundaries

Farmy includes usable solutions, reference modules, open contracts and conformance tests. The contracts/tests can be used independently to build a compatible implementation; they are a separable deliverable, not the whole product. Compatibility must be demonstrated by implementation and tests, not assumed from reuse of the documents.

Retain the nine-family architecture. The requirements below extend responsibilities within those families; they do not justify additional mandatory families or a redesign of the current path.

## Source-level permission

For ongoing data, authority is scoped to an identified logical or physical source, its owner and its consumer. Observations do not each require approval. When observations need different access rules, represent them through separately identified sources with enforced membership boundaries. A logical partition is still a real authorisation boundary, not just a display label.

Wallet owns source identity/ownership and permission decisions. Connectors enforce permitted source membership when serving content. Exact observation/batch/version references remain necessary for provenance, repeatable retrieval and audit; these references do not require separate grants per observation. Source scope, permitted operations, expiry and revocation must remain explicit.

This is the next sensor slice's requirement, not a retroactive removal of UC-001/UC-002 exact-version grants. Dynamic recipient groups are not required for that slice; grant to identified consumers.

## Confidentiality and credential assurance

Access policy and the evidence supporting a claim remain distinct within existing Wallet/credential responsibilities. Who can read data does not determine who issued or signed it; a valid credential does not automatically grant data access. This clarification does not add a new implementation milestone or family.

An external wallet may complement Farmy by storing, signing, presenting or verifying selected data/credentials through suitable adapters. It does not automatically replace FarmWallet's resource inventory, policy authority or provenance responsibilities. A full replacement would have to implement Farmy's relevant contracts, or an explicitly designed compatible mapping; supporting a wallet standard alone is not such evidence. There is no current decision to turn FarmWallet into a standard credential wallet or prioritise its replacement.

Wallet owns selection, authority and credential references; provider-specific integration stays behind adapters. Exchange handles externally directed presentation/delivery when needed. No external wallet product or protocol is selected here.

## Usage conditions and consumer accountability

Define permitted use and onward disclosure, and record the terms applicable to a transfer. Farmy enforces the operations it controls; it cannot guarantee downstream behaviour after a consumer obtains usable content. Consumer responsibilities must be made explicit rather than implying complete technical control.

Wallet records policy/term references. Connectors retain incoming source/term provenance. Serving modules record authenticated access and delivered source/batch/version references. Exchange records outward disclosure, recipient and applicable conditions. Logs establish what Farmy observed or delivered, not proof of every subsequent use by the recipient.

Watermarking is an optional future investigation, not a guaranteed control or requirement of the next slice. If implemented, Processing may produce a marked derivative and Exchange associate it with a disclosure; preserve the original and record the transformation. Suitability for each data type and evidential limits require testing.

## Next increment

Build a thin synthetic sensor-source slice before model integration. Demonstrate one source permission covering multiple observations, isolation of a separately identified source, consumer-specific denial, revocation and traceable delivery. Retain UC-001/UC-002 regression checks. No physical sensors, offline authorisation, credential wallet integration or watermarking is included yet.

See [UC-003](../../solutions/sensor-path/use-cases/UC-003-source-scoped-observations.md).
