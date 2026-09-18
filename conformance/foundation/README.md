# Minimum integration foundation checks

Implemented: JSON Schema document validation and cross-document declared compatibility checks, with positive examples and negative tests. Not implemented: network services, cryptographic authentication, grants, readiness verification, dependency resolution, operation payload validation or deployment tests.

Run from the repository root on an environment supporting the pinned dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r conformance/foundation/requirements.txt
.venv/bin/python conformance/foundation/check.py
.venv/bin/python -m unittest discover -s conformance/foundation -v
python3 scripts/check_docs.py
```

On Windows, a virtual environment normally uses `.venv\Scripts\python.exe` instead of `.venv/bin/python`; this procedure has only been executed on the current macOS arm64/Python 3.14.6 development host. Four platform documents are validated as data, not deployed or run.

Validate a single document:

```sh
.venv/bin/python conformance/foundation/check.py --kind module --file contracts/v0.1-draft/examples/module.json
```

Kinds: module, instance, binding, environment, request and response. The schema also defines resourceRef and capability structures. Unknown top-level fields are rejected; operation payloads are intentionally left to capability-specific schemas. The tool does not retrieve URLs, load plugins, contact endpoints or read credential references.

The compatibility result never grants access. It reports exact declared version/operation/feature matching, target declaration and required dependencies still unresolved. A profile name, peer identity or `tested` flag in untrusted JSON is only a claim until independently verified.

Regression tests cover mismatched releases/bindings/versions/features, unsupported targets, duplicate declarations, insecure/credential-bearing endpoint URLs, missing exact source versions, cross-wallet references, malformed UTC deadlines, grant material in bindings and conflicting success/error results. These are structural/consistency checks, not runtime attacks against actual modules. Field validation cannot prevent arbitrary secrets being placed in free text or payloads; review and runtime redaction are still required.

See the [foundation contract](../../contracts/v0.1-draft/README.md). Public capability operations and corresponding runtime conformance will be introduced with [UC-001](../../solutions/core/use-cases/UC-001-controlled-memory.md).

Local verification on 2026-09-18: 10 fixtures validated, four environment-description combinations checked, 19 regression tests passed and documentation links/JSON checks passed. Only the local macOS arm64/Python 3.14.6 tooling environment was executed; no module or target deployment was tested.
