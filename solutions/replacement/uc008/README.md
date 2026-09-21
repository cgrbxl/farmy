# UC-008 — Replace a Knowledge implementation

Status: experimental synthetic macOS slice. Two Knowledge instances coexist; one is replaced by a separately written domain implementation and rebuilt through public APIs. Both use the optional Python HTTP/mTLS and persistence helpers. This proves bounded implementation substitution, not an independent transport, language or vendor certification.

## Run

Use the Python environment from [UC-001](../../core/uc001/README.md). No model or cloud credentials are needed.

```sh
.venv/bin/python solutions/replacement/uc008/run.py demo
.venv/bin/python solutions/replacement/uc008/run.py launch
.venv/bin/python -m unittest discover -s conformance/uc008 -v
```

`launch` runs the replacement scenario, then prints a private local dashboard link. It shows six running module instances, including Evidence Knowledge A and Ledger Knowledge B, their real counts and declared dependencies. The Workflow points to B. Registry remains a binding-file adapter. The monitor is read-only; closing its browser does not stop modules. Ctrl-C stops this runner's processes and deletes temporary data. The default UI port falls back to a free port if occupied; `--port 0` explicitly chooses a free port.

## Outcome and acceptance

The owner registers one synthetic crop report. Distinct grants permit source reading, Processing-to-Knowledge transfer, indexing and querying for each target. The consumer resolves a revisioned binding and checks the selected peer's descriptor over pinned mTLS. A binding never supplies an access grant.

1. Index the exact report into A and B and compare their evidence.
2. Keep A running while replacing B with the journal provider, preserving B's previous store untouched. B initially returns `not_found`.
3. Advance the binding revision, start a new rebuild job and fetch accepted evidence from Processing through `extraction.get`. The solution never reads either Knowledge database.
4. Verify identical source reference, proposal, quote and digest; restart B and retrieve again.
5. Reject A's query grant at B, reject old job keys after a binding change, deny revoked/expired readers and fail closed without Wallet.
6. Monitor both instances independently through authenticated summaries.

Eleven acceptance tests cover both domain providers, concurrent duplicate indexing, changed idempotency inputs, exact-version permissions, unavailable-instance isolation, separate transfer authority, mismatched declarations, interrupted jobs and the complete replacement/rebuild scenario.

## Module impact and versions

| Component | Expected and actual change |
| --- | --- |
| Knowledge | Add `knowledge/ledger`, implementation `farmy.reference.knowledge-ledger` 0.1.0, with an append-only journal schema. Existing Evidence provider remains unchanged. |
| Workflow | Optional `knowledgeBinding`; capture the full binding in durable job input and validate the selected descriptor before indexing. UC-008 advertises 0.2.0; legacy configurations retain existing behavior and digest format. |
| Registry adapter | Resolve an explicit contract version; authenticate and check selected instance declarations. No new service, discovery or access rights. |
| Composition/client | Two instances, per-instance grants, explicit stop/reconfigure/start and fresh rebuild job. |
| Wallet, Connector, Processing, transport SDK, live monitor | Implementation code unchanged; configuration supplies the second identity, scoped permissions and inventory. |

Public operations remain [UC-002 0.2-draft](../../../contracts/uc002/README.md); bindings use the existing foundation schema. [UC-008 contract profile](../../../contracts/uc008/README.md) records selection and replacement semantics. Every service owns its state directory.

## Replacement limits

This is an operator-controlled local replacement with downtime for B, not a hot swap or automatic migration. A successful historical job remains historical: replacing a store does not replay it. Advance the binding revision and use a new job key to rebuild. An incomplete job can resume only with its original complete binding and inputs. The binding is loaded at Workflow startup; edit it only while Workflow is stopped. No live reconfiguration API is provided.

The controlled replacement retains B's enrolled service identity and key; its current grants remain valid. The new implementation must therefore be trusted to receive B's rights. Replacing an untrusted operator requires a new identity, enrollment, fresh scoped grants and revocation of the old identity/rights; that lifecycle is not demonstrated here. Old stores are retained for this short experiment, never automatically copied/deleted or reopened by the replacement. Production backup, retention, rollback reconciliation, credential rotation and deletion remain future work.

Only fixed exact-source crop evidence is compared. Full-text/vector search equivalence, arbitrary extractors, cross-wallet federation, remote providers, Windows/Linux/Kubernetes and independently implemented transport are unverified. UC-007's live Scaleway evidence remains pending and is not promoted by this slice.

## Evidence

2026-09-21, macOS 26.6.2 arm64 / Python 3.14.6: eleven UC-008 acceptance tests passed. Full regression passed 102 tests and eight demos, including installed local Qwen/Ollama and the optional S3 HTTP double. The final inventory-label adjustment was followed by another passing UC-008 suite. Browser checks confirmed the replacement walkthrough, diagram, six live nodes and B’s one evidence entry / one accepted index request. The completed baseline is 91 tests across seven slices; the other eleven checks belong to pending UC-007.

Use the repository verification command:

```sh
.venv/bin/python scripts/verify.py --with-local-model --with-s3-fixture
```

The optional S3 flag exercises an HTTP double only. The optional model flag requires the installed local Qwen/Ollama setup. Neither is needed to run UC-008.
