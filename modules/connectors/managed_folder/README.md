# Managed Folder reference implementation

One configured flat local folder is a collectively governed source; selected content can become an immutable individually governed copy. Wallet owns item identity, provenance and grants. This Connector owns source access and snapshot bytes.

See [UC-009](../../../solutions/managed-items/uc009/README.md), its [contract](../../../contracts/uc009/README.md) and the [source/item distinction](../../../docs/sources-and-managed-items.md). Configuration adds `sourceReaderCeiling` to the existing pinned mTLS local-folder settings. The ceiling limits admitted-copy readers; source grants separately authorise original contents. This is synthetic development code, not a real mailbox adapter or encrypted vault.
