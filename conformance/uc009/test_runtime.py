"""Public-API acceptance for the source / managed-item boundary."""
import base64
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from pathlib import Path
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uc009', ROOT / 'solutions/managed-items/uc009/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from farmy_transport.http import Fault


class Runtime(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='farmy-uc009-test-')
        self.addCleanup(temp.cleanup)
        self.directory = run.bootstrap(temp.name)
        self.processes = run.core.Processes(self.directory, run.SERVICES)
        self.addCleanup(self.processes.__exit__,None,None,None)
        self.processes.__enter__()
        self.source,self.owner,self.reader = run.setup(self.directory)
        self.scope = run.scope(self.source)

    def call(self, op, payload=None, **kw):
        return run.call(self.directory,op,payload,**kw)

    def denied(self, code, action):
        with self.assertRaises(Fault) as caught: action()
        self.assertEqual(caught.exception.code,code)

    def payload(self, **changes):
        return run.admission(self.directory,self.source,self.owner,**changes)

    def item(self, **changes):
        return self.call('item.admit',self.payload(**changes))

    def listing(self, grant=None, identity='reader'):
        return self.call('folder.list',self.scope,identity=identity,grant=(grant or self.reader)['grantId'])

    def test_source_is_collective_and_admission_is_explicit(self):
        self.assertEqual(self.listing()['entries'],['inspection.eml','supplies.eml'])
        for entry,content in [('inspection.eml',run.MAIL),('supplies.eml',run.OTHER)]:
            result = self.call('folder.read',dict(self.scope,entry=entry),identity='reader',grant=self.reader['grantId'])
            self.assertEqual(base64.b64decode(result['contentBase64']),content)
        state = run.monitor.bridge.snapshot(run.core.config(self.directory,'monitor.local'))
        counts = {n['instanceId']:{c['label']:c['value'] for c in n['counts']} for n in state['nodes']}
        self.assertEqual(counts['wallet.local']['Managed items'],0)
        item = self.item()
        self.assertEqual(item['sourceId'],self.source['sourceId'])
        self.assertEqual(item['mode'],'managed-copy')
        self.assertNotIn('sourceGrant',item)
        self.assertEqual(self.call('item.inspect',{'resourceId':item['resource']['resourceId']}),item)

    def test_grants_do_not_cross_boundaries(self):
        resource = self.item()['resource']
        permission = run.core.grant(self.directory,resource)
        self.assertEqual(run.core.read(self.directory,resource,permission),run.MAIL)
        self.denied('denied',lambda: run.core.read(self.directory,resource,self.reader))
        self.denied('denied',lambda: self.listing(permission))
        self.denied('denied',lambda: run.core.read(self.directory,resource,permission,'denied'))

    def test_reader_ceiling_and_private_policy(self):
        self.denied('denied',lambda:self.item(allowedReaders=['denied']))
        self.denied('denied',lambda:self.item(classification='private'))
        resource = self.item(classification='private',allowedReaders=['owner'])['resource']
        self.denied('denied',lambda:run.core.grant(self.directory,resource,'reader'))
        owner = run.core.grant(self.directory,resource,'owner')
        self.assertEqual(run.core.read(self.directory,resource,owner,'owner'),run.MAIL)
        restricted = self.item()['resource']
        self.denied('denied',lambda:run.core.grant(self.directory,restricted,'denied'))

    def test_revocations_are_independent(self):
        resource = self.item()['resource']; permission = run.core.grant(self.directory,resource)
        self.call('source.revoke',{'grantId':self.reader['grantId']},revision=1)
        self.denied('denied',self.listing)
        self.assertEqual(run.core.read(self.directory,resource,permission),run.MAIL)
        fresh = run.source_grant(self.directory,self.source)
        self.call('grant.revoke',{'grantId':permission['grantId']},revision=1)
        self.denied('denied',lambda:run.core.read(self.directory,resource,permission))
        self.assertEqual(len(self.listing(fresh)['entries']),2)
        short=self.call('source.grant',dict(self.scope,consumerId='reader',expiresAt=run.core.utc(1)))
        time.sleep(1.1)
        self.denied('denied',lambda:self.listing(short))

    def test_changed_or_deleted_source_preserves_copy(self):
        payload = self.payload(); resource = self.call('item.admit',payload)['resource']
        permission = run.core.grant(self.directory,resource)
        path = self.directory / 'source/inspection.eml'
        path.write_bytes(b'new bytes')
        self.denied('conflict',lambda:self.call('item.admit',payload))
        path.unlink()
        self.assertEqual(run.core.read(self.directory,resource,permission),run.MAIL)

    def test_idempotency_parallel_and_conflicting_payload(self):
        payload = self.payload()
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda _: self.call('item.admit',payload,key='key.same'),range(3)))
        self.assertTrue(all(r==results[0] for r in results))
        self.denied('conflict',lambda:self.call('item.admit',dict(payload,title='different'),key='key.same'))

    def test_receipt_replay_does_not_read_source_after_revocation(self):
        payload = self.payload(); receipt = self.call('item.admit',payload,key='key.receipt')
        self.call('source.revoke',{'grantId':self.owner['grantId']},revision=1)
        self.assertEqual(self.call('item.admit',payload,key='key.receipt'),receipt)
        self.denied('denied',lambda:self.call('item.admit',payload))

    def test_owner_only_admission_metadata_and_capture(self):
        payload = self.payload(); item = self.call('item.admit',payload)
        self.denied('denied',lambda:self.call('item.admit',payload,identity='reader'))
        self.denied('denied',lambda:self.call('item.inspect',{'resourceId':item['resource']['resourceId']},identity='reader'))
        self.denied('denied',lambda:self.call('folder.capture',{k:payload[k] for k in ('sourceId','ownerId','entry','sha256')},grant=self.owner['grantId']))
        self.denied('denied',lambda:self.listing(identity='denied'))
        self.denied('unauthenticated',lambda:self.listing(identity='unknown'))

    def test_path_escape_symlink_and_scope_confusion(self):
        (self.directory / 'source/link.eml').symlink_to(self.directory / 'owner.json')
        self.assertNotIn('link.eml',self.listing()['entries'])
        self.denied('denied',lambda:self.call('folder.read',dict(self.scope,entry='link.eml'),grant=self.owner['grantId']))
        self.denied('invalid_request',lambda:self.call('folder.read',dict(self.scope,entry='../owner.json'),grant=self.owner['grantId']))
        other = self.call('source.register',{'connectorId':'connector.local'})
        self.denied('conflict',lambda:self.call('folder.attach',run.scope(other)))
        other_grant = run.source_grant(self.directory,other)
        self.denied('denied',lambda:self.call('folder.list',run.scope(other),identity='reader',grant=other_grant['grantId']))

    def test_restarts_and_authority_outage(self):
        item=self.item(); resource=item['resource']; permission=run.core.grant(self.directory,resource)
        for service in run.SERVICES:
            self.processes.stop(service); self.processes.start(service)
        self.assertEqual(self.call('item.inspect',{'resourceId':resource['resourceId']}),item)
        self.assertEqual(run.core.read(self.directory,resource,permission),run.MAIL)
        self.processes.stop('wallet.local')
        self.denied('unavailable',self.listing)
        self.denied('unavailable',lambda:run.core.read(self.directory,resource,permission))

    def test_managed_items_cannot_use_legacy_mutation_or_export(self):
        resource=self.item()['resource']
        for op in ('resource.move','resource.update'):
            self.denied('unsupported',lambda:self.call(op,dict(resourceId=resource['resourceId'], **({'path':'supplies.eml'} if op=='resource.move' else {})),refs=run.core.refs(resource),revision=1))
        self.denied('unsupported',lambda:self.call('access.issue',dict(resourceId=resource['resourceId'],versionId=resource['versionId'],
            subjectId='reader',audience='connector.local',operation='read.version',purpose='uc001.read',expiresAt=run.core.utc(600)),refs=run.core.refs(resource)))

    def test_descriptors_and_monitor_disclose_counts_only(self):
        client=run.core.config(self.directory,'monitor.local')
        state=run.monitor.bridge.snapshot(client)
        self.assertTrue(all(n['status']=='available' for n in state['nodes']))
        self.assertNotIn('inspection.eml',str(state))
        from bindings import admit, resolve
        owner=run.core.config(self.directory)
        binding=resolve(owner['binding'],owner['walletId'],'farmy.folder-source','folder.capture','0.9-draft')
        self.assertEqual(admit(owner,binding),'connector.local')
        self.denied('denied',lambda:run.core.exchange(run.core.config(self.directory,'reader'),'wallet.local',path='/farmy/v0/monitor/summary'))


if __name__ == '__main__': unittest.main()
