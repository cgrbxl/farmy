# Directory Connector

Generic read-only provider for a selected nested local directory. Owns its handle/path catalogue and immutable managed snapshots. Source data remains outside Wallet membership until explicit admission. No farm-specific schema, dataset location or domain logic is embedded.

See [UC-012](../../../solutions/directory/uc012/README.md) for launch instructions, limits, contracts and verification. This reference reuses managed-folder authorisation and snapshot components; it demonstrates another provider, not a wholly independent implementation of the transport stack.
