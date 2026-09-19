# UC-004 — Selected-model invocation and cited answer

Experimental `0.4-draft` operations over the unchanged foundation envelope and mutual TLS service profile. [OpenAPI](openapi.json), [schemas](operations.schema.json) and [catalogue](operations.json) describe the interface. Earlier operation versions remain unchanged. The schema embeds UC-002 evidence definitions unchanged so citation fields retain identical semantics.

| Operation | Capability / purpose | Input and result |
| --- | --- | --- |
| `model.invoke` | `farmy.models` / `uc004.invoke` | A selected `routeId` and Model access evidence grant; returns validated crop/citation selection, exact evidence and route provenance |
| `answer.create` | `farmy.assistance` / `uc004.answer` | The fixed question, selected route and three downstream grant references; returns rendered answer, exact citation and route provenance |

Both operations require exactly one source-version reference and an idempotency key. The authenticated actor must equal the subject. `answer.create` requires a current reader-to-Assistance permission; `model.invoke` requires a separate Assistance-to-Model-access permission. Both services retrieve evidence under their own separately issued Knowledge grants, and compare source identities. Wallet's existing generic permission contract handles all four grants without new authority semantics.

`payloadSchema` uses `urn:farmy:uc004:<operation>.input`; results use `.output`. Unknown fields and versions fail. Arbitrary questions, prompts, model URLs, provider parameters and tools are unsupported. The selected route is trusted bootstrap configuration containing the endpoint, model name and pinned local model digest; its digest is checked before invocation or replay. Changing routes needs a new composition/grants. This is one fixed local route, not a general multi-provider permission system.

## Acceptance, denial and recovery

Model access checks the installed model digest before releasing a prompt, then validates the returned crop and citation against evidence. Assistance independently compares the returned evidence and selection, rechecks its permissions and renders the one supported answer. Model-produced authority, tool requests and unvalidated prose are never executed or returned as accepted answers.

Accepted idempotent retries return retained results only after live permission checks. Changed payloads/refs/grants/profile or uncertain invocations return `conflict`. An invocation reservation is committed before the runtime call; a crash or failed call cannot trigger automatic regeneration. A new key is an explicit new attempt, not a transparent retry guarantee. A lost reply after the successful journal commit can be recovered with the original key. Cross-service answer and invocation acceptance are not a distributed transaction.

Errors use the common codes: `denied`, `unauthenticated`, `invalid_request` (including rejected provider content), `conflict`, `expired`, `unavailable` and `unsupported`. Unavailable authority fails closed. Revocation cannot retract a prompt already authorised in flight. Minimal audit records label prompt release as `release_authorized`, not proof of model processing or receipt.

The profile permits only a numeric-loopback HTTP Ollama endpoint with no URL credentials, query, redirects or proxy use. It checks a locally installed GGUF model digest and never downloads or substitutes a model. That loopback runtime is a trusted external process; production runtime isolation, TLS/authentication and network egress controls remain future work.

See [run instructions and limits](../../solutions/assisted-answer/uc004/README.md) and [ten runtime checks](../../conformance/uc004/test_runtime.py). The fault-injection provider is only a test double; real Qwen/Ollama compatibility is demonstrated separately.
