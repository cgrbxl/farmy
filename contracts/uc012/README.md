# UC-012 directory catalogue — 0.12-draft

`folder.browse` is a read operation under `farmy.directory`, purpose `uc012.folder.browse`. Input is the existing source/owner scope. Output is at most 100 entries containing opaque `entry`, relative `path`, byte `size` and `reason` (empty when size/format permit attempting a preview). UTF-8 validity is checked when read; empty reason does not promise valid text or parsed content. See [schema](operations.schema.json) and [operation metadata](operations.json).

The authenticated caller must match the subject, possess a current source read grant and address the mounted source/owner. Authorisation is checked before and after enumeration. Consumers with only a managed-item grant cannot browse source metadata. Unavailable authority fails closed.

Entries may be passed to the unchanged UC-009 read/capture/admission contracts. Handles are stable for a relative path within this configured source and survive service restart. They do not identify a byte version; the exact digest does. The catalogue is a current observation, not an atomic snapshot of a mutable directory. The client must preview and submit that digest to admission.

The reference provider excludes hidden entries, symlinks and non-regular files. Bounds, read-only semantics and recovery evidence are documented in [UC-012](../../solutions/directory/uc012/README.md). No pagination or automatic relationship inference is claimed.
