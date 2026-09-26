# macOS local profile — Farmy 0.1.0

Status: experimental persistent local installation, verified on macOS 26.6.2 arm64 / Python 3.14.6. No Farmy cloud service is required. This installs the existing Wallet, read-only directory Connector and interactive client; it is not yet the full Copilot/Hub/Control experience.

## Installed on the development Mac

The current user installation is `~/.local/share/farmy`, with a convenience launcher at `~/.local/bin/farmy`. Persistent state is separate at `~/Library/Application Support/Farmy`. An optional `FARMY_HOME` or `--home PATH` selects a different private workspace. The selected source is `docs/data_v2` in the checkout; the executable does not depend on the checkout, but that explicitly configured source naturally does.

```sh
farmy status
farmy open
farmy doctor
```

`open` opens a fresh private owner link. Browser credentials rotate after restarting the supervisor, so old bookmarked access links stop working. The default local port is 54800, chosen at initialisation. All listeners are loopback-only.

## Build and install without a source checkout

Build an artifact on the intended platform and Python minor version:

```sh
.venv/bin/python packaging/macos/build.py --output .farmy/releases
```

The builder downloads pinned dependency wheels. Subsequent builds can use `--wheels PATH` offline. The archive contains code, contracts, client assets, dependency wheels, a checksum manifest and the installer; it excludes datasets, video, user state and credentials. An artifact SHA-256 is written alongside it. Per-file checksums detect corruption; they are not publisher signatures. The recorded source revision is the base commit; file digests identify included working-tree changes.

Unpack the verified archive into a new directory, then run its `install.py` with Python 3.14. The installer checks platform/Python compatibility and the file manifest, installs dependencies offline into an isolated environment, validates the CLI, and switches a stable launcher to the versioned release. It requires the declared Python interpreter and OpenSSL already installed. It is not a native signed/notarised application bundle.

```sh
python3.14 /path/to/unpacked/farmy/install.py
~/.local/share/farmy/bin/farmy init --source /absolute/path/to/test-folder
~/.local/share/farmy/bin/farmy service-install
~/.local/share/farmy/bin/farmy open
```

Initialisation never overwrites an existing workspace. Source and runtime directories must be separate trees. `--prefix PATH` chooses another installation location. Installation and initialisation are separate: unpacking software grants no source access.

## Lifecycle and login service

```sh
farmy service-remove   # unregister login startup and wait for shutdown
farmy start            # start manually in the background
farmy stop             # stop manually; retain workspace data
farmy service-install  # register and start again at user login
```

Choose one mode; workspace locks reject duplicate supervisors. Login service removal waits for the runtime to release the workspace. The login service uses the stable installed launcher, so later compatible releases do not need a new executable path. It starts on login; it does not continuously restart a broken composition. Installation into a running workspace is refused.

The supervisor stops the composition if a module exits. Per-module guards stop children when their supervisor pipe closes, including supervisor SIGKILL. Separate module locks prevent overlapping access during recovery. This is process supervision, not protection against a malicious process running as the same OS user. Killing the guard itself or machine power loss remains OS/recovery territory.

Service identities and their CA are regenerated on startup, with private state paths preserved. The supervisor also schedules transport replacement every twelve hours; the two-day certificate lifetime is not extended. This can briefly interrupt requests. The full twelve-hour timer and extended sleep/wake behaviour have not yet been exercised. Owner source access is explicitly established at initialisation and maintained by the local owner bridge; consumer grants are never automatically renewed, and revocations survive restarts. Owner reads acquire fresh short-lived grants instead of relying on the original import time.

## Backup, restore, update and removal

```sh
farmy service-remove
farmy backup /absolute/path/to/new-backup-directory
farmy --home /absolute/path/to/new-restored-workspace restore /absolute/path/to/new-backup-directory
farmy service-install
```

Backups require a stopped workspace and a new destination. They contain private Wallet/Connector/client state and exact snapshots, but not source files, logs or generated transport credentials. Protect backups as private data. Checksums are verified during restoration; restoring overwrites nothing and rejects symlinks. The source path is retained and must exist before starting the restored installation. Start only one copy if both configurations use the same port. Fresh transport/browser credentials are created on start; resource identities and permission state are preserved.

Stop before installing another release into the same prefix. Compatible development-build replacement and state retention were tested. There is no advertised older schema migration or downgrade path yet; unknown schemas are rejected. Retain a verified backup before future schema-changing upgrades.

To uninstall, unregister the login service and remove only the software prefix/convenience launcher. Workspace and backup directories are deliberately separate and must not be deleted implicitly. OS-user file permissions protect local keys/state; Keychain integration and application-level encryption are not implemented.

## Homebrew route

The builder emits `farmy.rb` with an immutable artifact checksum, Python/OpenSSL dependencies and a background-service definition. Its current URL is a **local file URL**, not a published tap/release. A local development tap was prepared at `cgrbxl/farmy`; installation stopped at Homebrew's prerequisite check because Xcode 16.4 is older than required by the current toolchain. Farmy itself was installed through the standalone installer. Do not claim a tested Homebrew install or recommend upgrading unrelated tools solely to run this build. The formula still needs verification in a compatible Homebrew environment and a published immutable artifact URL before distribution.

## Evidence and remaining work

2026-09-26: 154 tests and 12 demos passed, including eight lifecycle scenarios (the full regression selection plus a final targeted shutdown check): stable copies/revocations with credential rotation; stopped backup/restore; duplicate-start/consumer-stop rejection; safe initialisation; abrupt supervisor-exit recovery; occupied-port failure recovery; unsupported schema/unsafe-backup rejection; draining in-flight requests before releasing the workspace. Earlier module tests and local-model/S3-fixture demos passed.

The standalone artifact installed offline outside the checkout. Real launchd registration/start/removal/re-registration, runtime diagnosis, stopped backup and a compatible development-build replacement were exercised on this Mac. Browser admission followed by installed-service restart verified retained managed state.

Clean-machine installation, public artifact signatures, native Keychain custody, large-file contracts, retention/log maintenance, long-duration operation, real logout/reboot and other OS/architecture targets remain unverified. The next functional milestone is the [shared application composition](../../../docs/deployment-plan.md), not mandatory cloud infrastructure.
