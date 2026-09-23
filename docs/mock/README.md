# Las Tres Encinas — a possible Farmy phone solution

The supplied **farmy · Las Tres Encinas.html** is preserved unchanged in this folder. It is a self-contained mockup with fictional farm records, messages, sensors and model responses. It illustrates a possible finished experience; it is not a production application or an additional completed implementation slice.

The [annotated public copy](../../dashboard/mock/index.html) adds optional module tags and explanatory popups. It is embedded in the project dashboard's **Phone solution** section. Select **How Farmy works** to hide or show notes, or **All 9 families** for the full map. Each popup separates the proposed behavior from today's demonstrated scope.

## What this clarifies

The farmer has four understandable views: Copilot, Drive, Hub and Control. Those views compose capabilities rather than defining four large backend services. Evidence, access decisions and outward disclosure remain visible within ordinary tasks. This is a useful expression of the intended product without making the farmer manage architecture.

| Visible experience | Main families | Boundary |
| --- | --- | --- |
| Ask what needs attention | Assistance, Knowledge, Processing, Model access | An answer is a derived explanation, not a new authoritative farm record. Model access checks the chosen route and permitted context. |
| Inspect a cited manual, invoice or message | Connectors, Wallet, Knowledge | Source identity and current permission remain distinct from storage and retrieval. |
| Compare meter readings, soil moisture and equipment state | Connectors, Processing, Knowledge | Physical acquisition and specialist analysis need their own verified adapters and semantics. |
| Prepare a task and approve an action | Workflow, Assistance, Wallet | Coordination does not authorise itself; real equipment control needs a separately validated safety/execution contract. |
| Choose sources and recipient rights | Wallet, Connectors | Govern source/owner/consumer access. Sender filters constrain ingestion; they are not portable recipient grants. |
| Preview what leaves and track the outcome | Exchange, Wallet, Workflow | Reading, approving export and proving receipt are separate; downstream obligations cannot technically prevent all reuse. |
| Select compatible implementations behind the UI | Registry | A binding selects an instance; it grants no access and transfers no private database. |
| Inspect a certificate or assurance label | Wallet with future credential/key adapters | Declared issuer/signature labels are not cryptographic verification, trust decisions or proof of ownership. |

A **hub** is a possible deployment location for several module instances, not a tenth family. The phone is a replaceable client. Neither this single-hub example nor its source controls demonstrate federation between independent data-space authorities.

## Important design distinctions

- **AI plasticity:** this example expresses useful AI-assisted analysis and source diversity. It does not yet show an AI generating, testing and admitting a new interface while its module stays running.
- **Pseudonymisation:** replacing direct identifiers may reduce exposure, but combinations of farm facts can still identify someone. The real capability needs a clear policy and its own tests.
- **Assurance and access:** a signed certificate does not automatically grant its holder access. Hash-linked audit entries do not supply independent witnessing or issuer/holder/verifier credential verification.
- **Data use conditions:** Farmy can enforce controlled release at its own boundary and retain traceability. Contractual restrictions after delivery still depend on recipient responsibility and enforcement.
- **Device controls:** the mock's valve and threshold changes affect fictional browser state only. They do not establish real-world safety, reversibility or authorisation semantics.

## Reproduction and publication

Run `python3 scripts/build_phone_mock.py` from the repository root after updating the supplied source. The script preserves the source and regenerates `dashboard/mock/index.html`; the explanation layer lives in its adjacent `architecture.js` and `architecture.css`. The public copy blocks network API calls with a Content Security Policy. There are no external model calls, uploads, real messages, map tiles or device connections. A model selection may be retained in browser local storage; reloading resets the other simulated state.

Serve the dashboard normally and open `mock/index.html`, or use the embedded view. Only the annotated static mock's three files are included in the public preview, not the repository, live monitoring bridge, private feedback or runtime configuration. Public hosting details will be recorded here after successful publication.

The existing UC-001–006 and UC-008 runtime evidence remains unchanged; UC-007 still awaits real Scaleway validation.
