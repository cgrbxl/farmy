"""Persistent composition lifecycle using real subprocesses and HTTP boundaries."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('local_runtime', ROOT / 'runtime/local/farmy.py')
runtime = importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='farmy-local-');self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name);self.home = self.root/'workspace'
        self.source = self.root/'source';self.source.mkdir();(self.source/'note.txt').write_text('An exact generic record.\n')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));self.port=sock.getsockname()[1]
        runtime.initialise(self.home,self.source,self.port)
        self.addCleanup(self.cleanup_runtime)

    def cleanup_runtime(self):
        try: runtime.stop(self.home)
        except (OSError,ValueError,RuntimeError): pass

    def request(self,action=None,payload=None,token=None):
        running=json.loads((self.home/'running.json').read_text())
        port=running['port']
        consumer=json.loads(next((self.home/'transport').glob('*/reader.json')).read_text())
        if token==consumer['browserToken']:port=consumer['browserPort']
        origin=f'http://127.0.0.1:{port}'
        data=None if action is None else json.dumps(dict(action=action,payload=payload or {})).encode()
        req=urllib.request.Request(origin+('/api/state' if action is None else '/api/action'),data=data,
            headers={'Authorization':'Bearer '+(token or running['token']),'Origin':origin,'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)

    def admit(self):
        state=self.request();entry=state['entries'][0]
        preview=self.request('preview',dict(entry=entry))
        return self.request('admit',dict(entry=entry,sha256=preview['sha256'],policy='restricted',key='admit'))['id']

    def test_restart_preserves_copy_revocation_and_rotates_credentials(self):
        runtime.start(self.home);item=self.admit();self.request('grant',dict(id=item,key='grant'))
        consumer=self.request()['consumerToken'];self.assertIn('exact',self.request('read',dict(id=item),consumer)['text'])
        self.request('revoke',dict(id=item,key='revoke'))
        old=json.loads((self.home/'running.json').read_text())['token']
        old_ca=next((self.home/'transport').glob('*/certs/ca.pem')).read_bytes()
        runtime.stop(self.home);(self.source/'note.txt').unlink();runtime.start(self.home)
        state=self.request();self.assertEqual(state['items'][0]['id'],item);self.assertEqual(state['items'][0]['sharing'],'Revoked')
        self.assertIn('exact',self.request('read',dict(id=item))['text'])
        self.assertNotEqual(next((self.home/'transport').glob('*/certs/ca.pem')).read_bytes(),old_ca)
        with self.assertRaises(urllib.error.HTTPError) as err:self.request(token=old)
        self.assertEqual(err.exception.code,401);err.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as err:self.request('read',dict(id=item),state['consumerToken'])
        self.assertEqual(err.exception.code,403);err.exception.close()

    def test_policy_change_grant_revoke_and_private_cannot_resurrect_grant(self):
        runtime.start(self.home)
        entry=self.request()['entries'][0];preview=self.request('preview',dict(entry=entry))
        item=self.request('admit',dict(entry=entry,sha256=preview['sha256'],policy='private',key='private'))['id']
        with self.assertRaises(urllib.error.HTTPError) as err:self.request('grant',dict(id=item,key='badgrant'))
        self.assertEqual(err.exception.code,403);err.exception.close()
        self.request('policy',dict(id=item,policy='restricted',key='allow'))
        self.assertEqual(self.request()['items'][0]['sharing'],'Not granted')
        self.request('grant',dict(id=item,key='goodgrant'))
        consumer=self.request()['consumerToken']
        self.assertIn('exact',self.request('read',dict(id=item),consumer)['text'])
        self.request('policy',dict(id=item,policy='private',key='private-again'))
        self.request('policy',dict(id=item,policy='restricted',key='allow-again'))
        with self.assertRaises(urllib.error.HTTPError) as err:self.request('read',dict(id=item),consumer)
        self.assertEqual(err.exception.code,403);err.exception.close()
        self.request('grant',dict(id=item,key='newgrant'))
        self.assertIn('exact',self.request('read',dict(id=item),consumer)['text'])
        self.request('revoke',dict(id=item,key='revoke-new'))
        with self.assertRaises(urllib.error.HTTPError) as err:self.request('read',dict(id=item),consumer)
        self.assertEqual(err.exception.code,403);err.exception.close()

    def test_persistent_keys_and_separate_consumer_receipts(self):
        runtime.start(self.home);item=self.admit();self.request('grant',dict(id=item,key='grant'))
        before=self.request()['identities'];consumer=self.request()['consumerToken']
        state=self.request(token=consumer)
        self.assertEqual(state['identity']['fingerprint'],before['reader']['fingerprint'])
        self.assertNotEqual(before['owner']['fingerprint'],before['reader']['fingerprint'])
        self.assertNotIn('consumerToken',state);self.assertNotIn('entries',state)
        self.assertTrue((self.home/'state-reader/state.sqlite').exists())
        generation=next((self.home/'transport').iterdir())
        descriptor=runtime.core.exchange(runtime.core.config(generation,'owner'),'reader',path='/farmy/v0/descriptor')
        self.assertEqual(descriptor['module']['family'],'exchange')
        runtime.stop(self.home);runtime.start(self.home)
        self.assertEqual(self.request()['identities'],before)
        self.assertIn('exact',self.request('read',dict(id=item),self.request()['consumerToken'])['text'])

    def test_expired_grant_wrong_identity_and_stale_policy_are_denied(self):
        runtime.start(self.home);item=self.admit()
        generation=next((self.home/'transport').iterdir());core=runtime.core
        metadata=self.request()['items'][0];resource=metadata['resource'];refs=core.refs(resource)
        owner=core.config(generation,'owner')
        permission=core.exchange(owner,'wallet.local',core.request(owner,'wallet.local','grant.issue',dict(resourceId=item,versionId=resource['versionId'],subjectId='reader',expiresAt=core.utc(1),purpose='uc001.read'),refs=refs))
        with self.assertRaises(runtime.Fault) as err:core.read(generation,resource,permission,'denied')
        self.assertEqual(err.exception.code,'denied')
        time.sleep(1.1)
        with self.assertRaises(runtime.Fault) as err:core.read(generation,resource,permission,'reader')
        self.assertEqual(err.exception.code,'denied')
        payload=dict(resourceId=item,classification='private',allowedReaders=['owner'])
        query=core.request(owner,'wallet.local','item.policy',payload,refs=refs,revision=resource['revision'],key='key.policy')
        first=core.exchange(owner,'wallet.local',query)
        self.assertEqual(core.exchange(owner,'wallet.local',query),first)
        query['idempotencyKey']='key.stale'
        with self.assertRaises(runtime.Fault) as err:core.exchange(owner,'wallet.local',query)
        self.assertEqual(err.exception.code,'conflict')
        bad=core.config(generation,'reader')
        with self.assertRaises(runtime.Fault) as err:core.exchange(bad,'wallet.local',core.request(bad,'wallet.local','item.policy',payload,refs=refs,revision=first['resource']['revision']))
        self.assertEqual(err.exception.code,'denied')

    def test_consumer_offer_replay_cannot_replace_newer_receipt(self):
        runtime.start(self.home);item=self.admit();generation=next((self.home/'transport').iterdir())
        core=runtime.core;owner=core.config(generation,'owner');resource=self.request()['items'][0]['resource']
        def issue(seconds):
            return core.exchange(owner,'wallet.local',core.request(owner,'wallet.local','grant.issue',dict(resourceId=item,versionId=resource['versionId'],subjectId='reader',expiresAt=core.utc(seconds),purpose='uc001.read'),refs=core.refs(resource)))
        first=issue(1);second=issue(60)
        query=core.request(owner,'reader','consumer.offer',dict(resource=resource,grantId=first['grantId']),refs=core.refs(resource),key='key.first')
        core.exchange(owner,'reader',query)
        newer=core.request(owner,'reader','consumer.offer',dict(resource=resource,grantId=second['grantId']),refs=core.refs(resource),key='key.second')
        core.exchange(owner,'reader',newer);core.exchange(owner,'reader',query)
        time.sleep(1.1)
        self.assertIn('exact',self.request('read',dict(id=item),self.request()['consumerToken'])['text'])
        query['payload']['grantId']=second['grantId']
        with self.assertRaises(runtime.Fault) as err:core.exchange(owner,'reader',query)
        self.assertEqual(err.exception.code,'conflict')
        denied=core.config(generation,'denied')
        with self.assertRaises(runtime.Fault) as err:core.exchange(denied,'reader',core.request(denied,'reader','consumer.offer',newer['payload'],refs=core.refs(resource)))
        self.assertEqual(err.exception.code,'denied')

    def test_policy_cannot_exceed_source_reader_ceiling(self):
        generation=runtime.transport(self.home)
        path=generation/'connector.local.json';config=json.loads(path.read_text())
        config['sourceReaderCeiling']=['owner'];runtime.save(path,config)
        with runtime.Processes(generation,self.home):
            client=runtime.Workbench(generation,self.home,threading.Event(),('test-owner','test-consumer'))
            entry=client.state('owner')['entries'][0];preview=client.preview(entry)
            item=client.action('owner','admit',dict(entry=entry,sha256=preview['sha256'],policy='private',key='private'))['id']
            with self.assertRaises(runtime.Fault) as err:client.action('owner','policy',dict(id=item,policy='restricted',key='widen'))
            self.assertEqual(err.exception.code,'denied')
            self.assertEqual(client.state('owner')['items'][0]['classification'],'private')

    def test_key_substitution_fails_closed(self):
        runtime.start(self.home);runtime.stop(self.home)
        key=self.home/'identities/reader/private.pem'
        key.write_bytes((self.home/'identities/owner/private.pem').read_bytes())
        with self.assertRaises(ValueError):runtime.identities(self.home)

    def test_stopped_backup_restore_preserves_identity(self):
        runtime.start(self.home);item=self.admit()
        with self.assertRaises(ValueError):runtime.backup(self.home,self.root/'live-backup')
        runtime.stop(self.home);runtime.backup(self.home,self.root/'backup')
        before=runtime.identities(self.home)
        restored=self.root/'restored';runtime.restore(restored,self.root/'backup')
        self.home=restored;runtime.start(self.home)
        self.assertEqual(runtime.identities(self.home),before)
        self.assertEqual(self.request()['items'][0]['id'],item)
        self.assertIn('exact',self.request('read',dict(id=item))['text'])

    def test_duplicate_start_and_consumer_stop_are_rejected(self):
        runtime.start(self.home)
        with self.assertRaises(ValueError):runtime.start(self.home)
        with self.assertRaises(urllib.error.HTTPError) as err:self.request('runtime.stop',{},self.request()['consumerToken'])
        self.assertEqual(err.exception.code,403);err.exception.close()
        self.assertTrue(runtime.control(self.home)[1]['running'])

    def test_initialisation_refuses_overwrite_and_source_overlap(self):
        with self.assertRaises(ValueError):runtime.initialise(self.home,self.source,self.port)
        with self.assertRaises(ValueError):runtime.initialise(self.source/'state',self.source,self.port)
        self.assertEqual((self.source/'note.txt').read_text(),'An exact generic record.\n')

    def test_abrupt_supervisor_exit_stops_modules_and_can_restart(self):
        try: runtime.start(self.home)
        except RuntimeError as exc: self.fail(str(exc)+'\n'+(self.home/'runtime.log').read_text())
        item=self.admit()
        generation=next((self.home/'transport').iterdir())
        config=runtime.core.config(generation)
        pid=json.loads((self.home/'running.json').read_text())['pid'];os.kill(pid,signal.SIGKILL)
        deadline=time.monotonic()+8
        while True:
            try:runtime.core.exchange(config,'wallet.local',path='/farmy/v0/health/live')
            except runtime.Fault:break
            if time.monotonic()>deadline:self.fail('Orphaned module remained available')
            time.sleep(.1)
        runtime.start(self.home);self.assertEqual(self.request()['items'][0]['id'],item)

    def test_failed_start_preserves_state(self):
        runtime.start(self.home);item=self.admit();runtime.stop(self.home)
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            listener.bind(('127.0.0.1',self.port));listener.listen()
            with self.assertRaises(RuntimeError):runtime.start(self.home)
        runtime.start(self.home);self.assertEqual(self.request()['items'][0]['id'],item)

    def test_unknown_schema_and_unsafe_backup_are_rejected(self):
        config=json.loads((self.home/'installation.json').read_text());config['schema']=999
        runtime.save(self.home/'installation.json',config)
        with self.assertRaises(ValueError):runtime.start(self.home)
        config['schema']=1;runtime.save(self.home/'installation.json',config)
        runtime.backup(self.home,self.root/'backup')
        (self.root/'backup'/'unexpected-link').symlink_to(self.source)
        with self.assertRaises(ValueError):runtime.restore(self.root/'bad-restore',self.root/'backup')


if __name__ == '__main__':unittest.main()
