# S3 source connector — Scaleway candidate

Status: implementation and 11 local HTTP-double checks pass; **not yet validated against Scaleway**. This is the in-progress [UC-007 slice](../../../solutions/s3-source/uc007/README.md), not a seventh completed slice or a production provider integration.

Implements the existing `farmy.storage/0.1-draft` capture/read operations under the fixed `connector.local` role. Wallet, Processing, Knowledge, Workflow and Exchange retain their existing source code and contracts. Choose this implementation in a fresh composition; simultaneous Local Folder/S3 instances in one Wallet and migration of an existing connector store remain future work.

## Configuration and boundaries

Install [pinned optional dependencies](requirements.txt). `s3` in the connector configuration contains the fields from [scaleway.example.json](scaleway.example.json); it never contains secret values.

- One explicit bucket and nonempty dedicated prefix; API paths are relative object keys within that prefix. Absolute paths, traversal segments, backslashes, query syntax and percent escapes are rejected before provider access. This narrow profile supports ASCII path segments only.
- The endpoint must be the exact HTTPS Scaleway regional endpoint for the selected region. Certificate verification stays enabled. The SDK uses path-style addressing, SigV4, explicit credentials, no ambient proxy or endpoint override, bounded connection/read timeouts and one total attempt. A send-time destination check also rejects redirects to another host.
- Choose a **named static profile** in the local `~/.aws/credentials` file, or `accessKeyEnv` and `secretKeyEnv` environment-variable references, optionally `sessionTokenEnv`. There is no implicit default profile, unrelated AWS credential fallback, metadata service, credential process or SSO flow. Deployments needing managed credentials require a later adapter/profile.
- Only `HeadObject` and `GetObject` are used. No listing, upload, deletion, bucket creation, versioning change or IAM modification is performed by the connector. Provider credentials should permit only the agreed prefix and the required object/version reads; application filtering is not a substitute for provider IAM.
- `HeadObject` selects a provider version when one exists. The subsequent `GetObject` specifies that version and `If-Match`; on unversioned objects it uses `If-Match`. Response version, ETag and length must match. ETag is an opaque condition, never a content digest.
- Acquired bytes are bounded to 1 MiB. The connector computes SHA-256 and saves a private immutable local snapshot. Future reads require current Wallet authority and revalidate those bytes. Provider changes/outages do not rewrite retained versions. Revoking provider credentials alone does not recall already captured local copies; revoke the Farmy grant to deny future consumers.
- Readiness reports the Wallet dependency, not provider connectivity. Capture attempts are the current provider check. Monitoring exposes counts/activity only, not bucket names, keys, endpoints or credentials. The provider's native version ID/ETag are used during acquisition but are not yet exposed as public provenance fields.

The optional [snapshot helper](../../../sdk/python/farmy_transport/snapshots.py) is shared by the two reference storage connectors. It owns each connector's private snapshot files/SQLite store and shared read checks. Provider-specific acquisition stays in its implementation; independent providers need not use this helper. Local Folder keeps the same database schema and safe filesystem reader.

## Provider semantics and current evidence

Scaleway documents its [regional endpoints and S3 compatibility](https://www.scaleway.com/en/docs/object-storage/concepts/), [supported API operations](https://www.scaleway.com/en/docs/object-storage/api-cli/using-api-call-list/) and [versioning behaviour](https://www.scaleway.com/en/docs/object-storage/how-to/use-bucket-versioning/). The SDK documents [`GetObject` version/condition parameters](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/get_object.html) and [configuration controls](https://docs.aws.amazon.com/boto3/latest/guide/configuration.html). These references informed the adapter; documentation compatibility is not tested provider compatibility.

Local tests exercise real SDK HTTP requests against an intentionally small test double, with synthetic credentials. The double observes signed-request headers but is not a SigV4 verification implementation. It tests version selection, overwrite conflict, prefix confinement, denied/unavailable/missing objects, bounded responses, unchanged processing/export paths, persistence and grants. It cannot establish real IAM, TLS, region, checksum or provider error behaviour. Complete the real run described in UC-007 before marking the slice delivered.
