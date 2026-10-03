import base64
import hashlib
import http.client
import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'modules/processing/bounded_text'))
from server import Handler, HTTPServer
spec = importlib.util.spec_from_file_location('install', ROOT/'deployments/providers/scaleway/install.py')
install = importlib.util.module_from_spec(spec); spec.loader.exec_module(install)

class Deployment(unittest.TestCase):
    def setUp(self):
        self.p = install.plan('11111111-1111-4111-8111-111111111111',
                              '22222222-2222-4222-8222-222222222222', 'fr-par',
                              'farmy-text', 'ghcr.io/example/farmy/bounded-text@sha256:'+'a'*64)

    def test_pinned_public_image_only(self):
        for image in ('ghcr.io/example/farmy:latest', 'https://user:secret@example.com', 'x; echo bad'):
            with self.assertRaises(ValueError):
                install.plan(self.p['project'], self.p['namespace'], 'fr-par', 'farmy-text', image)

    def test_private_bounded_create(self):
        args = install.create_args(self.p)
        for required in ('privacy=private', 'max-scale=1', 'min-scale=0', 'https-connections-only=true'):
            self.assertIn(required, args)
        self.assertFalse(any('secret' in arg for arg in args))

    def test_namespace_mismatch_secrets_and_existing_resources_rejected(self):
        clean = dict(project_id=self.p['project'], region='fr-par')
        for ns, items in ((dict(clean, project_id='other'), []),
                          (dict(clean, secret_environment_variables=[{'key':'PASSWORD'}]), []),
                          (clean, [{'id':'already-created'}])):
            with self.assertRaises(ValueError):
                install.preflight(self.p, lambda *args: ns if 'get' in args else items)
        install.preflight(self.p, lambda *args: clean if 'get' in args else [])

class HTTPContract(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        data = b'Synthetic only.\n'
        digest = hashlib.sha256(data).hexdigest()
        self.query = dict(contract='farmy.processing.text/0.1-draft', operation='text.stats', requestId='test-00001',
            payload=dict(receiverId='processor.scaleway', purpose='text-statistics', evidence=dict(
                schema='farmy.evidence/0.1-draft', contentBase64=base64.b64encode(data).decode(),
                resource=dict(id='sha256:'+digest, sha256=digest, size=len(data), mediaType='text/plain;charset=utf-8'))))

    def tearDown(self):
        self.server.shutdown(); self.thread.join(); self.server.server_close()

    def post(self, body, headers=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=3)
        connection.request('POST', '/process', body, headers or {'Content-Type':'application/json'})
        response = connection.getresponse(); status = response.status; value = json.loads(response.read())
        connection.close(); return status, value

    def test_valid_stats_and_remote_identity(self):
        status, result = self.post(json.dumps(self.query))
        self.assertEqual(status, 200); self.assertEqual(result['producerId'], 'processor.scaleway')
        self.assertEqual(result['output']['words'], 2)
        self.query['payload']['receiverId'] = 'processor.local'
        self.assertEqual(self.post(json.dumps(self.query))[0], 400)

    def test_malformed_tampered_duplicate_and_oversized_inputs(self):
        for body in ('null', '{"contract":1,"contract":2}', '[]'):
            self.assertEqual(self.post(body)[0], 400)
        self.query['payload']['evidence']['resource']['sha256'] = '0'*64
        self.assertEqual(self.post(json.dumps(self.query))[0], 400)
        self.assertEqual(self.post('x'*65537)[0], 413)
        self.assertEqual(self.post('{}', {'Content-Type':'text/plain'})[0], 415)

if __name__ == '__main__': unittest.main()
