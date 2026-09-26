# Local Mac release tooling

`build.py` creates a platform/Python-specific archive, SHA-256 file and a local Homebrew formula. `install.py` installs an unpacked archive with bundled dependency wheels and a stable launcher; it does not initialise user data or grant source access.

See the [macOS profile](../../deployments/profiles/macos/README.md) for commands, evidence and known limits. Homebrew installation remains unverified because the development machine's Xcode prerequisite failed. Do not publish the generated local-file formula as a public tap.
