"""Upload through HTTP and real Connector; no shared private-store writes."""
import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
run=load('upload_run','solutions/uploads/uc011/run.py')
base=load('ui_tests','conformance/uc010/test_runtime.py')

class Uploads(unittest.TestCase):
    http=base.Runtime.http
    action=base.Runtime.action
    read=base.Runtime.read
    grant=base.Runtime.grant
    revoke=base.Runtime.revoke
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='farmy-upload-test-');self.addCleanup(temp.cleanup)
        self.directory=run.bootstrap(temp.name)
        self.processes=run.server.managed.core.Processes(self.directory,run.server.managed.SERVICES)
        self.addCleanup(self.processes.__exit__,None,None,None);self.processes.__enter__()
        self.workbench=run.server.Workbench(self.directory,allow_uploads=True)
        self.httpd=run.server.Server(self.workbench);self.addCleanup(self.httpd.server_close)
        threading.Thread(target=self.httpd.serve_forever,daemon=True).start();self.addCleanup(self.httpd.shutdown)
        self.origin=f'http://127.0.0.1:{self.httpd.server_port}'

    def payload(self,name='Field notes.txt',data=b'Crop: oats\n',key='upload'):
        return dict(name=name,contentBase64=base64.b64encode(data).decode(),key=key)

    def test_upload_exact_bytes_admit_grant_revoke(self):
        content='Région: Bruxelles\nCrop: oats\n'.encode()
        result=self.action('upload',self.payload(data=content))
        self.assertEqual(self.action('preview',{'entry':result['entry']})['text'],content.decode())
        self.assertEqual(json.loads(self.http()[1])['items'],[])
        resource=self.action('admit',dict(entry=result['entry'],sha256=result['sha256'],policy='restricted',key='admit'))['id']
        self.read(resource,403);self.grant(resource);self.assertEqual(self.read(resource)['text'],content.decode());self.revoke(resource);self.read(resource,403)

    def test_upload_denies_consumer_and_unenrolled_service_caller(self):
        self.action('upload',self.payload(),'consumer',403)
        source=run.server.managed.scope(self.workbench.session['source'])
        for identity in ('reader','monitor.local'):
            run.server.managed.core.expect_fault('denied',lambda:run.server.managed.call(self.directory,'folder.upload',dict(source,name='x.txt',contentBase64='YQ=='),identity=identity))

    def test_types_sizes_encoding_and_path_rejection(self):
        for i,payload in enumerate([self.payload(name='../x.txt'),self.payload(name='x.pdf'),self.payload(data=b'\xff'),self.payload(data=b'\0binary'),self.payload(data=b'a'*16385),dict(self.payload(),contentBase64='!!!')]):
            payload['key']=str(i);self.action('upload',payload,expected=400)
        self.assertEqual(len(json.loads(self.http()[1])['entries']),2)
        self.action('upload',self.payload(data=b'a'*16384))

    def test_same_name_never_overwrites_original(self):
        first=self.action('upload',self.payload(name='inspection.eml'))
        second=self.action('upload',self.payload(name='inspection.eml',data=b'Other bytes',key='other'))
        self.assertNotEqual(first['entry'],second['entry'])
        self.assertEqual(self.action('preview',{'entry':'inspection.eml'})['text'],run.server.managed.MAIL.decode())
        self.assertEqual(self.action('preview',{'entry':first['entry']})['text'],'Crop: oats\n')

    def test_retries_restart_and_conflicting_key(self):
        payload=self.payload();first=self.action('upload',payload)
        self.processes.stop('connector.local');self.processes.start('connector.local')
        self.workbench=run.server.Workbench(self.directory,allow_uploads=True);self.httpd.workbench=self.workbench
        self.assertEqual(self.action('upload',payload),first)
        self.action('upload',self.payload(data=b'changed'),expected=409)
        self.assertEqual(self.action('upload',dict(payload,key='same-content')),first)
        self.assertEqual(len(json.loads(self.http()[1])['entries']),3)

    def test_lost_upload_reply_recovers_without_another_file(self):
        original=self.workbench.call
        def lost(op,*args,**kwargs):
            result=original(op,*args,**kwargs)
            if op=='folder.upload':raise run.server.Fault('unavailable')
            return result
        with patch.object(self.workbench,'call',side_effect=lost):self.action('upload',self.payload(),expected=503)
        self.workbench=run.server.Workbench(self.directory,allow_uploads=True);self.httpd.workbench=self.workbench
        self.action('upload',self.payload())
        self.assertEqual(len(json.loads(self.http()[1])['entries']),3)
        self.assertIsNone(json.loads(self.http()[1])['pending'])

    def test_wallet_outage_does_not_accept_upload(self):
        self.processes.stop('wallet.local');self.action('upload',self.payload(),expected=503)
        self.processes.start('wallet.local')
        self.assertEqual(len(json.loads(self.http()[1])['entries']),2)
        self.action('upload',self.payload())

    def test_upload_is_disabled_unless_connector_opts_in(self):
        self.processes.stop('connector.local')
        path=self.directory/'connector.local.json'
        config=json.loads(path.read_text());config['allowUploads']=False
        path.write_text(json.dumps(config));self.processes.start('connector.local')
        self.action('upload',self.payload(),expected=403)
        self.assertEqual(len(json.loads(self.http()[1])['entries']),2)

    def test_symlink_cannot_redirect_upload(self):
        import hashlib
        target=self.directory/'untouched.txt';target.write_bytes(b'outside source')
        name='Field-notes-'+hashlib.sha256(b'Crop: oats\n').hexdigest()+'.txt'
        (self.directory/'source'/name).symlink_to(target)
        self.action('upload',self.payload(),expected=403)
        self.assertEqual(target.read_bytes(),b'outside source')

    def test_capacity_rejects_new_files_but_allows_retries(self):
        payload=self.payload();receipt=self.action('upload',payload)
        for i in range(97): (self.directory/'source'/f'quota-{i}.txt').write_bytes(b'x')
        self.assertEqual(self.action('upload',dict(payload,key='repeat')),receipt)
        self.action('upload',self.payload(data=b'new',key='new'),expected=400)
        self.assertEqual(len(json.loads(self.http()[1])['entries']),100)

    def test_html_is_preserved_as_inert_text(self):
        content=b'<script>alert("test")</script>\n'
        result=self.action('upload',self.payload(data=content))
        preview=self.action('preview',{'entry':result['entry']})
        self.assertEqual(preview['text'],content.decode())
        self.assertIn("default-src 'self'",self.http('/')[2]['Content-Security-Policy'])

if __name__=='__main__':unittest.main()
