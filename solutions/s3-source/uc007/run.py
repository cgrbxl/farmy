"""UC-007 S3 source: local fixture checks or explicitly configured provider reads."""
import argparse
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

exports = load('uc006_run', 'solutions/disclosure/uc006/run.py')
documents = load('uc002_run', 'solutions/document-path/uc002/run.py')
s3 = load('s3_connector', 'modules/connectors/s3/service.py')
fixture = load('s3_fixture', 'solutions/s3-source/uc007/fixture.py')
core = exports.core
SERVICES = dict(documents.SERVICES, **exports.SERVICES)
SERVICES['connector.local'] = 'modules/connectors/s3/service.py'
INVENTORY = dict(exports.INVENTORY, **{
    'processing.local': {'family': 'processing', 'name': 'Text Processing'},
    'knowledge.local': {'family': 'knowledge', 'name': 'Evidence Knowledge'},
    'workflow.local': {'family': 'workflow', 'name': 'Workflow'}})
INVENTORY['connector.local'] = {'family': 'connectors', 'name': 'S3 Source'}


def bootstrap(directory, settings):
    s3.validate_settings(settings)
    # All provider secrets remain outside generated module configuration.
    directory = core.bootstrap(directory, dict(SERVICES, **{'monitor.local': 'solutions/operations/uc005/server.py'}))
    import secrets
    for identity in [*SERVICES, 'monitor.local', 'owner', 'reader', 'denied', 'unknown']:
        path = directory / (identity + '.json')
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc007-local', bootstrapProfile='uc007.bootstrap', compositionRevision=1)
        if identity in INVENTORY:
            config.update(monitorSubjects=['monitor.local'], implementationVersion='0.1.1')
        if identity == 'wallet.local':
            config.update(readSubjects=['owner','reader','denied','processing.local','exchange.local'],
                          permissionScopes=documents.SCOPES + exports.SCOPES)
        if identity == 'connector.local':
            config.update(s3=settings, implementationId='farmy.reference.s3', implementationVersion='0.1.0')
            del config['sourceRoot']
        if identity == 'exchange.local':
            config.update(implementationId='farmy.reference.controlled-exchange',
                          implementationVersion='0.1.0', recipients=['recipient.local'])
        if identity == 'recipient.local': config['implementationId'] = 'farmy.fixture.recipient'
        if identity == 'monitor.local':
            inventory = dict(INVENTORY)
            if settings.get('fixture'):
                inventory['connector.local'] = {'family': 'connectors', 'name': 'S3 Source (fixture)'}
            config.update(inventory=inventory, browserToken=secrets.token_urlsafe(32))
            config = {k: config[k] for k in ('identity','walletId','ca','cert','key','endpoints','inventory','browserToken')}
            config['endpoints'] = {k: dict(v, timeoutSeconds=3) for k,v in config['endpoints'].items() if k in INVENTORY}
        path.write_text(json.dumps(config, indent=2))
    return directory


def exercise(directory, path):
    resource = core.call(directory, 'resource.register', {'path': path})
    grants, query_grant = documents.permissions(directory, resource)
    documents.call(directory, 'job.run', grants, refs=core.refs(resource))
    evidence = documents.query(directory, resource, query_grant)
    assert evidence['value'] == 'wheat'
    read = core.grant(directory, resource, 'exchange.local')
    preview = exports.call(directory, 'disclosure.prepare', {'recipientId':'recipient.local',
        'purpose':'synthetic.review', 'sourceReadGrant':read['grantId']}, refs=core.refs(resource))
    approve = exports.permission(directory, resource, 'approve')
    delivery = exports.permission(directory, resource, 'deliver')
    exports.approve(directory, resource, preview, approve)
    receipt = exports.deliver(directory, resource, preview, delivery)
    received = exports.call(directory, 'receipt.inspect', {'disclosureId':receipt['disclosureId']})
    assert received['contentBase64'] == preview['contentBase64']
    core.expect_fault('denied', lambda: documents.query(directory, resource, query_grant, 'denied'))
    return resource, query_grant, preview, delivery, receipt


def demo(settings, path):
    with tempfile.TemporaryDirectory(prefix='farmy-uc007-') as temp:
        directory = bootstrap(temp, settings)
        with core.Processes(directory, SERVICES) as processes:
            resource, permission, preview, delivery, receipt = exercise(directory, path)
            print('PASS S3 acquisition feeds unchanged extraction, evidence and approved disclosure APIs')
            for name in ('connector.local','knowledge.local','exchange.local'):
                processes.stop(name)
                processes.start(name)
            assert documents.query(directory, resource, permission)['value'] == 'wheat'
            assert exports.deliver(directory, resource, preview, delivery) == receipt
            core.call(directory, 'access.revoke', {'grantId':delivery['grantId']}, revision=1)
            core.expect_fault('denied', lambda: exports.deliver(directory, resource, preview, delivery))
            print('PASS restart retains exact source and receipt; revoked export is denied')
        print('All seven Farmy/recipient processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo','launch','bootstrap','serve','dashboard','exercise'])
    parser.add_argument('--fixture', action='store_true', help='Explicit local HTTP double; not provider validation')
    parser.add_argument('--s3-config', type=Path, help='Non-secret settings JSON with explicit credential references')
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--service', choices=list(SERVICES))
    parser.add_argument('--key', default='report.txt', help='Relative synthetic object key below configured prefix')
    parser.add_argument('--port', type=int)
    args = parser.parse_args()
    if args.action in ('demo','launch'):
        if args.directory: parser.error('demo/launch own temporary local state')
        if bool(args.fixture) == bool(args.s3_config): parser.error('Choose --fixture or --s3-config')
        def perform(settings):
            if args.action == 'demo':
                demo(settings, args.key)
            else:
                with tempfile.TemporaryDirectory(prefix='farmy-uc007-') as temp:
                    directory = bootstrap(temp, settings)
                    with core.Processes(directory, SERVICES):
                        exercise(directory, args.key)
                        print('S3 source uses '+('a local HTTP double; provider validation remains pending.' if args.fixture else 'the explicitly configured provider.'), flush=True)
                        exports.monitor.ui(directory, args.port)
        if args.fixture:
            with fixture.Fixture().running() as source:
                perform(source.settings())
            print('Local S3-double checks complete. No Scaleway compatibility claim.')
        else:
            settings = json.loads(args.s3_config.read_text())
            if settings.get('fixture'): parser.error('Provider config cannot enable fixture mode')
            perform(settings)
    elif not args.directory: parser.error('--directory is required')
    elif args.action == 'bootstrap':
        if not args.s3_config: parser.error('--s3-config is required')
        print(bootstrap(args.directory, json.loads(args.s3_config.read_text())))
    elif args.action == 'serve':
        if not args.service: parser.error('--service is required')
        os.execve(sys.executable, core.command(args.directory, args.service, SERVICES), core.environment())
    elif args.action == 'dashboard': exports.monitor.ui(args.directory, args.port)
    else:
        print(json.dumps(exercise(args.directory, args.key)[-1], indent=2))


if __name__ == '__main__': main()
