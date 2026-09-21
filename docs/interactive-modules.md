# Gradual interactive module interfaces

Status: future backlog, not implemented functionality. UC-005 remains a read-only monitor. These increments extend the [delivery queue](delivery-backlog.md) as use cases justify them; controlled disclosure remains the next queued outcome. Candidate IDs below are planning references, not delivered slice numbers.

## Build one interaction at a time

Start with a visible preview, add one authorised action through the owning module's public contract, show its durable result and test denial/recovery. Keep the existing read-only monitor independently usable. A module may expose its own interface or use a shared dashboard client; neither requires a central dashboard to run the module.

Interactive access needs a separate authenticated user/session and narrowly scoped action permissions. The current monitoring token must never acquire write or signing authority. Backend modules enforce permissions even if the interface is bypassed. Browser session protection, request-forgery protection, secret handling and audit belong in each interactive slice's acceptance profile. Module contracts retain the same meaning on Mac, Windows, Linux and Kubernetes; key custody, secret storage and ingress use the deployment profile. Support for each environment still requires a demonstrated run.

## Candidate vertical increments

| Candidate | Visible outcome | Ownership and dependencies | Acceptance evidence |
| --- | --- | --- | --- |
| INT-01 — Select an AI | Inspect available profiles; select an allowed provider/model, configure its endpoint and secret reference, test the connection and activate a versioned profile | Model access owns configuration and validation; Assistance selects an authorised route. Start with installed local Ollama, then one external API adapter | Persist and restore selection; reject unauthorised changes and unsupported profiles; failed validation preserves the active profile. Never display stored secrets or silently change provider. A connection test sends no source content; any paid inference test explicitly shows destination and possible cost |
| INT-02 — Issue a signed document claim | Add a document through a Connector, register its exact version in Wallet, preview the claim and sign as a named issuer | Wallet owns claim/evidence association and signing authority; Connector owns source bytes; key operations may use an attached wallet adapter | Verify the issuer signature and exact document digest/version; changing bytes fails verification; unauthorised signing is denied; retry does not create unintended duplicate issuance. Separate uploading a document from issuing a claim about it |
| INT-03 — Present as holder | Choose a held credential, inspect the verifier's request and disclosed content, then sign the presentation using the holder's wallet | Wallet owns holder authority and key use; Exchange owns approved outward disclosure and delivery. Depends on issuance and controlled disclosure | Bind presentation to verifier/audience, challenge and expiry; reject replay, changed recipients and excess disclosure. Require source/export authority separately from possession of a credential |
| INT-04 — Verify externally | A separate verifier interface requests a presentation through a link or QR code and shows signature, holder binding, issuer trust, document match and credential status results separately | A separately deployable Wallet-family verification implementation or adapter owns verification policy; Exchange supplies the presentation transport. It need not have access to the holder's private state | Test accepted, tampered, expired, revoked, wrong-audience and replayed presentations. Unknown issuers and unavailable status checks cannot appear as fully trusted. Demonstrate a real second browser/device; localhost-only links are not a cross-device proof |
| INT-05 — Attach a contribution | A third party verifies earlier evidence, signs a scoped confirmation/certification/marking and lets another verifier inspect the chain | Wallet owns linked claims and explicit trust policy; Exchange handles permitted sharing | Preserve exact references to earlier claims; do not infer transitive trust. Reject changed evidence and unacceptable issuers; show precisely what each party asserts |

The issuer and holder may be the same participant in the first synthetic example, but remain distinct roles. A signature supports attribution and integrity; it does not establish legal ownership or the truth of the statement by itself. A holder signature must be bound to the holder relationship accepted by the chosen credential profile.

Choose the credential format, holder-binding rules, key custody/recovery, status/revocation mechanism and presentation protocol when shaping INT-02/03. No credential standard is selected by this backlog. An external wallet complements FarmWallet through an adapter; a separate verifier is an implementation within the existing nine-family architecture, not a tenth family.

A QR code should carry a short-lived request/link, not private keys or the document itself. The interface must show the intended verifier and exact disclosure before release. Cross-device verification requires reachable endpoints and the appropriate transport security; scanning a code alone proves neither identity nor authority.

## Extend across the nine families

These are candidate interactions, not a promise to build a full administration console at once.

| Family | Gradual interactive modes |
| --- | --- |
| Wallet | Inspect documents/versions and source permissions; issue, hold and present signed claims; inspect verifier results and contribution chains |
| Connectors | Add a source, test connectivity, preview an import and inspect source disclosure settings; later review an AI-proposed interface configuration before admission |
| Processing | Preview extraction/mapping results, select a supported recipe and submit a bounded processing job |
| Knowledge | Search authorised evidence and inspect its exact source/version and provenance |
| Workflow | Submit a supported job, inspect steps and retry/cancel only where the job contract permits |
| Model access | Configure and validate allowed AI profiles, choose a route and inspect usage without revealing secrets |
| Assistance | Ask a question, choose an authorised model profile and inspect evidence/citations before accepting an answer |
| Exchange | Preview recipient/content/purpose, approve a permitted disclosure and inspect delivery receipts or uncertainty |
| Registry | Inspect compatible instances and propose/test bindings; changing a binding never grants permission |

For each chosen increment, publish its supported actions, permission boundary and deployment requirements; record expected versus actual module changes. Keep business logic out of the dashboard, update documentation and dashboard progress, and retain a runnable acceptance example before calling the interaction delivered.
