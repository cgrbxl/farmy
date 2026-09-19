"""UC-003: one source permission covers ongoing synthetic observations."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('core_runtime', ROOT / 'solutions/core/uc001/run.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
from farmy_transport.http import exchange, request, utc

# Retain the Wallet's existing document dependency without changing its contract.
SERVICES = dict(core.SERVICES, **{'sensor.local': 'modules/connectors/synthetic_sensor/service.py'})


def bootstrap(directory):
    directory = core.bootstrap(directory, SERVICES)
    for identity in [*SERVICES, 'owner', 'reader', 'denied', 'unknown']:
        path = directory / (identity + '.json')
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc003-local', bootstrapProfile='uc003.bootstrap')
        if identity == 'wallet.local':
            config.update(sourceConnectors=['sensor.local'], implementationVersion='0.3.0')
        if identity == 'sensor.local':
            config.update(implementationId='farmy.reference.synthetic-sensor', implementationVersion='0.1.0')
        path.write_text(json.dumps(config, indent=2))
    return directory


def call(directory, operation, payload=None, identity='owner', **kwargs):
    target = 'sensor.local' if operation.startswith('sensor.') else 'wallet.local'
    config = core.config(directory, identity)
    return exchange(config, target, request(config, target, operation, payload or {}, **kwargs))


def scope(source):
    return {key: source[key] for key in ('sourceId', 'ownerId')}


def register(directory):
    return call(directory, 'source.register', {'connectorId': 'sensor.local'})


def append(directory, source, value, key=None):
    return call(directory, 'sensor.append', dict(scope(source), observedAt='2026-09-19T12:00:00Z',
                                                value=value, unit='degC'), key=key)


def grant(directory, source, consumer='reader', seconds=600):
    return call(directory, 'source.grant', dict(scope(source), consumerId=consumer, expiresAt=utc(seconds)))


def read(directory, source, permission, identity='reader', after=0, limit=100):
    return call(directory, 'sensor.read', dict(scope(source), afterSequence=after, limit=limit),
                identity=identity, grant=permission['grantId'])


def audit(directory, source):
    return call(directory, 'sensor.audit', dict(scope(source), limit=10))['receipts']


def demo(directory):
    with core.Processes(directory, SERVICES) as processes:
        first, separate = register(directory), register(directory)
        a = append(directory, first, 18.5)
        b = append(directory, first, 19.0)
        append(directory, separate, 30.0)
        permission = grant(directory, first)
        result = read(directory, first, permission)
        assert [o['observationId'] for o in result['observations']] == [a['observationId'], b['observationId']]
        later = append(directory, first, 19.5)
        fresh = read(directory, first, permission, after=b['sequence'])
        assert fresh['observations'] == [later]
        print('PASS one source grant covers existing and subsequently added observations')
        core.expect_fault('denied', lambda: read(directory, separate, permission))
        core.expect_fault('denied', lambda: read(directory, first, permission, 'denied'))
        core.expect_fault('unauthenticated', lambda: read(directory, first, permission, 'unknown'))
        print('PASS separate source and unauthorised consumers remain inaccessible')
        receipts = audit(directory, first)
        matching = next(r for r in receipts if r['deliveryId'] == fresh['deliveryId'])
        assert matching['consumerId'] == 'reader' and matching['grantId'] == permission['grantId']
        assert matching['observations'][0]['observationId'] == later['observationId']
        print('PASS release records link consumer, source, permission and exact observations')
        for service in ('wallet.local', 'sensor.local'):
            processes.stop(service)
            processes.start(service)
        assert len(read(directory, first, permission)['observations']) == 3
        assert any(r['deliveryId'] == fresh['deliveryId'] for r in audit(directory, first))
        print('PASS source identity, observations, grants and release records survive restart')
        call(directory, 'source.revoke', {'grantId': permission['grantId']}, revision=1)
        core.expect_fault('denied', lambda: read(directory, first, permission))
        replacement = grant(directory, first)
        processes.stop('wallet.local')
        core.expect_fault('unavailable', lambda: read(directory, first, replacement))
        print('PASS revocation and unavailable authority stop subsequent reads')
    print('Demo complete. All three processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo', 'bootstrap', 'serve', 'request'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--service', choices=['wallet', 'connector', 'sensor'])
    parser.add_argument('--identity', choices=['owner', 'reader', 'denied'], default='owner')
    parser.add_argument('--operation')
    parser.add_argument('--payload', default='{}')
    parser.add_argument('--grant', default='grant.owner-bootstrap')
    parser.add_argument('--key')
    parser.add_argument('--revision', type=int)
    args = parser.parse_args()
    if args.action == 'demo':
        if args.directory is not None:
            parser.error('demo uses fresh temporary state')
        with tempfile.TemporaryDirectory(prefix='farmy-uc003-') as directory:
            demo(bootstrap(directory))
    elif args.directory is None:
        parser.error('--directory is required')
    elif args.action == 'bootstrap':
        print(bootstrap(args.directory))
    elif args.action == 'serve':
        if not args.service:
            parser.error('--service is required')
        os.execve(sys.executable, core.command(args.directory, args.service + '.local', SERVICES), core.environment())
    else:
        if not args.operation:
            parser.error('--operation is required')
        print(json.dumps(call(args.directory, args.operation, json.loads(args.payload), identity=args.identity,
                              grant=args.grant, key=args.key, revision=args.revision), indent=2))


if __name__ == '__main__':
    main()
