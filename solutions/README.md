# Solution templates

Status: broad solution recipes plus runnable synthetic macOS increments. Production installers and release lock manifests remain future work.

| Recipe | Purpose | Current state |
| --- | --- | --- |
| [Knowledge replacement](replacement/README.md) | Two instances, explicit provider substitution and public-API rebuild | [UC-008 development demo](replacement/uc008/README.md) |
| [Controlled disclosure](disclosure/README.md) | Preview, approve and deliver exact content with receipt recovery | [UC-006 development demo](disclosure/uc006/README.md) |
| [S3 source](s3-source/README.md) | Alternative storage implementation feeding existing extraction and disclosure | [UC-007 local preview](s3-source/uc007/README.md); real-provider evidence pending |
| [Operations](operations/README.md) | Live read-only installation inventory, contents and monitoring | [UC-005 operational dashboard](operations/uc005/README.md) |
| [Core](core/README.md) | Resource authority and composition with a useful source connector | [UC-001 development demo](core/uc001/README.md) |
| [Assisted answer](assisted-answer/README.md) | Permission-checked local model answer with exact citation | [UC-004 development demo](assisted-answer/uc004/README.md) |
| [Sensor path](sensor-path/README.md) | Source-scoped observations and traceable releases | [UC-003 development demo](sensor-path/uc003/README.md) |
| [Document path](document-path/README.md) | Authorised document ingestion, retrieval, answer and controlled export | [UC-002 extraction/retrieval demo](document-path/uc002/README.md); exact-document export demonstrated separately in UC-006 |

A solution composes module implementations through bindings and separately authorised grants. It does not own their private databases or require one release number for all modules. An individual module can be installed without a complete solution when its declared dependencies are satisfied.

A future deployable template must resolve exact module artifacts/digests, compatible contract/security profiles, configuration schemas, data flows, grants, target profiles and any migration. Each instance may use a different environment profile. Generated secrets and deployment state remain outside the repository.

Promote a recipe to deployable only after runnable artifacts and end-to-end installation/security/lifecycle evidence exist for the advertised combination. Follow [release requirements](../docs/releases.md) and the [conformance plan](../conformance/README.md). Do not supply fake installer commands while only designs exist.
