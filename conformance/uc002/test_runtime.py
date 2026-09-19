"""UC-002 acceptance checks across five real mutually authenticated processes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uc002_run', ROOT / 'solutions/document-path/uc002/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from farmy_transport.http import Fault, FOUNDATION, exchange, request, schema_check, utc


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-uc002-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = run.bootstrap(cls.temp.name)
        cls.processes = run.core.Processes(cls.directory, run.SERVICES)
        cls.addClassCleanup(cls.processes.__exit__, None, None, None)
        cls.processes.__enter__()

    def fixture(self, data=run.REPORT):
        path = 'fixture-' + str(time.time_ns()) + '.txt'
        (self.directory / 'source' / path).write_bytes(data)
        resource = run.core.call(self.directory, 'resource.register', {'path': path})
        grants, permission = run.permissions(self.directory, resource)
        return resource, grants, permission

    def execute(self, resource, grants, key='key.default'):
        return run.call(self.directory, 'job.run', grants, refs=run.core.refs(resource), key=key)

    def denied(self, code, action):
        with self.assertRaises(Fault) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_01_exact_evidence_duplicate_concurrent_and_restart(self):
        data = 'Farmy synthetic report é\ncrop: wheat\n'.encode()
        resource, grants, permission = self.fixture(data)
        with ThreadPoolExecutor(max_workers=3) as pool:
            receipts = list(pool.map(lambda _: self.execute(resource, grants, 'key.concurrent'), range(3)))
        self.assertTrue(all(result == receipts[0] for result in receipts))
        other = self.execute(resource, grants, 'key.duplicate-delivery')
        self.assertEqual(other['proposalId'], receipts[0]['proposalId'])
        evidence = run.query(self.directory, resource, permission)
        self.assertEqual(evidence['source'], run.core.refs(resource)[0])
        self.assertEqual(evidence['sourceSha256'], hashlib.sha256(data).hexdigest())
        self.assertEqual(evidence['value'], 'wheat')
        self.assertEqual(evidence['line'], 2)
        self.assertEqual(data[evidence['byteStart']:evidence['byteEnd']].decode(), evidence['quote'])
        self.assertEqual(evidence['extractor'], 'farmy.text-field/0.1.0')
        # Test-only storage inspection verifies duplicate acceptance, not a service dependency.
        with sqlite3.connect(self.directory / 'state-knowledge.local/state.sqlite') as db:
            count = db.execute('SELECT count(*) FROM evidence WHERE proposal=?', (other['proposalId'],)).fetchone()[0]
        self.assertEqual(count, 1)
        for service in run.SERVICES:
            self.processes.stop(service)
            self.processes.start(service)
        self.assertEqual(self.execute(resource, grants, 'key.concurrent'), receipts[0])
        self.assertEqual(run.query(self.directory, resource, permission), evidence)

    def test_02_version_scope_and_old_evidence(self):
        resource, grants, permission = self.fixture()
        self.execute(resource, grants, 'key.history1')
        (self.directory / 'source' / resource['path']).write_bytes(run.REPORT.replace(b'wheat', b'barley'))
        updated = run.core.call(self.directory, 'resource.update', {'resourceId': resource['resourceId']},
                                refs=run.core.refs(resource), revision=resource['revision'])
        new_grants, new_permission = run.permissions(self.directory, updated)
        self.denied('denied', lambda: run.query(self.directory, updated, permission))
        self.denied('conflict', lambda: self.execute(updated, new_grants, 'key.history1'))
        self.execute(updated, new_grants, 'key.history2')
        self.assertEqual(run.query(self.directory, updated, new_permission)['value'], 'barley')
        self.assertEqual(run.query(self.directory, resource, permission)['value'], 'wheat')

    def test_03_query_security_revocation_expiry_and_wallet_down(self):
        resource, grants, permission = self.fixture()
        self.execute(resource, grants, 'key.security')
        for identity, code in [('denied','denied'), ('owner','denied'), ('unknown','unauthenticated')]:
            self.denied(code, lambda: run.query(self.directory, resource, permission, identity))
        reader = run.core.config(self.directory, 'reader')
        body = request(reader, 'knowledge.local', 'evidence.query', {'field': 'crop'},
                       refs=run.core.refs(resource), grant=permission['grantId'])
        for field, value in [('subjectId','owner'), ('actorId','owner'), ('walletId','wallet.other'), ('purpose','uc002.index')]:
            self.denied('denied', lambda: exchange(reader, 'knowledge.local', dict(body, **{field:value})))
        self.denied('denied', lambda: run.query(self.directory, resource, {'grantId': grants['indexGrant']}))
        sibling, _, _ = self.fixture()
        self.denied('denied', lambda: run.query(self.directory, sibling, permission))
        run.call(self.directory, 'access.revoke', {'grantId': permission['grantId']}, revision=1)
        self.denied('denied', lambda: run.query(self.directory, resource, permission))
        self.denied('conflict', lambda: run.call(self.directory, 'access.revoke', {'grantId': permission['grantId']}, revision=1))
        short = run.call(self.directory, 'access.issue', {'resourceId': resource['resourceId'], 'versionId': resource['versionId'],
                        'subjectId':'reader', 'audience':'knowledge.local', 'operation':'evidence.query', 'purpose':'uc002.query',
                        'expiresAt':utc(.5)}, refs=run.core.refs(resource))
        time.sleep(.6)
        self.denied('denied', lambda: run.query(self.directory, resource, short))
        fresh = run.scoped(self.directory, resource, 'reader', 'knowledge.local', 'evidence.query', 'uc002.query')
        self.processes.stop('wallet.local')
        try:
            start = time.monotonic()
            self.denied('unavailable', lambda: run.query(self.directory, resource, fresh))
            self.assertLess(time.monotonic() - start, 5)
        finally:
            self.processes.start('wallet.local')

    def test_04_separate_transfer_index_and_read_permissions(self):
        resource, grants, permission = self.fixture()
        altered = dict(grants, sourceReadGrant=permission['grantId'])
        self.denied('denied', lambda: self.execute(resource, altered, 'key.no-source'))
        altered = dict(grants, disclosureGrant=grants['indexGrant'])
        self.denied('denied', lambda: self.execute(resource, altered, 'key.no-disclosure'))
        self.denied('not_found', lambda: run.query(self.directory, resource, permission))
        altered = dict(grants, indexGrant=grants['disclosureGrant'])
        self.denied('denied', lambda: self.execute(resource, altered, 'key.no-index'))
        self.denied('not_found', lambda: run.query(self.directory, resource, permission))
        self.execute(resource, grants, 'key.all-permissions')
        self.denied('denied', lambda: run.call(self.directory, 'extraction.get',
                    {'proposalId':'proposal.unknown'}, identity='reader', refs=run.core.refs(resource), grant=permission['grantId']))
        self.denied('denied', lambda: run.call(self.directory, 'extraction.compute',
                    {'sourceReadGrant': grants['sourceReadGrant']}, refs=run.core.refs(resource)))
        self.denied('denied', lambda: run.call(self.directory, 'job.run', grants,
                    identity='reader', refs=run.core.refs(resource)))

    def test_05_recovery_after_completed_extraction(self):
        resource, grants, permission = self.fixture()
        self.processes.stop('knowledge.local')
        try:
            self.denied('unavailable', lambda: self.execute(resource, grants, 'key.recovery'))
        finally:
            self.processes.start('knowledge.local')
        from farmy_transport.local import digest
        job_id = 'job.' + digest({'owner':'owner', 'key':'key.recovery'})
        before = run.call(self.directory, 'job.inspect', {'jobId':job_id})
        self.assertEqual(before['status'], 'extracted')
        self.processes.stop('workflow.local')
        self.processes.start('workflow.local')
        resumed = self.execute(resource, grants, 'key.recovery')
        self.assertEqual(resumed['proposalId'], before['proposalId'])
        self.assertEqual(resumed['status'], 'succeeded')
        self.assertEqual(run.query(self.directory, resource, permission)['value'], 'wheat')

    def test_06_ambiguous_malformed_and_oversized_reports(self):
        for index, data in enumerate([b'crop: wheat\ncrop: barley\n', b'no field\n', b'crop: WHEAT\n',
                                     b'crop: wheat\n\xff', b'x'*16385]):
            with self.subTest(index=index):
                resource, grants, permission = self.fixture(data)
                self.denied('invalid_request', lambda: self.execute(resource, grants, 'key.malformed.'+str(index)))
                self.denied('not_found', lambda: run.query(self.directory, resource, permission))

    def test_07_provenance_binding_and_unknown_operations(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(json.loads((ROOT / 'contracts/uc002/operations.schema.json').read_text()))
        resource, grants, permission = self.fixture()
        receipt = self.execute(resource, grants, 'key.provenance')
        sibling, sibling_grants, sibling_permission = self.fixture()
        workflow = run.core.config(self.directory, 'workflow.local')
        body = request(workflow, 'knowledge.local', 'evidence.index',
                       {'proposalId':receipt['proposalId'], 'disclosureGrant':sibling_grants['disclosureGrant']},
                       refs=run.core.refs(sibling), grant=sibling_grants['indexGrant'])
        self.denied('denied', lambda: exchange(workflow, 'knowledge.local', body))
        self.denied('not_found', lambda: run.query(self.directory, sibling, sibling_permission))
        self.denied('unsupported', lambda: exchange(workflow, 'knowledge.local', dict(body, contractVersion='0.1-draft')))
        bad = dict(body, payload=dict(body['payload'], value='forged'))
        self.denied('invalid_request', lambda: exchange(workflow, 'knowledge.local', bad))
        owner = run.core.config(self.directory)
        self.denied('unsupported', lambda: exchange(owner, 'knowledge.local',
                    request(owner, 'knowledge.local', 'not.supported', {})))
        for service in run.SERVICES:
            info = exchange(owner, service, path='/farmy/v0/descriptor')
            for kind in ('module','instance'):
                schema_check(FOUNDATION, kind, info[kind])
            names = [item['capabilityId'] for item in info['module']['capabilities']]
            self.assertEqual(len(names), len(set(names)))

    def test_08_lost_index_response_is_reconciled(self):
        resource, grants, permission = self.fixture()
        # Simulate a lost acknowledgement at the public boundary: pre-deliver both
        # steps using exactly the keys a retrying workflow will use.
        from farmy_transport.local import digest
        job = 'job.' + digest({'owner':'owner', 'key':'key.lost-response'})
        workflow = run.core.config(self.directory, 'workflow.local')
        computed = exchange(workflow, 'processing.local', request(workflow, 'processing.local', 'extraction.compute',
                      {'sourceReadGrant':grants['sourceReadGrant']}, refs=run.core.refs(resource),
                      grant='grant.workflow-extract', subject='owner', key='extract.'+job))
        accepted = exchange(workflow, 'knowledge.local', request(workflow, 'knowledge.local', 'evidence.index',
                      {'proposalId':computed['proposalId'], 'disclosureGrant':grants['disclosureGrant']},
                      refs=run.core.refs(resource), grant=grants['indexGrant'], key='index.'+job))
        retried = self.execute(resource, grants, 'key.lost-response')
        self.assertEqual(retried['proposalId'], accepted['proposalId'])
        self.assertEqual(run.query(self.directory, resource, permission)['value'], 'wheat')

    def test_09_existing_wallet_state_upgrade(self):
        with tempfile.TemporaryDirectory(prefix='farmy-upgrade-') as directory:
            directory = run.core.bootstrap(directory)
            with run.core.Processes(directory) as processes:
                resource = run.core.call(directory, 'resource.register', {'path':'record.txt'})
                permission = run.core.grant(directory, resource)
                processes.stop('wallet.local')
                # UC-001 schema is identical except for the new additive table.
                with sqlite3.connect(directory / 'state-wallet.local/wallet.sqlite') as db:
                    db.execute('DROP TABLE permissions')
                processes.start('wallet.local')
                self.assertEqual(run.core.read(directory, resource, permission), run.core.V1)
                self.assertEqual(run.core.call(directory, 'resource.inspect', {'resourceId':resource['resourceId']}), resource)
                run.core.call(directory, 'grant.revoke', {'grantId':permission['grantId']}, revision=1)
                self.denied('denied', lambda: run.core.read(directory, resource, permission))


if __name__ == '__main__':
    unittest.main()
