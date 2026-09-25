"""Real HTTP browser bridge and mTLS service acceptance."""
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('uc010_server',ROOT/'solutions/interactive/uc010/server.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)


class Runtime(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='farmy-ui-test-');self.addCleanup(temp.cleanup)
        self.directory=bridge.managed.bootstrap(temp.name)
        self.processes=bridge.managed.core.Processes(self.directory,bridge.managed.SERVICES)
        self.addCleanup(self.processes.__exit__,None,None,None);self.processes.__enter__()
        self.workbench=bridge.Workbench(self.directory)
        self.httpd=bridge.Server(self.workbench);self.addCleanup(self.httpd.server_close)
        threading.Thread(target=self.httpd.serve_forever,daemon=True).start();self.addCleanup(self.httpd.shutdown)
        self.origin=f'http://127.0.0.1:{self.httpd.server_port}'

    def http(self,path='/api/state',role='owner',body=None,headers=None,raw=None):
        client=http.client.HTTPConnection('127.0.0.1',self.httpd.server_port,timeout=10)
        h={'Origin':self.origin}
        if role:h['Authorization']='Bearer '+self.workbench.session[role]
        if body is not None or raw is not None:h['Content-Type']='application/json'
        h.update(headers or {})
        client.request('POST' if body is not None or raw is not None else 'GET',path,
            body=raw if raw is not None else json.dumps(body) if body is not None else None,headers=h)
        response=client.getresponse();data=response.read();result=(response.status,data,dict(response.getheaders()));client.close();return result

    def action(self,action,payload,role='owner',expected=200):
        code,data,_=self.http('/api/action',role,{'action':action,'payload':payload})
        self.assertEqual(code,expected,data)
        return json.loads(data)

    def admission(self,key='admit',policy='restricted'):
        preview=self.action('preview',{'entry':'inspection.eml'})
        payload=dict(entry=preview['entry'],sha256=preview['sha256'],policy=policy,key=key)
        return payload

    def admit(self,**kwargs):return self.action('admit',self.admission(**kwargs))['id']
    def grant(self,resource,key='grant'):return self.action('grant',{'id':resource,'key':key})
    def revoke(self,resource,key='revoke'):return self.action('revoke',{'id':resource,'key':key})
    def read(self,resource,expected=200):return self.action('read',{'id':resource},'consumer',expected)

    def test_full_visible_journey(self):
        state=json.loads(self.http()[1]);self.assertEqual(len(state['entries']),2);self.assertEqual(state['items'],[])
        resource=self.admit();self.read(resource,403);self.grant(resource)
        self.assertEqual(self.read(resource)['text'],bridge.managed.MAIL.decode())
        self.revoke(resource);self.read(resource,403)
        state=json.loads(self.http()[1]);self.assertEqual(state['items'][0]['sharing'],'Revoked')
        self.assertEqual(state['items'][0]['resource']['resourceId'],resource)

    def test_consumer_has_no_owner_actions_or_source_metadata(self):
        resource=self.admit()
        for action,payload in [('preview',{'entry':'inspection.eml'}),('admit',self.admission()),('grant',{'id':resource,'key':'g'}),('revoke',{'id':resource,'key':'r'})]:
            self.action(action,payload,'consumer',403)
        state=self.http(role='consumer')[1]
        for secret in [b'inspection.eml',b'ownerId',b'sourceGrant',self.workbench.session['owner'].encode(),b'consumerToken']:
            self.assertNotIn(secret,state)
        self.action('read',{'id':resource,'identity':'owner'},'consumer',400)

    def test_authentication_origin_host_and_monitor_token(self):
        self.assertEqual(self.http(role=None)[0],401)
        self.assertEqual(self.http(headers={'Host':'evil.invalid'})[0],403)
        self.assertEqual(self.http(headers={'Origin':'https://evil.invalid'})[0],403)
        token=bridge.managed.core.config(self.directory,'monitor.local')['browserToken']
        self.assertEqual(self.http(headers={'Authorization':'Bearer '+token})[0],401)
        self.assertEqual(self.http('/api/action',body={'action':'preview','payload':{'entry':'inspection.eml'}},headers={'Origin':''})[0],403)

    def test_request_validation_and_asset_headers(self):
        for raw in ('[]','{','x'*4097):self.assertEqual(self.http('/api/action',raw=raw)[0],400)
        self.assertEqual(self.http('/api/action',body={},headers={'Content-Type':'text/plain'})[0],400)
        self.action('arbitrary.operation',{},expected=400)
        self.action('preview',{'entry':'../owner.json'},expected=400)
        code,body,headers=self.http('/',role=None)
        self.assertEqual(code,200);self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
        self.assertEqual(headers['Referrer-Policy'],'no-referrer')
        self.assertNotIn(self.workbench.session['owner'].encode(),body)

    def test_changed_preview_is_not_silently_imported(self):
        payload=self.admission();(self.directory/'source/inspection.eml').write_bytes(b'changed')
        self.action('admit',payload,expected=409)
        self.assertEqual(json.loads(self.http()[1])['items'],[])

    def test_private_item_remains_private(self):
        resource=self.admit(policy='private')
        self.assertEqual(self.action('read',{'id':resource})['text'],bridge.managed.MAIL.decode())
        self.action('grant',{'id':resource,'key':'private-grant'},expected=403)
        self.read(resource,403)
        self.assertIsNone(json.loads(self.http()[1])['pending'])

    def test_idempotency_and_changed_click_payload(self):
        payload=self.admission();first=self.action('admit',payload)
        self.assertEqual(self.action('admit',payload),first)
        self.action('admit',dict(payload,policy='private'),expected=409)
        self.assertEqual(len(json.loads(self.http()[1])['items']),1)

    def lost_reply(self,operation,action,payload):
        original=self.workbench.call
        def lost(op,*args,**kwargs):
            result=original(op,*args,**kwargs)
            if op==operation:raise bridge.Fault('unavailable')
            return result
        with patch.object(self.workbench,'call',side_effect=lost):self.action(action,payload,expected=503)
        self.workbench=bridge.Workbench(self.directory);self.httpd.workbench=self.workbench

    def test_lost_admission_response_reconciles_after_bridge_restart(self):
        payload=self.admission()
        self.lost_reply('item.admit','admit',payload)
        state=json.loads(self.http()[1]);self.assertEqual(state['pending'],{'action':'admit','payload':payload})
        self.action('admit',dict(payload,key='different'),expected=409)
        resource=self.action('admit',payload)['id']
        self.assertEqual(len(json.loads(self.http()[1])['items']),1);self.read(resource,403)

    def test_lost_grant_response_cannot_leave_extra_permission(self):
        resource=self.admit();payload={'id':resource,'key':'lost-grant'}
        self.lost_reply('grant.issue','grant',payload)
        self.action('grant',dict(payload,key='another'),expected=409)
        self.action('grant',payload);self.read(resource)
        self.revoke(resource);self.read(resource,403)

    def test_repeat_grant_revoke_and_regrant(self):
        resource=self.admit();self.grant(resource)
        self.action('grant',{'id':resource,'key':'second'},expected=409)
        self.revoke(resource);self.grant(resource,'fresh');self.read(resource)
        self.revoke(resource,'fresh-revoke');self.read(resource,403)

    def test_lost_revocation_response_recovers_same_receipt(self):
        resource=self.admit();self.grant(resource);payload={'id':resource,'key':'lost-revoke'}
        self.lost_reply('grant.revoke','revoke',payload)
        self.read(resource,403);self.action('revoke',payload)
        self.assertEqual(json.loads(self.http()[1])['items'][0]['sharing'],'Revoked')

    def test_authority_failure_denies_new_content(self):
        resource=self.admit();self.grant(resource);self.read(resource)
        self.processes.stop('wallet.local');self.read(resource,503)
        self.assertEqual(self.http()[0],503)
        self.processes.start('wallet.local');self.read(resource)


if __name__=='__main__':unittest.main()
