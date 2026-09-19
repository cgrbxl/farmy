"""UC-003 acceptance checks at real HTTPS service boundaries."""
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
spec = importlib.util.spec_from_file_location('uc003_run', ROOT / 'solutions/sensor-path/uc003/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from farmy_transport.http import Fault, FOUNDATION, exchange, request, schema_check, utc


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-uc003-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = run.bootstrap(cls.temp.name)
        cls.processes = run.core.Processes(cls.directory, run.SERVICES)
        cls.addClassCleanup(cls.processes.__exit__, None, None, None)
        cls.processes.__enter__()

    def denied(self, code, action):
        with self.assertRaises(Fault) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def fixture(self):
        source = run.register(self.directory)
        observation = run.append(self.directory, source, 18.0)
        permission = run.grant(self.directory, source)
        return source, observation, permission

    def test_01_one_grant_covers_history_and_future_with_pagination(self):
        source, first, permission = self.fixture()
        second = run.append(self.directory, source, 19.0)
        third = run.append(self.directory, source, 20.0)
        page = run.read(self.directory, source, permission, limit=1)
        self.assertEqual(page['observations'], [first])
        page = run.read(self.directory, source, permission, after=first['sequence'], limit=1)
        self.assertEqual(page['observations'], [second])
        self.assertEqual(run.read(self.directory, source, permission, after=second['sequence'])['observations'], [third])
        self.assertEqual(run.read(self.directory, source, permission, after=third['sequence'])['observations'], [])
        with sqlite3.connect(self.directory / 'state-wallet.local/wallet.sqlite') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM source_grants WHERE source=?', (source['sourceId'],)).fetchone()[0], 1)

    def test_02_source_owner_consumer_and_audience_isolation(self):
        source, _, permission = self.fixture()
        separate, _, _ = self.fixture()
        self.denied('denied', lambda: run.read(self.directory, separate, permission))
        for identity, code in [('denied','denied'), ('owner','denied'), ('unknown','unauthenticated')]:
            self.denied(code, lambda: run.read(self.directory, source, permission, identity))
        reader = run.core.config(self.directory, 'reader')
        body = request(reader, 'sensor.local', 'sensor.read', dict(run.scope(source), afterSequence=0, limit=10),
                       grant=permission['grantId'])
        for field, value in [('actorId','owner'), ('subjectId','owner'), ('walletId','wallet.other'),
                             ('targetInstanceId','wallet.local'), ('purpose','uc003.manage')]:
            self.denied('denied', lambda: exchange(reader, 'sensor.local', dict(body, **{field:value})))
        self.denied('denied', lambda: run.read(self.directory, dict(source, ownerId='denied'), permission))
        self.denied('denied', lambda: run.call(self.directory, 'source.grant',
                   dict(run.scope(source), consumerId='reader', expiresAt=utc(600)), identity='denied'))
        wrong_audience = run.core.config(self.directory, 'connector.local')
        self.denied('denied', lambda: exchange(wrong_audience, 'wallet.local',
            request(wrong_audience, 'wallet.local', 'source.authorize', dict(run.scope(source), action='read'),
                    grant=permission['grantId'], subject='reader')))
        self.denied('denied', lambda: run.call(self.directory, 'source.authorize',
                    dict(run.scope(source), action='read'), identity='reader', grant=permission['grantId']))

    def test_03_append_membership_and_duplicates(self):
        source = run.register(self.directory)
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda _: run.append(self.directory, source, 18.0, 'key.concurrent'), range(3)))
        self.assertTrue(all(value == results[0] for value in results))
        self.denied('conflict', lambda: run.append(self.directory, source, 19.0, 'key.concurrent'))
        separate = run.register(self.directory)
        self.denied('conflict', lambda: run.append(self.directory, separate, 18.0, 'key.concurrent'))
        payload = dict(run.scope(source), observedAt=utc(), value=15, unit='degC')
        self.denied('denied', lambda: run.call(self.directory, 'sensor.append', payload, identity='reader'))
        self.denied('denied', lambda: run.call(self.directory, 'sensor.append', dict(payload, ownerId='denied')))
        self.denied('invalid_request', lambda: run.call(self.directory, 'sensor.append',
                    dict(payload, observationId=results[0]['observationId'])))
        self.assertEqual(len(run.read(self.directory, source, run.grant(self.directory, source))['observations']), 1)

    def test_04_revocation_expiry_and_unavailable_authority(self):
        source, _, permission = self.fixture()
        run.call(self.directory, 'source.revoke', {'grantId':permission['grantId']}, revision=1)
        self.denied('denied', lambda: run.read(self.directory, source, permission))
        self.denied('conflict', lambda: run.call(self.directory, 'source.revoke', {'grantId':permission['grantId']}, revision=1))
        short = run.grant(self.directory, source, seconds=.5)
        time.sleep(.6)
        self.denied('denied', lambda: run.read(self.directory, source, short))
        fresh = run.grant(self.directory, source)
        self.processes.stop('wallet.local')
        try:
            start = time.monotonic()
            self.denied('unavailable', lambda: run.read(self.directory, source, fresh))
            self.assertLess(time.monotonic() - start, 5)
            self.denied('unavailable', lambda: run.append(self.directory, source, 20))
        finally:
            self.processes.start('wallet.local')
        self.assertEqual(len(run.read(self.directory, source, fresh)['observations']), 1)

    def test_05_traceability_and_audit_privacy(self):
        source, observation, permission = self.fixture()
        read = run.read(self.directory, source, permission)
        receipts = run.audit(self.directory, source)
        receipt = next(r for r in receipts if r['deliveryId'] == read['deliveryId'])
        self.assertEqual(receipt['sourceId'], source['sourceId'])
        self.assertEqual(receipt['ownerId'], source['ownerId'])
        self.assertEqual(receipt['consumerId'], 'reader')
        self.assertEqual(receipt['grantId'], permission['grantId'])
        self.assertEqual(receipt['decisionRevision'], 1)
        self.assertEqual(receipt['event'], 'release_authorized')
        digest = hashlib.sha256(json.dumps(observation, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(receipt['observations'], [{'observationId':observation['observationId'],
                        'sequence':observation['sequence'], 'sha256':digest}])
        self.denied('denied', lambda: run.call(self.directory, 'sensor.audit',
                    dict(run.scope(source), limit=10), identity='reader', grant=permission['grantId']))
        self.denied('denied', lambda: run.read(self.directory, source, permission, 'denied'))
        self.assertEqual(len(run.audit(self.directory, source)), len(receipts))
        with sqlite3.connect(self.directory / 'state-sensor.local/state.sqlite') as db:
            self.assertGreater(db.execute("SELECT count(*) FROM audit WHERE actor='denied' AND outcome='denied'").fetchone()[0], 0)

    def test_06_restart_preserves_all_state(self):
        source, first, permission = self.fixture()
        delivered = run.read(self.directory, source, permission)
        for service in ('wallet.local','sensor.local'):
            self.processes.stop(service)
            self.processes.start(service)
        self.assertEqual(run.read(self.directory, source, permission)['observations'], [first])
        self.assertTrue(any(r['deliveryId'] == delivered['deliveryId'] for r in run.audit(self.directory, source)))
        second = run.append(self.directory, source, 20)
        self.assertEqual(second['sequence'], first['sequence'] + 1)
        run.call(self.directory, 'source.revoke', {'grantId':permission['grantId']}, revision=1)
        self.processes.stop('wallet.local')
        self.processes.start('wallet.local')
        self.denied('denied', lambda: run.read(self.directory, source, permission))

    def test_07_corrupted_membership_and_audit_failure_fail_closed(self):
        source, observation, permission = self.fixture()
        path = self.directory / 'state-sensor.local/state.sqlite'
        # Simulate corrupt storage. This is test-only inspection, not service integration.
        with sqlite3.connect(path) as db:
            db.execute('UPDATE observations SET result=? WHERE id=?',
                       (json.dumps(dict(observation, sourceId='source.other')), observation['observationId']))
        self.denied('unavailable', lambda: run.read(self.directory, source, permission))
        self.assertEqual(run.audit(self.directory, source), [])
        with sqlite3.connect(path) as db:
            db.execute('UPDATE observations SET result=? WHERE id=?', (json.dumps(observation), observation['observationId']))
            db.execute("CREATE TRIGGER reject_delivery BEFORE INSERT ON deliveries BEGIN SELECT RAISE(ABORT, 'test failure'); END")
        try:
            self.denied('internal', lambda: run.read(self.directory, source, permission))
        finally:
            with sqlite3.connect(path) as db:
                db.execute('DROP TRIGGER reject_delivery')
        self.assertEqual(run.audit(self.directory, source), [])

    def test_08_contract_limits_and_descriptors(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(json.loads((ROOT / 'contracts/uc003/operations.schema.json').read_text()))
        source, _, permission = self.fixture()
        reader = run.core.config(self.directory, 'reader')
        body = request(reader, 'sensor.local', 'sensor.read', dict(run.scope(source), afterSequence=0, limit=100),
                       grant=permission['grantId'])
        self.denied('unsupported', lambda: exchange(reader, 'sensor.local', dict(body, contractVersion='0.2-draft')))
        self.denied('expired', lambda: exchange(reader, 'sensor.local', dict(body, deadline=utc(-1))))
        for change in [{'limit':101}, {'afterSequence':-1}, {'observationId':'observation.other'}]:
            self.denied('invalid_request', lambda: exchange(reader, 'sensor.local', dict(body, payload=dict(body['payload'], **change))))
        for field, value in [('unit','fahrenheit'), ('value',81), ('observedAt','not-a-time')]:
            payload = dict(run.scope(source), observedAt=utc(), value=18.0, unit='degC')
            self.denied('invalid_request', lambda: run.call(self.directory, 'sensor.append', dict(payload, **{field:value})))
        owner = run.core.config(self.directory)
        for service in run.SERVICES:
            info = exchange(owner, service, path='/farmy/v0/descriptor')
            for kind in ('module','instance'):
                schema_check(FOUNDATION, kind, info[kind])
        self.assertEqual(info['module']['implementationId'], 'farmy.reference.synthetic-sensor')

    def test_09_additive_wallet_upgrade_preserves_document_grants(self):
        with tempfile.TemporaryDirectory(prefix='farmy-source-upgrade-') as directory:
            directory = run.core.bootstrap(directory)
            config_path = directory / 'wallet.local.json'
            old_config = json.loads(config_path.read_text())
            old_config['implementationVersion'] = '0.2.0'
            config_path.write_text(json.dumps(old_config))
            with run.core.Processes(directory) as processes:
                resource = run.core.call(directory, 'resource.register', {'path':'record.txt'})
                permission = run.core.grant(directory, resource)
                processes.stop('wallet.local')
                with sqlite3.connect(directory / 'state-wallet.local/wallet.sqlite') as db:
                    db.execute('DROP TABLE source_grants')
                    db.execute('DROP TABLE sources')
                processes.start('wallet.local')
                info = exchange(run.core.config(directory), 'wallet.local', path='/farmy/v0/descriptor')
                self.assertEqual(info['instance']['implementationVersion'], '0.3.0')
                self.assertEqual(run.core.read(directory, resource, permission), run.core.V1)
                self.assertEqual(run.core.call(directory, 'resource.inspect', {'resourceId':resource['resourceId']}), resource)
                run.core.call(directory, 'grant.revoke', {'grantId':permission['grantId']}, revision=1)
                self.denied('denied', lambda: run.core.read(directory, resource, permission))


if __name__ == '__main__':
    unittest.main()
