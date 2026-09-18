"""Offline structural/compatibility checks; NOT authentication or runtime admission."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'contracts' / 'v0.1-draft'
SCHEMA = json.loads((CONTRACT / 'foundation.schema.json').read_text())
KINDS = ('module', 'instance', 'binding', 'environment', 'request', 'response')


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError('Non-finite numbers are not JSON')


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant)


def validate(kind, data):
    if kind not in KINDS:
        raise ValueError('Unknown document kind')
    schema = dict(SCHEMA, **{'$ref': '#/$defs/' + kind})
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
    # An https prefix alone does not rule out userinfo, fragments or malformed ports.
    urls = []
    if kind == 'instance':
        urls.append(data['endpoint'])
    elif kind == 'environment':
        urls.extend(data['allowedEgress'])
    for url in urls:
        parsed = urlsplit(url)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or parsed.query or parsed.fragment
                or any(c.isspace() for c in url) or '\\' in url):
            raise ValueError('Endpoint must be HTTPS without userinfo, query or fragment')
        try:
            port = parsed.port
        except ValueError as exc:
            raise ValueError('Invalid endpoint port') from exc
        if port == 0:
            raise ValueError('Invalid endpoint port')
    if kind == 'module':
        for key, field in [('capabilities', 'capabilityId'), ('dependencies', 'capabilityId'),
                           ('targets', 'target')]:
            ids = [item[field] for item in data[key]]
            if len(ids) != len(set(ids)):
                raise ValueError('Duplicate ' + field)
    if kind == 'request' and any(r['walletId'] != data['walletId'] for r in data['inputRefs']):
        raise ValueError('Cross-wallet inputs require a later explicit profile')


def compatible(module, instance, binding, environment):
    """Check declared compatibility only. Does not grant access or activate a binding."""
    for kind, data in [('module', module), ('instance', instance),
                       ('binding', binding), ('environment', environment)]:
        validate(kind, data)
    if (instance['implementationId'], instance['implementationVersion']) != (
            module['implementationId'], module['implementationVersion']):
        raise ValueError('Instance does not match implementation release')
    if binding['instanceId'] != instance['instanceId']:
        raise ValueError('Binding points at another instance')
    if instance['environmentId'] != environment['environmentId']:
        raise ValueError('Instance points at another environment')
    if not (instance['securityProfile'] == environment['securityProfile']
            and instance['securityProfile'] in module['securityProfiles']):
        raise ValueError('Security profile mismatch')
    if not (instance['connectivityMode'] == environment['connectivityMode']
            and instance['connectivityMode'] in module['connectivityModes']):
        raise ValueError('Connectivity profile mismatch')
    target = next((t for t in module['targets'] if t['target'] == environment['target']), None)
    if target is None or target['status'] == 'unsupported':
        raise ValueError('Target not advertised or explicitly unsupported')
    capability = next((c for c in module['capabilities']
                       if c['capabilityId'] == binding['capabilityId']), None)
    if capability is None or capability['contractVersion'] != binding['contractVersion']:
        raise ValueError('Capability or exact draft version mismatch')
    if not set(binding['operations']) <= set(capability['operations']):
        raise ValueError('Required operation missing')
    if not set(binding['requiredFeatures']) <= set(capability['features']):
        raise ValueError('Required semantic feature missing')
    return {'declaredCompatibility': True, 'targetStatus': target['status'],
            'runtimeVerified': False, 'accessGranted': False,
            'unresolvedRequiredDependencies': [d['capabilityId'] for d in module['dependencies']
                                               if d['required']]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=KINDS)
    parser.add_argument('--file', type=Path)
    args = parser.parse_args()
    if bool(args.kind) != bool(args.file):
        parser.error('--kind and --file must be supplied together')
    Draft202012Validator.check_schema(SCHEMA)
    if args.kind:
        validate(args.kind, load(args.file))
        print('Structure valid; runtime, trust and operation payload semantics NOT verified.')
        return
    examples = CONTRACT / 'examples'
    count = 0
    for path in sorted(examples.glob('*.json')):
        kind = path.stem.split('-')[0]
        validate(kind, load(path))
        count += 1
    module, instance, binding = [load(examples / (k + '.json'))
                                 for k in ('module', 'instance', 'binding')]
    for target in ('macos', 'windows', 'linux', 'kubernetes'):
        environment = load(examples / ('environment-' + target + '.json'))
        variant = dict(instance, environmentId=environment['environmentId'])
        result = compatible(module, variant, binding, environment)
        print(target + ': ' + json.dumps(result, sort_keys=True))
    print(f'{count} fixtures structurally valid. Four declared-profile combinations checked; '
          'no deployment, authentication or operation payload validation performed.')


if __name__ == '__main__':
    try:
        main()
    except ValidationError as exc:
        # Do not echo a potentially sensitive input document in a traceback.
        raise SystemExit('Validation failed: schema constraint ' + str(exc.validator)) from None
    except (ValueError, OSError):
        raise SystemExit('Validation failed: invalid document, reference or compatibility declaration') from None
