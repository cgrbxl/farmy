"""Acceptance evidence against real, separate processes over mutual TLS."""
import copy
import http.client
import importlib.util
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'solutions/core/uc001'))
import run
from farmy_transport.http import (Fault, FOUNDATION, MAX_BYTES, client_context, exchange,
                                  request, schema_check, utc)


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = run.bootstrap(cls.temp.name)
        cls.processes = run.Processes(cls.directory)
        cls.addClassCleanup(cls.processes.__exit__, None, None, None)
        cls.processes.__enter__()
        cls.owner = run.config(cls.directory)

    def fixture(self):
        resource = run.call(self.directory, 'resource.register', {'path': 'record.txt'})
        return resource, run.grant(self.directory, resource)

    def denied(self, code, action):
        with self.assertRaises(Fault) as result:
            action()
        self.assertEqual(result.exception.code, code)

    def test_01_versions_move_idempotency_restart_revocation(self):
        source = self.directory / 'source'
        (source / 'history.txt').write_bytes(run.V1)
        resource = run.call(self.directory, 'resource.register', {'path': 'history.txt'}, key='key.history')
        replay = run.call(self.directory, 'resource.register', {'path': 'history.txt'}, key='key.history')
        self.assertEqual(resource, replay)
        self.denied('conflict', lambda: run.call(self.directory, 'resource.register',
                                                {'path': 'record.txt'}, key='key.history'))
        permission = run.grant(self.directory, resource)
        self.assertEqual(run.read(self.directory, resource, permission), run.V1)
        (source / 'history.txt').rename(source / 'history-moved.txt')
        moved = run.call(self.directory, 'resource.move', {'resourceId': resource['resourceId'],
                        'path': 'history-moved.txt'}, refs=run.refs(resource), revision=1)
        self.assertEqual(moved['resourceId'], resource['resourceId'])
        self.assertEqual(moved['versionId'], resource['versionId'])
        self.denied('conflict', lambda: run.call(self.directory, 'resource.update',
                    {'resourceId': resource['resourceId']}, refs=run.refs(resource), revision=1))
        (source / 'history-moved.txt').write_bytes(run.V2)
        updated = run.call(self.directory, 'resource.update', {'resourceId': moved['resourceId']},
                           refs=run.refs(moved), revision=2)
        self.assertNotEqual(updated['versionId'], resource['versionId'])
        self.assertEqual(updated['resourceId'], resource['resourceId'])
        fresh_grant = run.grant(self.directory, updated)
        self.assertEqual(run.read(self.directory, updated, fresh_grant), run.V2)
        self.assertEqual(run.read(self.directory, resource, permission), run.V1)
        for identity in run.SERVICES:
            self.processes.stop(identity)
            self.processes.start(identity)
        self.assertEqual(run.read(self.directory, resource, permission), run.V1)
        run.call(self.directory, 'grant.revoke', {'grantId': permission['grantId']}, revision=1)
        self.denied('denied', lambda: run.read(self.directory, resource, permission))
        self.assertEqual(run.read(self.directory, updated, fresh_grant), run.V2)

    def test_02_identity_scope_and_direct_access(self):
        resource, permission = self.fixture()
        for identity, code in [('denied', 'denied'), ('owner', 'denied'), ('unknown', 'unauthenticated')]:
            with self.subTest(identity=identity):
                self.denied(code, lambda: run.read(self.directory, resource, permission, identity))
        reader = run.config(self.directory, 'reader')
        body = request(reader, 'connector.local', 'read.version', {}, refs=run.refs(resource), grant=permission['grantId'])
        for field, value in [('actorId', 'owner'), ('subjectId', 'owner'), ('walletId', 'wallet.other'),
                             ('purpose', 'other'), ('targetInstanceId', 'wallet.local')]:
            altered = dict(body, **{field: value})
            self.denied('denied', lambda: exchange(reader, 'connector.local', altered))
        sibling, _ = self.fixture()
        self.denied('denied', lambda: run.read(self.directory, sibling, permission))
        self.denied('denied', lambda: run.call(self.directory, 'snapshot.capture', {'path': 'record.txt'}))
        self.denied('denied', lambda: run.call(self.directory, 'authorize.read', refs=run.refs(resource),
                                               grant=permission['grantId'], identity='reader'))
        self.denied('denied', lambda: exchange(reader, 'wallet.local', path='/farmy/v0/descriptor'))
        self.denied('denied', lambda: exchange(reader, 'wallet.local', path='/farmy/v0/health/ready'))

    def test_03_root_and_size_boundaries(self):
        source = self.directory / 'source'
        outside = self.directory / 'outside.txt'
        outside.write_bytes(b'outside fixture')
        (source / 'escape.txt').symlink_to(outside)
        (source / 'escape-dir').symlink_to(self.directory, target_is_directory=True)
        (source / 'oversized.txt').write_bytes(b'x' * (MAX_BYTES + 1))
        for path in ['../outside.txt', str(outside), 'escape.txt', 'escape-dir/outside.txt',
                     'oversized.txt', 'missing.txt', './record.txt', 'a/../record.txt']:
            with self.subTest(path=path):
                self.denied('denied', lambda: run.call(self.directory, 'resource.register', {'path': path}))

    def test_04_dependencies_fail_closed(self):
        resource, permission = self.fixture()
        self.processes.stop('wallet.local')
        try:
            start = time.monotonic()
            self.denied('unavailable', lambda: run.read(self.directory, resource, permission))
            self.assertLess(time.monotonic() - start, 5)
            self.denied('unavailable', lambda: exchange(self.owner, 'connector.local', path='/farmy/v0/health/ready'))
        finally:
            self.processes.start('wallet.local')
        self.processes.stop('connector.local')
        try:
            self.denied('unavailable', lambda: run.call(self.directory, 'resource.register', {'path': 'record.txt'}))
        finally:
            self.processes.start('connector.local')
        self.assertEqual(run.read(self.directory, resource, permission), run.V1)

    def test_05_tls_and_pin(self):
        endpoint = self.owner['endpoints']['wallet.local']
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(self.owner['ca'])
        conn = http.client.HTTPSConnection('127.0.0.1', int(endpoint['url'].rsplit(':', 1)[1]), context=context, timeout=3)
        try:
            with self.assertRaises((OSError, http.client.HTTPException)):
                conn.request('GET', '/farmy/v0/health/live')
                conn.getresponse()
        finally:
            conn.close()
        altered = copy.deepcopy(self.owner)
        altered['endpoints']['wallet.local']['fingerprint'] = '0' * 64
        self.denied('unauthenticated', lambda: exchange(altered, 'wallet.local', path='/farmy/v0/health/live'))

    def test_06_contracts_and_expiration(self):
        from jsonschema import Draft202012Validator
        operation_schema = json.loads((ROOT / 'contracts/uc001/operations.schema.json').read_text())
        Draft202012Validator.check_schema(operation_schema)
        api = json.loads((ROOT / 'contracts/uc001/openapi.json').read_text())
        expected_operations = {key[:-6] for key in operation_schema['$defs'] if key.endswith('.input')}
        self.assertEqual({value['post']['operationId'] for value in api['paths'].values()}, expected_operations)
        for service in run.SERVICES:
            records = exchange(self.owner, service, path='/farmy/v0/descriptor')
            for kind in ('module', 'instance'):
                schema_check(FOUNDATION, kind, records[kind])
        body = request(self.owner, 'wallet.local', 'resource.register', {'path': 'record.txt'})
        self.denied('expired', lambda: exchange(self.owner, 'wallet.local', dict(body, deadline=utc(-1))))
        self.denied('invalid_request', lambda: exchange(self.owner, 'wallet.local', dict(body, unexpected=True)))
        self.denied('invalid_request', lambda: exchange(self.owner, 'wallet.local', dict(body, payload={'path': 'record.txt', 'extra': True})))
        resource, _ = self.fixture()
        output = subprocess.run([sys.executable, str(ROOT / 'solutions/core/uc001/run.py'),
                'request', '--directory', str(self.directory), '--operation', 'resource.inspect',
                '--payload', json.dumps({'resourceId': resource['resourceId']})],
                capture_output=True, text=True, check=True, timeout=5)
        self.assertEqual(json.loads(output.stdout), resource)
        permission = run.call(self.directory, 'grant.issue', {'resourceId': resource['resourceId'],
                       'versionId': resource['versionId'], 'subjectId': 'reader', 'expiresAt': utc(.5),
                       'purpose': 'uc001.read'}, refs=run.refs(resource))
        time.sleep(.6)
        self.denied('denied', lambda: run.read(self.directory, resource, permission))
        # Inspect the wire envelope, not just the client exception.
        reader = run.config(self.directory, 'reader')
        body = request(reader, 'wallet.local', 'resource.inspect', {'resourceId': resource['resourceId']})
        port = int(reader['endpoints']['wallet.local']['url'].rsplit(':', 1)[1])
        conn = http.client.HTTPSConnection('127.0.0.1', port, context=client_context(reader), timeout=3)
        try:
            conn.request('POST', '/farmy/v0/resource.inspect', json.dumps(body), {'Content-Type': 'application/json'})
            response = conn.getresponse()
            self.assertEqual(response.status, 403)
            data = json.loads(response.read())
            schema_check(FOUNDATION, 'response', data)
            self.assertEqual(data['status'], 'failed')
            self.assertNotIn('result', data)
        finally:
            conn.close()

    def test_07_corrupted_snapshot_unavailable(self):
        (self.directory / 'source/corrupt.txt').write_bytes(b'unique corruption fixture')
        resource = run.call(self.directory, 'resource.register', {'path': 'corrupt.txt'})
        permission = run.grant(self.directory, resource)
        snapshot = self.directory / 'state-connector.local/snapshots' / resource['sha256']
        snapshot.write_bytes(b'changed')
        self.denied('unavailable', lambda: run.read(self.directory, resource, permission))


class CaptureRace(unittest.TestCase):
    def test_mutation_during_capture_is_rejected(self):
        spec = importlib.util.spec_from_file_location('local_connector', ROOT / 'modules/connectors/local_folder/service.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'record.txt'
            source.write_bytes(run.V1)
            fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            original_read = os.read
            changed = False
            def racing_read(file_fd, count):
                nonlocal changed
                data = original_read(file_fd, count)
                if not changed:
                    source.write_bytes(run.V2)
                    changed = True
                return data
            try:
                with patch.object(module.os, 'read', racing_read):
                    with self.assertRaises(Fault) as result:
                        module.safe_read(fd, 'record.txt')
                self.assertEqual(result.exception.code, 'conflict')
            finally:
                os.close(fd)


if __name__ == '__main__':
    unittest.main()
