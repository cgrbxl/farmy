# ADR 0003 — Apache 2.0 licensing

Date: 2026-09-18
Status: Accepted by the maintainer; applied to the repository.

## Context

Farmy is an altruistic project intended to support broad reuse and independent providers. Sharing improvements upstream is highly desired, but private modifications and commercial hosting without payment to the maintainer are acceptable. The maintainer explicitly approved applying Apache 2.0 to original code, contracts and documentation and recording the decision on GitHub.

## Decision

Apply the unmodified Apache License, Version 2.0 to original repository materials, including code, documentation, specifications, schemas, configuration and synthetic examples, unless explicitly identified otherwise. The complete text is in [LICENSE](../../LICENSE); scope and exclusions are in [LICENSING.md](../../LICENSING.md).

Encourage upstream contributions without making them a condition of use. Accept contributions under section 5 of the licence, with contributors retaining ownership. Do not require copyright assignment or a separate CLA under the current policy.

Farmer data and third-party materials are outside this grant. Independent providers may use other licences. Licensing does not establish technical compatibility, authorise data access or certify an implementation.

## Alternatives considered

- MIT: similarly permissive, but without the express contributor patent grant present in Apache 2.0.
- MPL 2.0: file-level reciprocity on distribution, which is more restrictive than the maintainer’s stated requirements.
- AGPLv3: reciprocity including modified programs used over a network, also beyond the stated requirements.
- Separate documentation licence: possible, but unnecessary complexity for the current repository.

## Consequences

Commercial reuse, competing hosting and private modifications are permitted subject to Apache 2.0. Sharing back is voluntary. The licence includes notice obligations, a scoped patent grant and warranty/liability provisions; it does not grant general trademark rights. Already-granted rights cannot simply be withdrawn from compliant recipients by changing future releases. Third-party dependencies and contributions must still be reviewed for compatible terms.

This decision changes reuse terms, not implementation maturity: Farmy remains a documentation baseline with illustrative contracts.

## References

- [Official Apache 2.0 text](https://www.apache.org/licenses/LICENSE-2.0.html)
- [Licensing discussion](https://github.com/cgrbxl/farmy/issues/1)
