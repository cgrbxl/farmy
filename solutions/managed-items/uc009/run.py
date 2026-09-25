"""UC-009: a connected folder and individually governed managed copies."""
import argparse
import base64
import importlib.util
import json
from pathlib import Path
import secrets
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('monitor_run', ROOT / 'solutions/operations/uc005/run.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
core = monitor.core
SERVICES = {'wallet.local': 'modules/wallet/reference/service.py',
            'connector.local': 'modules/connectors/managed_folder/service.py'}
MAIL = b'From: synthetic@example.invalid\nSubject: Farm inspection\n\nInspection completed.\n'
OTHER = b'From: synthetic@example.invalid\nSubject: Supplies\n\nDelivery on Monday.\n'


def bootstrap(directory):
    directory = core.bootstrap(directory, dict(SERVICES, **{'monitor.local': 'solutions/operations/uc005/server.py'}))
    (directory / 'source/record.txt').unlink()
    (directory / 'source/inspection.eml').write_bytes(MAIL)
    (directory / 'source/supplies.eml').write_bytes(OTHER)
    binding = json.loads((directory / 'binding.json').read_text())
    binding.update(capabilityId='farmy.folder-source', contractVersion='0.9-draft',
                   operations=['folder.capture'], requiredFeatures=[])
    (directory / 'binding.json').write_text(json.dumps(binding, indent=2))
    for path in directory.glob('*.json'):
        if path.name == 'binding.json': continue
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc009-local', bootstrapProfile='uc009.bootstrap')
        identity = config['identity']
        if identity in SERVICES: config['monitorSubjects'] = ['monitor.local']
        if identity == 'wallet.local':
            config.update(managedItems=True, sourceConnectors=['connector.local'], readSubjects=['owner','reader','denied'])
        if identity == 'connector.local':
            config.update(implementationId='farmy.reference.managed-folder', implementationVersion='0.1.0',
                          sourceReaderCeiling=['owner', 'reader'])
        if identity == 'monitor.local':
            config.update(inventory={name: {'family': family, 'name': label} for name, family, label in [
                ('wallet.local','wallet','Wallet · managed items'),
                ('connector.local','connectors','Connected folder · managed copies')]}, browserToken=secrets.token_urlsafe(32))
            config = {k: config[k] for k in ('identity','walletId','ca','cert','key','endpoints','inventory','browserToken')}
            config['endpoints'] = {k: dict(v, timeoutSeconds=3) for k,v in config['endpoints'].items() if k in SERVICES}
        path.write_text(json.dumps(config, indent=2))
    return directory


def call(directory, operation, payload=None, identity='owner', **kwargs):
    client = core.config(directory, identity)
    target = 'connector.local' if operation.startswith('folder.') or operation == 'read.version' else 'wallet.local'
    return core.exchange(client, target, core.request(client, target, operation, payload or {}, **kwargs))


def scope(source):
    return {k: source[k] for k in ('sourceId','ownerId')}


def source_grant(directory, source, consumer='reader'):
    return call(directory, 'source.grant', dict(scope(source), consumerId=consumer, expiresAt=core.utc(600)))


def setup(directory):
    source = call(directory, 'source.register', {'connectorId': 'connector.local'})
    call(directory, 'folder.attach', scope(source))
    return source, source_grant(directory, source, 'owner'), source_grant(directory, source)


def admission(directory, source, permission, **changes):
    data = call(directory, 'folder.read', dict(scope(source), entry='inspection.eml'), grant=permission['grantId'])
    payload = dict(scope(source), entry='inspection.eml', sha256=data['sha256'], sourceGrant=permission['grantId'],
                   title='Synthetic inspection email', classification='restricted', allowedReaders=['owner','reader'])
    payload.update(changes)
    return payload


def seed(directory):
    source, owner, reader = setup(directory)
    item = call(directory, 'item.admit', admission(directory, source, owner))
    return source, owner, reader, item


def demo(directory):
    with core.Processes(directory, SERVICES) as processes:
        source, owner, reader = setup(directory)
        assert call(directory, 'folder.list', scope(source), identity='reader', grant=reader['grantId'])['entries'] == ['inspection.eml','supplies.eml']
        for entry, content in [('inspection.eml',MAIL),('supplies.eml',OTHER)]:
            data = call(directory,'folder.read',dict(scope(source),entry=entry),identity='reader',grant=reader['grantId'])
            assert base64.b64decode(data['contentBase64']) == content
        print('PASS one source grant covers both emails outside the Wallet')
        payload = admission(directory,source,owner)
        item = call(directory,'item.admit',payload,key='key.admission')
        assert call(directory,'item.admit',payload,key='key.admission') == item
        resource = item['resource']
        permission = core.grant(directory,resource)
        assert core.read(directory,resource,permission) == MAIL
        core.expect_fault('denied',lambda: core.read(directory,resource,reader))
        core.expect_fault('denied',lambda: call(directory,'folder.list',scope(source),identity='reader',grant=permission['grantId']))
        core.expect_fault('denied',lambda: core.grant(directory,resource,'denied'))
        print('PASS selected copy has provenance and narrower readers; source and item grants cannot substitute')
        (directory / 'source/inspection.eml').write_bytes(b'Changed source email\n')
        core.expect_fault('conflict',lambda: call(directory,'item.admit',payload))
        (directory / 'source/inspection.eml').unlink()
        assert core.read(directory,resource,permission) == MAIL
        call(directory,'source.revoke',{'grantId':reader['grantId']},revision=1)
        core.expect_fault('denied',lambda: call(directory,'folder.list',scope(source),identity='reader',grant=reader['grantId']))
        assert core.read(directory,resource,permission) == MAIL
        print('PASS copy survives original changes; source revocation does not recall an authorised retained copy')
        processes.stop('wallet.local'); processes.start('wallet.local')
        processes.stop('connector.local'); processes.start('connector.local')
        assert call(directory,'item.inspect',{'resourceId':resource['resourceId']}) == item
        assert core.read(directory,resource,permission) == MAIL
        state = monitor.bridge.snapshot(core.config(directory,'monitor.local'))
        assert all(n['status']=='available' for n in state['nodes'])
        call(directory,'grant.revoke',{'grantId':permission['grantId']},revision=1)
        core.expect_fault('denied',lambda: core.read(directory,resource,permission))
        fresh = core.grant(directory,resource)
        processes.stop('wallet.local')
        core.expect_fault('unavailable',lambda: core.read(directory,resource,fresh))
        core.expect_fault('unavailable',lambda: call(directory,'folder.list',scope(source),grant=owner['grantId']))
        print('PASS restart preserves metadata; item revocation and authority outage deny reads')
    print('Demo complete. Both Farmy processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo','launch'])
    parser.add_argument('--port', type=int)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='farmy-uc009-') as temp:
        directory = bootstrap(temp)
        if args.action == 'demo': demo(directory)
        else:
            with core.Processes(directory,SERVICES):
                seed(directory)
                monitor.ui(directory,args.port)


if __name__ == '__main__': main()
