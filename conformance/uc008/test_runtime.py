"""UC-008 real-process acceptance; both providers exercise the same public contracts."""
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uc008_run', ROOT / 'solutions/replacement/uc008/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from bindings import admit, resolve
from farmy_transport.http import Fault, exchange, request, utc


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-uc008-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = run.bootstrap(cls.temp.name)
        cls.processes = run.core.Processes(cls.directory, dict(run.SERVICES))
        cls.addClassCleanup(cls.processes.__exit__, None, None, None)
        cls.processes.__enter__()
        run.replace(cls.directory, cls.processes)

    def denied(self, code, action):
        with self.assertRaises(Fault) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def fixture(self, target, data=run.path.REPORT):
        name = str(time.time_ns()) + '.txt'
        (self.directory / 'source' / name).write_bytes(data)
        resource = run.core.call(self.directory, 'resource.register', {'path': name})
        grants, permission = run.permissions(self.directory, resource, target)
        run.select(self.directory, self.processes, target, 1)
        receipt = run.execute(self.directory, resource, grants, 'key.' + name)
        return resource, grants, permission, receipt

    def test_01_shared_contract_evidence_and_restart(self):
        for target in (run.A, run.B):
            with self.subTest(target=target):
                data = 'Report é\ncrop: barley\n'.encode()
                resource, grants, permission, receipt = self.fixture(target, data)
                evidence = run.bound_query(self.directory, resource, permission)
                self.assertEqual(evidence['value'], 'barley')
                self.assertEqual(evidence['source'], run.core.refs(resource)[0])
                self.assertEqual(evidence['proposalId'], receipt['proposalId'])
                self.assertEqual(data[evidence['byteStart']:evidence['byteEnd']].decode(), evidence['quote'])
                self.processes.stop(target)
                self.processes.start(target)
                self.assertEqual(run.bound_query(self.directory, resource, permission), evidence)

    def test_02_audience_and_subject_are_not_portable(self):
        for target in (run.A, run.B):
            resource, _, permission, _ = self.fixture(target)
            other = run.B if target == run.A else run.A
            self.denied('denied', lambda: run.query(self.directory, resource, permission, other))
            for identity, code in [('denied', 'denied'), ('unknown', 'unauthenticated')]:
                self.denied(code, lambda: run.query(self.directory, resource, permission, target, identity))

    def test_03_revocation_expiry_and_authority_outage(self):
        for target in (run.A, run.B):
            resource, _, permission, _ = self.fixture(target)
            run.path.call(self.directory, 'access.revoke', {'grantId': permission['grantId']}, revision=1)
            self.denied('denied', lambda: run.query(self.directory, resource, permission, target))
            short = run.path.call(self.directory, 'access.issue', {
                'resourceId': resource['resourceId'], 'versionId': resource['versionId'], 'subjectId': 'reader',
                'audience': target, 'operation': 'evidence.query', 'purpose': 'uc002.query', 'expiresAt': utc(.5)},
                refs=run.core.refs(resource))
            time.sleep(.6)
            self.denied('denied', lambda: run.query(self.directory, resource, short, target))
            fresh = run.path.scoped(self.directory, resource, 'reader', target, 'evidence.query', 'uc002.query')
            self.processes.stop('wallet.local')
            try:
                self.denied('unavailable', lambda: run.query(self.directory, resource, fresh, target))
            finally:
                self.processes.start('wallet.local')

    def test_04_binding_change_conflicts_with_existing_job(self):
        resource, grants, _, receipt = self.fixture(run.A)
        key = 'key.pinned'
        run.execute(self.directory, resource, grants, key)
        run.select(self.directory, self.processes, run.A, 2)
        self.denied('conflict', lambda: run.execute(self.directory, resource, grants, key))
        run.select(self.directory, self.processes, run.B, 3)
        self.denied('conflict', lambda: run.execute(self.directory, resource, grants, key))
        # A new binding cannot turn an A permission into a B permission.
        self.denied('denied', lambda: run.execute(self.directory, resource, grants, 'key.bad-audience'))

    def test_05_admission_rejects_mismatched_declarations(self):
        config = run.core.config(self.directory)
        good = exchange(config, run.B, path='/farmy/v0/descriptor')
        self.assertEqual(admit(config, run.binding(run.B)), run.B)
        variants = []
        for field, value in [('instanceId', run.A), ('environmentId', 'environment.other'),
                             ('implementationVersion', '9.0.0'), ('peerIdentity', 'urn:farmy:identity:other')]:
            candidate = json.loads(json.dumps(good))
            candidate['instance'][field] = value
            variants.append(candidate)
        for field, value in [('contractVersion', '0.1-draft'), ('operations', ['evidence.query'])]:
            candidate = json.loads(json.dumps(good))
            candidate['module']['capabilities'][0][field] = value
            variants.append(candidate)
        for candidate in variants:
            with patch('farmy_transport.http.exchange', return_value=candidate):
                self.denied('unsupported', lambda: admit(config, run.binding(run.B)))
        self.denied('unsupported', lambda: admit(config, dict(run.binding(run.B), requiredFeatures=['unknown-feature'])))
        self.denied('unsupported', lambda: resolve(self.directory / 'knowledge-binding.json',
                    'wallet.other', 'farmy.knowledge', 'evidence.query', '0.2-draft'))

    def test_06_idempotency_and_exact_version_for_both(self):
        for target in (run.A, run.B):
            resource, grants, permission, receipt = self.fixture(target)
            config = run.core.config(self.directory, 'workflow.local')
            body = request(config, target, 'evidence.index',
                           {'proposalId': receipt['proposalId'], 'disclosureGrant': grants['disclosureGrant']},
                           refs=run.core.refs(resource), grant=grants['indexGrant'], key='key.concurrent')
            with ThreadPoolExecutor(max_workers=3) as pool:
                results = list(pool.map(lambda _: exchange(config, target, body), range(3)))
            self.assertTrue(all(r == {'proposalId': receipt['proposalId']} for r in results))
            new_disclosure = run.path.scoped(self.directory, resource, target, 'processing.local', 'extraction.get', 'uc002.index')
            changed = dict(body, payload=dict(body['payload'], disclosureGrant=new_disclosure['grantId']))
            self.denied('conflict', lambda: exchange(config, target, changed))
            (self.directory / 'source' / resource['path']).write_bytes(b'crop: oats\n')
            updated = run.core.call(self.directory, 'resource.update', {'resourceId': resource['resourceId']},
                                   refs=run.core.refs(resource), revision=resource['revision'])
            self.denied('denied', lambda: run.query(self.directory, updated, permission, target))
            self.assertEqual(run.query(self.directory, resource, permission, target)['value'], 'wheat')

    def test_07_no_cross_instance_data_and_unavailable_isolation(self):
        resource, _, permission, _ = self.fixture(run.A)
        _, other_permission = run.permissions(self.directory, resource, run.B)
        self.denied('not_found', lambda: run.query(self.directory, resource, other_permission, run.B))
        self.processes.stop(run.B)
        try:
            self.assertEqual(run.query(self.directory, resource, permission, run.A)['value'], 'wheat')
            self.denied('unavailable', lambda: run.query(self.directory, resource, other_permission, run.B))
        finally:
            self.processes.start(run.B)

    def test_08_monitor_reports_distinct_implementations_and_dependency(self):
        run.select(self.directory, self.processes, run.B, 4)
        state = run.monitor.bridge.snapshot(run.core.config(self.directory, 'monitor.local'))
        nodes = {node['instanceId']: node for node in state['nodes']}
        self.assertEqual(len(nodes), 6)
        self.assertTrue(all(n['status'] == 'available' for n in nodes.values()))
        info_a = exchange(run.core.config(self.directory), run.A, path='/farmy/v0/descriptor')
        info_b = exchange(run.core.config(self.directory), run.B, path='/farmy/v0/descriptor')
        self.assertNotEqual(info_a['module']['implementationId'], info_b['module']['implementationId'])
        self.assertEqual(info_a['module']['capabilities'], info_b['module']['capabilities'])

    def test_09_replacement_and_public_rebuild(self):
        with tempfile.TemporaryDirectory(prefix='farmy-uc008-rebuild-') as temp:
            directory = run.bootstrap(temp)
            with run.core.Processes(directory, dict(run.SERVICES)) as processes:
                run.exercise(directory, processes)
                # Test-only check: old state still exists; composition never reads it.
                self.assertTrue((directory / 'state-knowledge.secondary/state.sqlite').is_file())
                self.assertTrue((directory / 'state-ledger-secondary/state.sqlite').is_file())

    def test_10_disclosure_permission_and_source_provenance(self):
        for target in (run.A, run.B):
            resource, grants, permission, receipt = self.fixture(target)
            config = run.core.config(self.directory, 'workflow.local')
            body = request(config, target, 'evidence.index',
                           {'proposalId': receipt['proposalId'], 'disclosureGrant': grants['indexGrant']},
                           refs=run.core.refs(resource), grant=grants['indexGrant'], key='key.no-disclosure')
            self.denied('denied', lambda: exchange(config, target, body))
            sibling, sibling_grants, sibling_permission, _ = self.fixture(target, b'crop: oats\n')
            body = request(config, target, 'evidence.index',
                           {'proposalId': receipt['proposalId'], 'disclosureGrant': sibling_grants['disclosureGrant']},
                           refs=run.core.refs(sibling), grant=sibling_grants['indexGrant'], key='key.wrong-source')
            self.denied('denied', lambda: exchange(config, target, body))
            self.assertEqual(run.query(self.directory, sibling, sibling_permission, target)['value'], 'oats')

    def test_11_interrupted_job_cannot_be_redirected(self):
        resource, grants, permission, _ = self.fixture(run.B)
        self.processes.stop(run.B)
        try:
            self.denied('unavailable', lambda: run.execute(self.directory, resource, grants, 'key.interrupted'))
            run.select(self.directory, self.processes, run.A, 2)
            self.denied('conflict', lambda: run.execute(self.directory, resource, grants, 'key.interrupted'))
        finally:
            self.processes.start(run.B)
            run.select(self.directory, self.processes, run.B, 1)
        result = run.execute(self.directory, resource, grants, 'key.interrupted')
        self.assertEqual(result['status'], 'succeeded')
        self.assertEqual(run.bound_query(self.directory, resource, permission)['value'], 'wheat')


if __name__ == '__main__':
    unittest.main()
