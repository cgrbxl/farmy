# Optional bounded processor on Scaleway

Status: experimental deployment implementation, locally tested HTTP and installer guards. No image has yet been published by this increment and no Scaleway deployment has been validated. On 2026-10-03 the Linux AMD64 image built successfully on the Mac; the actual container passed health, exact-result and tamper-rejection checks with a non-root user, read-only filesystem, dropped capabilities and no request logs.

This profile deploys **only** a stateless text-statistics processor. Farmy's Library and Wallet stay on the participant's laptop. No central Farmy service, Kubernetes, cloud database, wallet key or farm directory is required. Use a separate Farmy project in your existing Scaleway account, independent of onmygarage. Other participants use their own project/account.

## 1. Obtain and publish the module from GitHub

After this change is published to the repository, clone `https://github.com/cgrbxl/farmy` (or your fork), select a reviewed commit, and inspect this directory. Do not execute an unreviewed downloaded installation script.

A maintainer runs **Actions → Publish bounded processor → Run workflow** at that commit. The workflow tests the HTTP interface, builds Linux AMD64 from only the bounded processor directory, and publishes `ghcr.io/OWNER/REPOSITORY/bounded-text`. It needs only the temporary GitHub Actions token; **no Scaleway credentials belong in GitHub**. Make the resulting package public in GitHub Packages, then copy the complete `@sha256:…` image reference from the run summary. A private GHCR package will not work with this profile.

The Dockerfile uses a versioned Python base tag and refreshes it on each build. Builds can therefore differ; deployments pin the resulting image digest. Base-image digest pinning, vulnerability review and signed release provenance are still release-hardening work, not claims made by this prototype.

## 2. Prepare your own Scaleway environment

Install the official Scaleway CLI (the command interface was checked against local version 2.60.0; incompatible interfaces are rejected) and run `scw init` **in your own terminal**. Authenticate with a project-scoped deployment principal; never paste API keys into chat, source files or screenshots. Scaleway's CLI manages its local credential configuration. Protect that file and do not enable CLI debug logging while using credentials.

In the Scaleway console:

1. Select/create a separate Farmy project and note its public project UUID.
2. Create an empty Serverless Containers namespace in that project and note its UUID and region (`fr-par`, `nl-ams`, or `pl-waw` in this initial profile). Leave namespace environment variables and secrets empty. Namespace creation can also create registry resources.
3. Review current charges and configure billing alerts. Scaling to zero and one maximum instance limit capacity, **not monthly expenditure**.

The deployment principal needs namespace read, container list/create/get permissions for the chosen project. Use a separate narrowly scoped principal or revocable container token for invocation; do not give the processor the deployment key. Exact IAM policy and revocation must be checked in the participant's environment before real data is used.

## 3. Run the guided installer

From the repository root:

```sh
python3 deployments/providers/scaleway/install.py
```

It asks for project UUID, empty namespace UUID, region, container name and immutable public image reference. It reads the namespace to check project/region, rejects inherited environment variables/secrets and existing containers, and shows the complete resource plan. Enter stops without creating resources. Typing the project UUID approves creation of one private container: 256 MB, 250 mCPU, minimum zero/maximum one instance, ten-second provider timeout, port 8080, HTTPS-only access and health check.

Credentials are neither requested nor stored by the installer. They remain under the local Scaleway CLI's control and are sent to Scaleway for API authentication. The script stores only a plan, status and container ID in an ignored `.farmy/deployments/` receipt. It never prints raw provider responses. A pending receipt or existing container blocks blind retries after an ambiguous failure: inspect the console and receipt first. Do not remove the receipt until you have reconciled whether creation succeeded.

Creation submission is **not** a successful deployment claim. Image pulls, quotas, readiness and provider configuration still require verification.

## 4. Verify before using

In the Scaleway console, verify the exact image digest, `private` privacy, selected project, limits and ready status. Obtain the HTTPS endpoint there. An unauthenticated request must be denied by Scaleway (normally 403), including `/health`. Authenticated `/health` must return `{"status":"ok"}`. Use the console or a local client that reads the separate invocation credential privately; never put a literal key in shell history or URLs.

`POST /process` accepts the existing `farmy.processing.text/0.1-draft` request with receiver **`processor.scaleway`**, purpose `text-statistics`, request ID and one exact digest-bound UTF-8 evidence item (maximum 16 KiB). It returns statistics bound to that input and request. Duplicate fields, malformed/tampered evidence and the local receiver ID are rejected. The request body ceiling is 64 KiB; processing is single-threaded. Nothing is persisted by the application and request logging is disabled. The provider can still observe traffic/metadata and operate its infrastructure.

This adapter relies on authenticated private Scaleway ingress; it has no standalone internet-facing authentication. Never expose port 8080 publicly or deploy it with public privacy. **Platform authentication is not a Farmy Wallet grant.** Remote delegated grants, replay budgets, trusted endpoint binding and integration with the Mac approval gate remain outstanding. Use synthetic text only in this profile until those are implemented. A request ID correlates results; this stateless processor does not promise exactly-once execution.

Record successful authenticated and denied requests, region, image digest, runtime limits and credential-revocation results before declaring provider support validated. No automatic connection from the installed Mac apps is made.

## Updates and removal

For this first profile, review and deploy a new immutable image through a fresh empty namespace, validate it, switch clients explicitly, then remove the old container. The installer intentionally does not overwrite a running deployment. Keep the old image digest for rollback.

The installer prints the command to delete the exact created container; confirm its ID against the receipt. Delete leftover namespace/registry resources separately in the console after checking their contents and billing. Namespace deletion may also delete its associated registry: never use it as a general cleanup shortcut.

## Verification and sources

```sh
python3 -m unittest discover -s conformance/scaleway -v
```

Five local tests cover private bounded configuration, immutable-image validation, namespace isolation and actual HTTP positive/negative cases. They do not substitute for cloud IAM, image-build or provider acceptance tests.

- [Scaleway container API and private access](https://www.scaleway.com/en/developers/api/serverless-containers)
- [Scaleway CLI container commands](https://github.com/scaleway/scaleway-cli/blob/main/docs/commands/container.md)
- [External images and Scaleway registries](https://www.scaleway.com/en/docs/serverless-containers/api-cli/migrate-external-image-to-scaleway-registry/)
- [Securing a container](https://www.scaleway.com/en/docs/serverless-containers/how-to/secure-a-container/)

The broader [provider plan](../../../docs/providers/scaleway.md) keeps Kubernetes as an optional future profile.
