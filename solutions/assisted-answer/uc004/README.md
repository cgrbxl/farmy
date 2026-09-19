# UC-004: a cited answer through a selected local model

Status: experimental synthetic macOS slice. Seven separate Farmy services compose the unchanged document/evidence path with Model access and Assistance. It answers **“Which crop is recorded?”** and validates the model's crop and citation against exact-version evidence. This is a bounded integration test, not a general agricultural adviser. A deterministic renderer produces the final sentence only after validating the real model's structured selection.

## Run

Use the existing Python environment, foundation requirements and OpenSSL prerequisites from [UC-001](../../core/uc001/README.md). Install/run Ollama separately and explicitly make the selected model available. The runner neither installs software nor downloads models and never falls back to another provider.

The tested choice is local `qwen2.5:3b` (GGUF Q4_K_M), digest `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`, through `http://127.0.0.1:11434`. Bootstrap records the installed model digest and immutable route profile. Selecting a different installed model creates a new composition and requires its own verification.

From the repository root:

```sh
.venv/bin/python solutions/assisted-answer/uc004/run.py demo
.venv/bin/python scripts/verify.py --with-local-model
```

The demo owns temporary state, starts/stops its seven Farmy processes, and retains your existing Ollama server. It prints the answer, exact citation and model/profile digests; then checks restart/replay, rejected readers/routes, revoked model permission and unavailable authority. Model memory is requested for one minute. Only synthetic crop evidence is sent to the selected loopback runtime.

For repeatable fault injection without an installed model:

```sh
.venv/bin/python -m unittest discover -s conformance/uc004 -v
```

Those ten tests use a controlled Ollama-shaped HTTP double and real Farmy services. They establish security/recovery behaviour, not provider compatibility. The real-model demo establishes the latter separately. `scripts/verify.py` without the flag runs all 55 tests and the original three demos without requiring Ollama.

## Compose independently

Bootstrap into a new empty directory:

```sh
.venv/bin/python solutions/assisted-answer/uc004/run.py bootstrap --directory .farmy/uc004
```

Start each service in its own terminal using the same configuration directory:

```sh
.venv/bin/python solutions/assisted-answer/uc004/run.py serve --directory .farmy/uc004 --service wallet.local
```

Repeat with `connector.local`, `processing.local`, `knowledge.local`, `workflow.local`, `model.local` and `assistance.local`. Then run:

```sh
.venv/bin/python solutions/assisted-answer/uc004/run.py example --directory .farmy/uc004
```

Stop each owned terminal with Ctrl-C. Development certificates expire after two days; use a new directory for a new bootstrap. Grants expire after ten minutes. Old directories are never overwritten. Module configuration is trusted operator input, not remotely editable policy. A route/model change requires a new bootstrap and new grants, not editing a live composition in place.

## Data and authority flow

```mermaid
sequenceDiagram
    participant R as Reader
    participant A as Assistance
    participant K as Knowledge
    participant M as Model access
    participant W as Wallet
    participant O as Selected local Ollama
    R->>A: Exact source, question, route and grant references
    A->>W: Check reader answer permission
    A->>K: Retrieve permitted evidence as Assistance
    K->>W: Check Assistance evidence permission
    A->>M: Invoke selected route with separate invocation grant
    M->>W: Check Assistance invocation permission
    M->>K: Independently retrieve evidence as Model access
    K->>W: Check Model access evidence permission
    M->>O: Check installed digest; release bounded evidence prompt
    O-->>M: Crop and citation ID (untrusted)
    M->>M: Validate exact value/citation; recheck permissions
    M-->>A: Validated selection, evidence and route provenance
    A->>A: Compare evidence independently; recheck access
    A-->>R: Rendered sentence with exact-source citation
```

Four independent permissions gate answer disclosure, Assistance evidence retrieval, model invocation and Model access evidence retrieval. All references bind the exact document version. Grants are references, not transferable credentials. Model access fetches evidence itself; callers cannot supply arbitrary prompts, endpoints, tools or source content.

## Persistence and recovery

Model access owns its invocation journal. Assistance owns accepted answers. Each has a private SQLite database and minimal audit. Replaying an accepted key rechecks live permissions without invoking the model again. Changed inputs conflict. Calls reserved before a crash or unsuccessful provider response remain uncertain; replay returns `conflict` without automatic regeneration. An operator can deliberately choose a new key for a new attempt; there is no exactly-once inference claim or background reconciliation worker.

No prior module database migrations are needed. The optional transport helper adds the new operation catalogue and bounded per-endpoint timeouts for model latency; unchanged endpoints retain their three-second limit. UC-004 allows a 55-second envelope deadline and up to 40 seconds for generation. Other operation versions remain unchanged.

## Limits and evidence

Validated on macOS 26.6.2 (arm64), Python 3.14.6, with ten new runtime tests, all 45 earlier tests and all four demos. The implementation is contained in the commit adding UC-004; [use-case evidence](../use-cases/UC-004-cited-model-answer.md) records the scope and impact.

Farmy service boundaries use mutual TLS 1.3. The Ollama adapter boundary uses plain HTTP restricted to numeric loopback; it is an explicitly trusted same-host development dependency, not an authenticated remote model channel. The model process is not sandboxed by Farmy, and application route checks are not an OS firewall. Remote/cloud models, provider secrets, streaming, cancellation, prompt injection resistance for general documents and unrestricted questions remain unsupported.

Only the extracted crop quote and citation ID enter the prompt. Unexpected fields, fabricated references, mismatched values and malformed model replies are rejected. This proves grounding for one exact fact, not general factual correctness. Already authorised in-flight prompts cannot be recalled by later revocation. Raw prompts are not added to Farmy's generic logs; owned answer/evidence stores contain synthetic content and are not encrypted at rest. The host user can access all development credentials and state.

Adapter reference: [Ollama generate API](https://github.com/ollama/ollama/blob/main/docs/api.md). Public Farmy interface: [UC-004 contracts](../../../contracts/uc004/README.md).
