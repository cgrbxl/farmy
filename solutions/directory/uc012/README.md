# UC-012 — Connect a read-only directory

Farmy is an evolving modular concept explored through concrete use cases. This increment adds a generic directory Connector; the simulated farm dataset is an optional exploration fixture, never an implementation dependency.

```sh
.venv/bin/python solutions/directory/uc012/run.py launch --source /absolute/path/to/test-folder
```

For the supplied exploration dataset, use `--source docs/data_v2` from the repository root. Open the private local URL printed by the runner. Relative paths distinguish files with identical names. Preview a supported file, choose its permitted readers and explicitly add it to the Wallet. New previews default to private. To test sharing, choose **Owner and demo consumer**, admit, then grant access, read in the separate consumer view and revoke.

The source is read-only: browsing and admission never upload, rename or write there. Only selected admissions create managed snapshots in the Connector's own temporary state. Closing the browser does not stop services; stopping the runner discards that temporary state. Source files remain untouched. This runner uses local test identities and one-hour grants, not production human authentication.

## Bounded generic behaviour

- Recursive catalogue: up to 100 visible regular files, eight directory levels, 2,000 examined entries, and relative paths of at most 160 characters. Exceeding a bound fails explicitly rather than returning a partial catalogue.
- Hidden entries, symlinks and special files are excluded. Reads open every path component without following symlinks; a changed directory cannot redirect reads outside the selected root.
- TXT, Markdown, CSV, email exports, JSON, GeoJSON and XML can be previewed as inert UTF-8 text up to 16 KiB. Encoding is checked on read. Other formats and larger files remain visible with an explanatory disabled preview. No XML execution, JSON interpretation or table analysis occurs.
- Catalogue entries use deterministic opaque handles based on relative path. The Connector persists handle-to-path mappings; the Wallet retains that handle, source identity, exact digest and the relative path as display title. A rename changes the entry handle. Admitted resource/version identity stays independent and immutable.
- An admission checks the preview digest against the current source. Changed bytes fail. Managed copies remain available under their own grants after source edits or deletion. Revocation blocks future reads but cannot recall bytes already delivered.

Folder hierarchy and exact bytes are preserved as provenance; semantic joins, data-model relationships, automatic discovery of linked records, bulk admission and analysis are not implemented. File ownership and configured source roots remain operator trust boundaries. An adversarial local process with write access is outside this profile; the digest check detects changed content, but does not prove semantic authorship.

## Contracts and module impact

The new [folder.browse contract](../../../contracts/uc012/README.md) returns relative path, size, handle and preview limitation. Existing `folder.list`, `folder.read`, `folder.capture` and `read.version` contracts remain unchanged. An entry is an opaque provider identifier; this Connector resolves it privately, so Wallet needs no path semantics.

Expected and actual changes: a separate directory Connector, additive browse contract and transport registration, and a small client extension for catalogue labels and admission titles. **No Wallet domain or permission code changes.** The upload Connector stays available independently.

## Verification

```sh
.venv/bin/python -m unittest discover -s conformance/uc012 -v
.venv/bin/python solutions/directory/uc012/run.py demo
.venv/bin/python solutions/directory/uc012/run.py demo --source docs/data_v2
.venv/bin/python scripts/verify.py --with-local-model --with-s3-fixture
```

Nine generic HTTP/mTLS tests cover nested duplicate names, exact managed copies, grant/revoke, consumer metadata denial, unchanged source/upload denial, hidden entries/symlinks and replaced directories, stale previews, format/size/encoding rejection, restart stability, catalogue limits and Wallet outage. Tests and the default demo construct domain-neutral fixtures; they do not rely on the farm dataset.

Verified 2026-09-26 on the local macOS environment: **146 tests and 12 demos passed**, including the installed local model and optional S3 HTTP fixture. A separate run against the supplied dataset catalogued 57 files and completed admission/read/revocation. Browser checks verified path filtering, JSON preview, private default, admission and denial → grant → allowed → revoke → denied. Four dataset files exceed the current size profile.
