# Security and trust model

Status: requirements, not implemented guarantees.

See the [proposed module communication/security design](module-communication.md) for per-hop checks and complete workflows. Its identity and grant mechanisms remain proposals pending security ADRs.

## Trust boundaries

Identify farmer device, each hosting operator, each model provider, source provider and external recipient separately. Encryption at rest does not hide plaintext from an authorised processor. Stronger operator-blind processing requires a separate evaluated design and is not promised here.

## Required controls

- Authenticate humans, services and agents. Authorise each action against the wallet, resource, purpose, audience and scope.
- Deny access by default. Check permissions before content is retrieved or passed to models.
- Encrypt communications and platform-managed persistent data, including indexes, queues, backups and derived text.
- Store secrets outside versioned configuration. Separate data-plane credentials from deployment administration.
- Permit only approved egress destinations; local-model failure must not trigger unapproved cloud routing.
- Treat documents, retrieved passages and model outputs as untrusted data. They cannot grant tools, expand permissions or override system policy.
- Validate ingestion output, preserve originals and use explicit authority for writing accepted records.
- Record access, grants, changes, exports, processing destinations and cancellation/revocation outcomes. Avoid copying sensitive prompts into general logs.
- Bound offline authorisations by expiry and document revocation latency.
- Use source-version checks, idempotency and durable audit/outbox coordination.

## Deployment enforcement

Cloud deployments must meet the [provider landing-zone requirements](cloud-landing-zones.md). Cloud IAM, Kubernetes RBAC and wallet grants are distinct controls. Verify secrets protection and network enforcement in each provider implementation before advertising support. Laptop release profiles must document OS permissions, secret storage and background-service identity. These remain unimplemented requirements.

## Deletion and withdrawal

Specify handling of original, cached, staged, indexed and backup copies. Request downstream deletion and record acknowledgement; distinguish a requested action from verified completion. Revoking future access cannot recall recipient copies. Deletion may require index rebuilds.

## Credentials and anonymisation

A signed claim identifies its issuer; signature validity is not proof that an AI inference is true or officially certified. Anonymisation is a transformation requiring an explicit re-identification assessment, not a guarantee from removing names alone.

## Threat-driven acceptance tests

Cross-wallet retrieval denial; revoked/expired grant rejection; malicious document tool-request rejection; blocked fallback egress; stale-version mutation rejection; duplicate job handling; secret-free exported configuration; index deletion propagation; backup/key recovery; offline authorisation expiry. Implement these alongside the affected components.
