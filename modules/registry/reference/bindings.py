"""Minimal revisioned binding adapter; not a running registry/catalogue service."""
import json
from pathlib import Path
from farmy_transport.http import Fault, FOUNDATION, schema_check


def resolve(path, wallet, capability, operation, version="0.1-draft"):
    binding = json.loads(Path(path).read_text())
    schema_check(FOUNDATION, 'binding', binding)
    if (binding['walletId'] != wallet or binding['capabilityId'] != capability
            or binding['contractVersion'] != version or operation not in binding['operations']):
        raise Fault('unsupported')
    return binding


def admit(config, binding):
    """Check the pinned peer's current declarations; never issue a permission."""
    from farmy_transport.http import exchange
    target = binding['instanceId']
    if target not in config['endpoints']:
        raise Fault('unsupported')
    info = exchange(config, target, path='/farmy/v0/descriptor')
    try:
        module, instance = info['module'], info['instance']
        schema_check(FOUNDATION, 'module', module)
        schema_check(FOUNDATION, 'instance', instance)
        capabilities = [c for c in module['capabilities'] if c['capabilityId'] == binding['capabilityId']]
        if (len(capabilities) != 1 or instance['instanceId'] != target
                or instance['endpoint'] != config['endpoints'][target]['url']
                or instance['environmentId'] != config['environmentId']
                or instance['peerIdentity'] != 'urn:farmy:identity:' + target
                or (instance['implementationId'], instance['implementationVersion']) !=
                   (module['implementationId'], module['implementationVersion'])
                or instance['securityProfile'] != 'farmy.mtls-online/0.1-draft'
                or instance['securityProfile'] not in module['securityProfiles']
                or instance['connectivityMode'] != 'direct-https'
                or instance['connectivityMode'] not in module['connectivityModes']
                or not any(t['target'] == 'macos' and t['status'] != 'unsupported' for t in module['targets'])):
            raise Fault('unsupported')
        capability = capabilities[0]
        if (capability['contractVersion'] != binding['contractVersion']
                or not set(binding['operations']) <= set(capability['operations'])
                or not set(binding['requiredFeatures']) <= set(capability['features'])):
            raise Fault('unsupported')
    except (KeyError, TypeError, ValueError):
        raise Fault('unsupported') from None
    return target
