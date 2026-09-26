"""Generic directory scenarios: fixtures do not depend on farm domain records."""
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
run = load('directory_run', 'solutions/directory/uc012/run.py')
base = load('ui_cases', 'conformance/uc010/test_runtime.py')


class Directory(unittest.TestCase):
    http = base.Runtime.http
    action = base.Runtime.action
    read = base.Runtime.read
    grant = base.Runtime.grant
    revoke = base.Runtime.revoke

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='farmy-directory-test-');self.addCleanup(temp.cleanup)
        self.source = Path(temp.name)/'external';self.source.mkdir()
        (self.source/'a').mkdir();(self.source/'b').mkdir()
        (self.source/'a'/'record.csv').write_text('key,value\nexample,42\n')
        (self.source/'b'/'record.csv').write_text('key,value\nother,23\n')
        self.directory = run.bootstrap(Path(temp.name)/'runtime', self.source)
        self.processes = run.server.managed.core.Processes(self.directory, run.SERVICES)
        self.addCleanup(self.processes.__exit__, None, None, None);self.processes.__enter__()
        self.workbench = run.Workbench(self.directory)
        self.httpd = run.server.Server(self.workbench);self.addCleanup(self.httpd.server_close)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start();self.addCleanup(self.httpd.shutdown)
        self.origin = f'http://127.0.0.1:{self.httpd.server_port}'

    def catalogue(self):
        return json.loads(self.http()[1])['catalogue']

    def admit(self):
        item = self.catalogue()[0]
        preview = self.action('preview', {'entry':item['entry']})
        result = self.action('admit',dict(entry=item['entry'],sha256=preview['sha256'],policy='restricted',key='admit'))
        return item, result['id']

    def test_nested_duplicate_names_and_exact_copy_access(self):
        items = self.catalogue()
        self.assertEqual([i['path'] for i in items],['a/record.csv','b/record.csv'])
        self.assertNotEqual(items[0]['entry'],items[1]['entry'])
        item,resource = self.admit()
        self.read(resource,403);self.grant(resource)
        original = (self.source/item['path']).read_text()
        self.assertEqual(self.read(resource)['text'],original)
        metadata = json.loads(self.http()[1])['items'][0]
        self.assertEqual(metadata['title'],item['path'])
        (self.source/item['path']).unlink()
        self.assertEqual(self.read(resource)['text'],original)
        self.revoke(resource);self.read(resource,403)

    def test_consumer_cannot_browse_or_discover_paths(self):
        self.catalogue()
        state = json.loads(self.http(role='consumer')[1])
        self.assertNotIn('catalogue',state);self.assertNotIn('entries',state)
        run.server.managed.core.expect_fault('denied',lambda:run.server.managed.call(self.directory,'folder.browse',run.server.managed.scope(self.workbench.session['source']),identity='reader'))

    def test_source_unchanged_and_upload_denied(self):
        before = {str(p.relative_to(self.source)):p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        self.admit()
        run.server.managed.core.expect_fault('denied',lambda:run.server.managed.call(self.directory,'folder.upload',dict(run.server.managed.scope(self.workbench.session['source']),name='x.txt',contentBase64='eA==')))
        after = {str(p.relative_to(self.source)):p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_symlinks_hidden_entries_and_directory_swap(self):
        outside = self.source.parent/'outside';outside.mkdir();(outside/'secret.txt').write_text('secret')
        (self.source/'link').symlink_to(outside,target_is_directory=True)
        (self.source/'.hidden').write_text('secret')
        items = self.catalogue();self.assertEqual(len(items),2)
        (self.source/'a'/'record.csv').unlink();(self.source/'a').rmdir()
        (self.source/'a').symlink_to(outside,target_is_directory=True)
        self.action('preview',{'entry':items[0]['entry']},expected=403)

    def test_changed_preview_cannot_be_admitted(self):
        item = self.catalogue()[0];preview=self.action('preview',{'entry':item['entry']})
        (self.source/item['path']).write_text('changed')
        self.action('admit',dict(entry=item['entry'],sha256=preview['sha256'],policy='private',key='stale'),expected=409)

    def test_large_binary_and_invalid_text_are_explicit(self):
        (self.source/'large.csv').write_bytes(b'x'*16385)
        (self.source/'binary.pdf').write_bytes(b'%PDF')
        (self.source/'invalid.txt').write_bytes(b'\xff')
        (self.source/'structure.json').write_text('{"example":42}')
        items={i['path']:i for i in self.catalogue()}
        self.assertTrue(items['large.csv']['reason']);self.assertTrue(items['binary.pdf']['reason'])
        for name in ('large.csv','binary.pdf','invalid.txt'):
            self.action('preview',{'entry':items[name]['entry']},expected=400)
        self.assertEqual(self.action('preview',{'entry':items['structure.json']['entry']})['text'],'{"example":42}')

    def test_handles_and_admission_receipts_survive_restart(self):
        before=self.catalogue();item,resource=self.admit()
        self.processes.stop('connector.local');self.processes.start('connector.local')
        self.workbench=run.Workbench(self.directory);self.httpd.workbench=self.workbench
        self.assertEqual(self.catalogue(),before)
        self.assertEqual(json.loads(self.http()[1])['items'][0]['id'],resource)

    def test_inventory_limit_fails_without_partial_result(self):
        for i in range(99): (self.source/f'entry-{i}.txt').write_text('x')
        self.assertEqual(self.http()[0],400)

    def test_wallet_outage_blocks_directory_metadata(self):
        self.processes.stop('wallet.local');self.assertEqual(self.http()[0],503)


if __name__ == '__main__':unittest.main()
