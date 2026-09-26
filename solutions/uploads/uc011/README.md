# UC-011 — Upload and control a document

Upload a local file through the Connector, review its exact bytes, then explicitly admit a managed copy to the Wallet. Uploading grants no consumer access.

```sh
.venv/bin/python solutions/uploads/uc011/run.py launch
```

Open the private URL printed by the runner. Choose a UTF-8 `.txt`, `.md`, `.csv` or `.eml` file up to 16 KiB and click **Upload to local source**. Review the preview. The default is **Only me (private)**; choose **Owner and demo consumer** if you want to test sharing, then **Add to my Wallet**. Open the consumer view to see denial, grant access as owner, retry the read, then revoke and retry again.

This runner uses a temporary local workspace, unencrypted storage and one-hour development grants. Stopping it discards uploads and state; your original file is untouched. No cloud service receives the file. PDF, Word, images, larger files and persistent user workspaces are outside this increment. Use non-sensitive test files.

## Component boundary

The optional `farmy.folder-upload` capability adds `folder.upload` under the [UC-011 contract](../../../contracts/uc011/README.md). It is disabled unless the Connector opts in. The authenticated owner must match the source owner; the Wallet must authorise source append before the Connector writes. The bridge uses public contracts and owns only its request/receipt ledger. Wallet domain code is unchanged.

Names are normalised into a bounded entry containing the SHA-256 digest. Path traversal, symlinks, unsupported extensions, non-UTF-8 data and binary control characters are rejected. Different content never overwrites a prior entry. File publication uses a synced temporary file and a no-overwrite hard link, followed by directory sync. A database transaction serialises upload receipts and enforces a 100-entry source limit. Repeated content can reuse its entry even at capacity.

Retries preserve the original request and key across lost replies and service/bridge restarts. A conflicting key fails. If publication succeeds before the receipt transaction commits, retry recognises the exact existing bytes and records the receipt. A process crash before publication may leave a hidden temporary file; these count toward capacity and require operator cleanup while the service is stopped. The source directory must remain under operator control; this is not isolation against another process with filesystem write access.

The browser defaults uploaded items to private and renders content as text. Upload does not imply admission, grant, extraction or model processing. The existing loopback, Origin, bearer-token and CSP protections apply. Production human authentication, key custody, encrypted storage, quotas across tenants and cross-platform filesystem validation remain separate component work.

## Verification

```sh
.venv/bin/python -m unittest discover -s conformance/uc011 -v
.venv/bin/python solutions/uploads/uc011/run.py demo
.venv/bin/python scripts/verify.py --with-local-model --with-s3-fixture
```

Eleven upload acceptance cases cover exact-byte admission/sharing/revocation, caller restrictions, disabled capability, file validation and size boundaries, no overwrite, symlink rejection, capacity, retry/restart/conflict, lost replies, Wallet outage and inert HTML. Shared transport registration also requires the earlier slices to pass.

Verified on 2026-09-25: **137 tests and 11 demos passed**, including the installed local model and optional S3 HTTP fixture. Browser verification confirmed the real file picker, upload, exact text preview and private default. Local fixture checks do not establish Scaleway compatibility.
