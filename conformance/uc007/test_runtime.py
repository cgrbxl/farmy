"""Local S3-double checks only; provider compatibility requires a real run."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uc007_run', ROOT / 'solutions/s3-source/uc007/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from farmy_transport.http import Fault, MAX_BYTES, exchange


class Configuration(unittest.TestCase):
    def settings(self):
        return {'region':'fr-par', 'endpoint':'https://s3.fr-par.scw.cloud', 'bucket':'synthetic-bucket',
                'prefix':'farmy-tests/', 'accessKeyEnv':'FARMY_TEST_ACCESS', 'secretKeyEnv':'FARMY_TEST_SECRET'}

    def test_endpoint_and_scope_are_explicit(self):
        base = self.settings()
        for change in [{'endpoint':'http://s3.fr-par.scw.cloud'}, {'endpoint':'https://external.invalid'},
                       {'prefix':''}, {'prefix':'../'}, {'prefix':'test'}, {'bucket':'bad/bucket'},
                       {'aws_secret_access_key':'do-not-embed'}, {'credentialProfile':'default'}]:
            with self.subTest(change=change), self.assertRaises((ValueError, Fault)):
                run.s3.validate_settings(dict(base, **change))
        run.s3.validate_settings(base)

    def test_no_ambient_credential_fallback(self):
        with patch.dict(os.environ, {'AWS_ACCESS_KEY_ID':'unrelated', 'AWS_SECRET_ACCESS_KEY':'unrelated'}, clear=True):
            with self.assertRaises(ValueError): run.s3.client(self.settings())
        with patch.dict(os.environ, {'FARMY_TEST_ACCESS':'explicit', 'FARMY_TEST_SECRET':'explicit'}, clear=True):
            self.assertEqual(run.s3.credentials(self.settings()), ('explicit','explicit',None))
            config = dict(self.settings(), sessionTokenEnv='MISSING_SESSION')
            with self.assertRaises(ValueError): run.s3.credentials(config)

    def test_fixture_mode_cannot_send_real_credentials(self):
        base = {'region':'fr-par','endpoint':'http://127.0.0.1:8123','bucket':'farmy-fixture','prefix':'farmy-tests/','fixture':True}
        run.s3.validate_settings(base)
        for change in [{'credentialProfile':'scaleway'}, {'accessKeyEnv':'SECRET'},
                       {'endpoint':'http://example.invalid'}, {'endpoint':'http://127.0.0.1:8123/path'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                run.s3.validate_settings(dict(base, **change))


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-s3-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.source = run.fixture.Fixture()
        cls.running = cls.source.running()
        cls.running.__enter__()
        cls.addClassCleanup(cls.running.__exit__, None, None, None)
        cls.directory = run.bootstrap(cls.temp.name, cls.source.settings())
        cls.processes = run.core.Processes(cls.directory, run.SERVICES)
        cls.addClassCleanup(cls.processes.__exit__, None, None, None)
        cls.processes.__enter__()

    def setUp(self):
        self.source.versioned = True
        self.source.denied = False
        self.source.available = True
        self.source.after_head = None
        self.source.bad_length = False
        self.source.put('report.txt', run.documents.REPORT)

    def fault(self, code, fn):
        with self.assertRaises(Fault) as caught: fn()
        self.assertEqual(caught.exception.code, code)

    def register(self, path='report.txt'):
        return run.core.call(self.directory, 'resource.register', {'path':path})

    def test_01_existing_pipeline_and_read_only_s3_calls(self):
        result = run.exercise(self.directory, 'report.txt')
        self.assertEqual(result[0]['sha256'], result[2]['manifest']['sha256'])
        self.assertTrue(self.source.calls)
        self.assertTrue(all(method in ('HEAD','GET') and signed for method,key,signed in self.source.calls))
        self.assertTrue(all(key.startswith('farmy-tests/') for _,key,_ in self.source.calls))

    def test_02_versioned_overwrite_captures_pinned_old_object(self):
        self.source.after_head = lambda: self.source.put('report.txt', b'changed after head')
        resource = self.register()
        grant = run.core.grant(self.directory, resource)
        self.assertEqual(run.core.read(self.directory, resource, grant), run.documents.REPORT)

    def test_03_unversioned_overwrite_fails_condition(self):
        self.source.versioned = False
        self.source.after_head = lambda: self.source.put('report.txt', b'changed after head')
        self.fault('conflict', self.register)

    def test_04_key_scope_rejected_before_provider_call(self):
        before = len(self.source.calls)
        for path in ('../private', '/absolute', 'a/../b', 'a//b', 'a\\b', 'https://elsewhere', 'a%2f..', 'a?x=1'):
            self.fault('denied', lambda: self.register(path))
        self.assertEqual(len(self.source.calls), before)

    def test_05_provider_denial_outage_and_missing_object(self):
        self.source.denied = True
        self.fault('denied', self.register)
        self.source.denied = False
        self.fault('not_found', lambda: self.register('missing.txt'))
        self.source.available = False
        self.fault('unavailable', self.register)

    def test_06_size_and_truncated_response_never_register(self):
        self.source.put('large.txt', b'x'*(MAX_BYTES+1))
        self.fault('denied', lambda: self.register('large.txt'))
        self.source.bad_length = True
        self.fault('conflict', self.register)

    def test_07_retained_versions_survive_provider_change_and_restart(self):
        resource = self.register()
        grant = run.core.grant(self.directory, resource)
        self.source.put('report.txt', b'crop: rye\n')
        updated = run.core.call(self.directory, 'resource.update', {'resourceId':resource['resourceId']},
                                refs=run.core.refs(resource), revision=1)
        second_grant = run.core.grant(self.directory, updated)
        self.source.available = False
        calls = len(self.source.calls)
        self.processes.stop('connector.local')
        self.processes.start('connector.local')
        self.assertEqual(run.core.read(self.directory, resource, grant), run.documents.REPORT)
        self.assertEqual(run.core.read(self.directory, updated, second_grant), b'crop: rye\n')
        self.assertEqual(len(self.source.calls), calls)
        run.core.call(self.directory, 'grant.revoke', {'grantId':grant['grantId']}, revision=1)
        self.fault('denied', lambda: run.core.read(self.directory, resource, grant))
        self.processes.stop('wallet.local')
        try: self.fault('unavailable', lambda: run.core.read(self.directory, updated, second_grant))
        finally: self.processes.start('wallet.local')

    def test_08_monitoring_does_not_disclose_provider_settings(self):
        self.register()
        snapshot = run.exports.monitor.bridge.snapshot(run.core.config(self.directory,'monitor.local'))
        self.assertEqual(len(snapshot['nodes']),6)
        self.assertTrue(all(n['status']=='available' for n in snapshot['nodes']))
        encoded = json.dumps(snapshot)
        for private in ('farmy-fixture','farmy-tests/',run.s3.FIXTURE_SECRET):
            self.assertNotIn(private, encoded)
        self.fault('denied',lambda: exchange(run.core.config(self.directory,'reader'),'connector.local',path='/farmy/v0/monitor/summary'))
        config = run.core.config(self.directory,'connector.local')
        self.assertNotIn('sourceRoot',config)
        self.assertNotIn(run.s3.FIXTURE_SECRET,json.dumps(config))


if __name__ == '__main__': unittest.main()
