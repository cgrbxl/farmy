"""Minimal revisioned binding adapter; not a running registry/catalogue service."""
import json
from pathlib import Path
from farmy_transport.http import Fault, FOUNDATION, schema_check


def resolve(path, wallet, capability, operation):
    binding = json.loads(Path(path).read_text())
    schema_check(FOUNDATION, 'binding', binding)
    if (binding['walletId'] != wallet or binding['capabilityId'] != capability
            or binding['contractVersion'] != '0.1-draft' or operation not in binding['operations']):
        raise Fault('unsupported')
    return binding
