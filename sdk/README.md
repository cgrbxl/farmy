# Optional integration SDKs

Status: [optional Python development transport](python/farmy_transport/http.py) supports UC-001, UC-002 and UC-003 with versioned envelope/payload validation and mutual TLS. [Development state helpers](python/farmy_transport/local.py) provide per-service connections and audit writes; module schemas and policy stay in the modules. It is not a general-purpose stable SDK.

Future SDKs may provide typed clients, descriptor/config validation, common errors, authenticated transport integration, evidence helpers and audit envelopes. They must follow versioned public contracts and should be exercised by the same conformance suite as independent implementations.

SDKs are optional: neither language choice nor a shared runtime library is required for compatibility. Do not put domain algorithms, private persistence models, universal administrative credentials or module-specific policy decisions in a compulsory common package. A library can assist permission enforcement, but each receiving module remains responsible for enforcing its boundary.

Implement only helpers required by the MVP, after contracts exist. Dependency upgrades must not require unrelated modules to be released together. See [contracts](../contracts/README.md) and [conformance](../conformance/README.md).
