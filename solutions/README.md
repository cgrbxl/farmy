# Solution templates

Status: design recipes only. No runnable solution, release lock manifest or installation command exists yet.

| Recipe | Purpose | Current state |
| --- | --- | --- |
| [Core](core/README.md) | Resource authority and composition with a useful source connector | Design-only |
| [Document path](document-path/README.md) | Authorised document ingestion, retrieval, answer and controlled export | Design-only |

A solution composes module implementations through bindings and separately authorised grants. It does not own their private databases or require one release number for all modules. An individual module can be installed without a complete solution when its declared dependencies are satisfied.

A future deployable template must resolve exact module artifacts/digests, compatible contract/security profiles, configuration schemas, data flows, grants, target profiles and any migration. Each instance may use a different environment profile. Generated secrets and deployment state remain outside the repository.

Promote a recipe to deployable only after runnable artifacts and end-to-end installation/security/lifecycle evidence exist for the advertised combination. Follow [release requirements](../docs/releases.md) and the [conformance plan](../conformance/README.md). Do not supply fake installer commands while only designs exist.
