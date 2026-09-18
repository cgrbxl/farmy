# Contributing to Farmy

Farmy welcomes discussion of the architecture and independently provided modules. The project is at documentation-baseline stage. Original repository materials are licensed under [Apache 2.0](LICENSE).

Start with the [repository contributor path](docs/repository-structure.md), your [module family guide](modules/README.md), and the [common integration/security profile](contracts/profiles/README.md). Current solution recipes and deployment profiles are design-only; do not describe them as runnable.

1. Frame a small use-case card or issue describing the outcome and affected capabilities; use the draft [working method](docs/working-method.md). An architecture proposal is needed when changing lasting boundaries, not for every routine increment.
2. Distinguish new contract requirements from implementation-specific choices.
3. Describe data access, trust boundary, failure behaviour, portability and compatibility.
4. Keep changes focused and update the relevant ADR when changing architecture.
5. Use synthetic fixtures only; never submit real farm records, secrets or personal data.

Future module submissions should include descriptor, supported contract versions, deployment modes, configuration and secret references, permissions/egress requirements, lifecycle instructions, migration procedure and conformance evidence. Module implementations may live in separate repositories and use different languages. Declare target support and release evidence using the [release requirements](docs/releases.md); cloud offerings must identify their compatible [provider landing zones](docs/cloud-landing-zones.md).

Farmy is an altruistic project. Please consider sharing fixes, interoperability improvements and documentation with the community. Sharing back is encouraged, not a condition of use.

Contributions intentionally submitted for inclusion follow section 5 of Apache 2.0. You retain copyright and must have the rights to submit your contribution. Identify third-party material and its licence; do not assume Farmy can relicense it. The current policy requires neither copyright assignment nor a separate CLA. See [LICENSING.md](LICENSING.md).

The [foundation validator](conformance/foundation/README.md) checks draft document structure and declared compatibility; passing it does not prove runtime security or grant access.

For documentation checks run `python3 scripts/check_docs.py`. This checks links and JSON parsing only, not security or API conformance.

Public issues are for design and ordinary defects. See SECURITY.md before reporting sensitive findings.
