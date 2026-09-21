"""UC-006: preview, approve and deliver one exact synthetic document."""
import argparse
import base64
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

monitor = load('uc005_run', 'solutions/operations/uc005/run.py')
core = monitor.core
from farmy_transport.http import exchange, request, utc

SERVICES = dict(core.SERVICES, **{'exchange.local': 'modules/exchange/reference/service.py',
    'recipient.local': 'solutions/disclosure/uc006/recipient.py'})
SCOPES = [{'audience': 'exchange.local', 'operation': 'disclosure.' + op, 'purpose': 'uc006.' + op}
          for op in ('approve', 'deliver')]
INVENTORY = {'wallet.local': {'family': 'wallet', 'name': 'Wallet'},
             'connector.local': {'family': 'connectors', 'name': 'Local Folder'},
             'exchange.local': {'family': 'exchange', 'name': 'Controlled Exchange'}}


def bootstrap(directory):
    directory = core.bootstrap(directory, dict(SERVICES, **{'monitor.local': 'solutions/operations/uc005/server.py'}))
    import secrets
    for identity in [*SERVICES, 'monitor.local', 'owner', 'reader', 'denied', 'unknown']:
        path = directory / (identity + '.json')
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc006-local', bootstrapProfile='uc006.bootstrap',
                      compositionRevision=1)
        if identity in INVENTORY:
            config['monitorSubjects'] = ['monitor.local']
        if identity == 'wallet.local':
            config.update(readSubjects=['owner', 'reader', 'denied', 'exchange.local'], permissionScopes=SCOPES)
        if identity == 'connector.local':
            config['implementationVersion'] = '0.1.1'
        if identity == 'exchange.local':
            config.update(implementationId='farmy.reference.controlled-exchange',
                          implementationVersion='0.1.0', recipients=['recipient.local'])
        if identity == 'recipient.local':
            config['implementationId'] = 'farmy.fixture.recipient'
        if identity == 'monitor.local':
            config.update(inventory=INVENTORY, browserToken=secrets.token_urlsafe(32))
            config = {k: config[k] for k in ('identity','walletId','ca','cert','key','endpoints','inventory','browserToken')}
            config['endpoints'] = {k: dict(v, timeoutSeconds=3) for k, v in config['endpoints'].items() if k in INVENTORY}
        path.write_text(json.dumps(config, indent=2))
    return directory


def call(directory, operation, payload, identity='owner', **kwargs):
    target = 'recipient.local' if operation in ('receipt.inspect', 'disclosure.receive') else 'exchange.local'
    config = core.config(directory, identity)
    return exchange(config, target, request(config, target, operation, payload, **kwargs))


def permission(directory, resource, operation, subject='owner'):
    return core.call(directory, 'access.issue', dict(resourceId=resource['resourceId'],
        versionId=resource['versionId'], subjectId=subject, audience='exchange.local',
        operation='disclosure.' + operation, purpose='uc006.' + operation, expiresAt=utc(600)), refs=core.refs(resource))


def prepare(directory):
    resource = core.call(directory, 'resource.register', {'path': 'record.txt'})
    read = core.grant(directory, resource, 'exchange.local')
    preview = call(directory, 'disclosure.prepare', {'recipientId': 'recipient.local',
        'purpose': 'synthetic.review', 'sourceReadGrant': read['grantId']}, refs=core.refs(resource))
    approve_grant = permission(directory, resource, 'approve')
    deliver_grant = permission(directory, resource, 'deliver')
    return resource, read, preview, approve_grant, deliver_grant


def selection(preview):
    return {k: preview[k] for k in ('manifest', 'manifestHash')}


def approve(directory, resource, preview, grant):
    return call(directory, 'disclosure.approve', dict(selection(preview), expiresAt=utc(300)),
                refs=core.refs(resource), grant=grant['grantId'])


def deliver(directory, resource, preview, grant, **kwargs):
    return call(directory, 'disclosure.deliver', selection(preview), refs=core.refs(resource),
                grant=grant['grantId'], **kwargs)


def seed(directory):
    resource, read, preview, approval, delivery = prepare(directory)
    approve(directory, resource, preview, approval)
    receipt = deliver(directory, resource, preview, delivery)
    return resource, read, preview, approval, delivery, receipt


def demo(directory):
    with core.Processes(directory, SERVICES) as processes:
        resource, read, preview, approval, delivery = prepare(directory)
        print('Preview:', json.dumps(preview['manifest'], indent=2))
        print('Content:', base64.b64decode(preview['contentBase64']).decode().rstrip())
        core.expect_fault('denied', lambda: deliver(directory, resource, preview, delivery))
        approve(directory, resource, preview, approval)
        core.expect_fault('denied', lambda: deliver(directory, resource, preview, read))
        changed = json.loads(json.dumps(preview))
        changed['manifest']['recipientId'] = 'other.local'
        core.expect_fault('conflict', lambda: deliver(directory, resource, changed, delivery))
        changed = json.loads(json.dumps(preview))
        changed['manifest']['sha256'] = '0' * 64
        core.expect_fault('conflict', lambda: deliver(directory, resource, changed, delivery))
        print('PASS preview binds content, recipient and purpose; missing approval/export and altered manifests rejected')
        processes.stop('recipient.local')
        core.expect_fault('unavailable', lambda: deliver(directory, resource, preview, delivery, key='key.delivery'))
        processes.stop('exchange.local')
        processes.start('exchange.local')
        processes.start('recipient.local')
        receipt = deliver(directory, resource, preview, delivery, key='key.delivery')
        assert deliver(directory, resource, preview, delivery, key='key.delivery') == receipt
        received = call(directory, 'receipt.inspect', {'disclosureId': receipt['disclosureId']})
        assert base64.b64decode(received['contentBase64']) == core.V1 and received['receipt'] == receipt
        print('PASS delivery resumes after restart; exact bytes arrive once with a stable recipient receipt')
        core.call(directory, 'access.revoke', {'grantId': delivery['grantId']}, revision=1)
        core.expect_fault('denied', lambda: deliver(directory, resource, preview, delivery))
        processes.stop('wallet.local')
        core.expect_fault('unavailable', lambda: deliver(directory, resource, preview, delivery))
        print('PASS revoked export and unavailable authority deny subsequent delivery/replay')
    print('Demo complete. All four processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo', 'launch', 'bootstrap', 'serve', 'request', 'dashboard', 'seed'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--service', choices=list(SERVICES))
    parser.add_argument('--port', type=int)
    parser.add_argument('--operation')
    parser.add_argument('--payload', default='{}')
    parser.add_argument('--refs', default='[]')
    parser.add_argument('--identity', choices=['owner', 'reader', 'denied'], default='owner')
    parser.add_argument('--grant', default='grant.owner-bootstrap')
    parser.add_argument('--key')
    args = parser.parse_args()
    if args.action in ('demo', 'launch'):
        if args.directory:
            parser.error('demo/launch use temporary state; omit --directory')
        with tempfile.TemporaryDirectory(prefix='farmy-uc006-') as temp:
            directory = bootstrap(temp)
            if args.action == 'demo':
                demo(directory)
            else:
                with core.Processes(directory, SERVICES):
                    seed(directory)
                    print('Synthetic disclosure seeded automatically; this dashboard remains read-only.', flush=True)
                    monitor.ui(directory, args.port)
    elif args.directory is None:
        parser.error('--directory is required')
    elif args.action == 'bootstrap':
        print(bootstrap(args.directory))
    elif args.action == 'serve':
        if not args.service: parser.error('--service is required')
        os.execve(sys.executable, core.command(args.directory, args.service, SERVICES), core.environment())
    elif args.action == 'dashboard':
        monitor.ui(args.directory, args.port)
    elif args.action == 'seed':
        print(json.dumps(seed(args.directory)[-1], indent=2))
    else:
        if not args.operation: parser.error('--operation is required')
        print(json.dumps(call(args.directory, args.operation, json.loads(args.payload), args.identity,
            refs=json.loads(args.refs), grant=args.grant, key=args.key), indent=2))


if __name__ == '__main__': main()
