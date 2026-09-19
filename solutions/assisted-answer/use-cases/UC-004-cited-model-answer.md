# UC-004 — Cited local-model answer

Status: done for the synthetic macOS 26.6.2 arm64 development target, Python 3.14.6. Implementation/evidence revision: [`b24d0cb`](https://github.com/cgrbxl/farmy/commit/b24d0cb). See the [runnable solution](../uc004/README.md).

Actor: an enrolled reader asks which crop an exact report version records. The synthetic report contains `crop: wheat`. The observable result is a model-selected crop rendered as a sentence with the original version, SHA-256 digest, quote, byte range and proposal ID, plus selected-model provenance.

Expected module impact: new Model access/Ollama and Assistance/cited-crop implementations; UC-004 contracts and composition; additional grants through existing Wallet semantics; no edits to Wallet, Connectors, Processing, Knowledge or Workflow implementations.

Actual impact matches that prediction. The optional HTTP helper registers the new contract and supports a bounded configured timeout for model latency. Existing modules and operation versions remain unchanged; there are no migrations of their data. New services each own their SQLite state.

Acceptance evidence:

- A real installed `qwen2.5:3b` model returns a value and citation which independently match permitted Knowledge evidence.
- Unknown/mis-scoped readers, altered envelopes, arbitrary prompt/endpoint fields and unapproved routes are rejected before model generation.
- Each of the four independent grants can be revoked; cached answers do not bypass the resulting denial. Expired access and unavailable Wallet/Knowledge/Model access fail closed.
- Malformed model output, fabricated citations, false values and tool proposals do not become answers.
- Exact replay after restart returns the retained answer without another inference. Changed inputs conflict. Uncertain model calls are not automatically repeated.
- Test fixture instructions outside the selected crop field never reach the model. This is a narrow minimisation property, not a claim about general prompt injection protection.
- Ten UC-004 acceptance tests, all 45 previous tests and all four demos pass using the commands in the solution README.

Explicit integration choice: installed local Ollama and Qwen, without model downloads, paid provider access or off-host prompt transfer. The model is intentionally redundant for this simple crop fact: the value of this slice is testing interoperable authority, route selection, citations and failure behaviour before richer assistance.

Next learning: controlled export needs its own exact-content/recipient approval, independent of reading or model invocation. Broader questions should only follow explicit evidence and validation semantics; do not silently widen this contract.
