"""Controlled disclosure across real mTLS services and a separate recipient."""
import base64
import copy
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uc006_run', ROOT / 'solutions/disclosure/uc006/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from farmy_transport.http import Fault, exchange, request, utc
from farmy_transport.local import digest


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-disclosure-test-')
        cls.directory = run.bootstrap(cls.temp.name)
        cls.processes = run.core.Processes(cls.directory, run.SERVICES)
        cls.processes.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.processes.__exit__(None, None, None)
        cls.temp.cleanup()

    def fixture(self, approve=True):
        (self.directory / 'source/record.txt').write_bytes(run.core.V1)
        resource, read, preview, approval, delivery = run.prepare(self.directory)
        if approve:
            run.approve(self.directory, resource, preview, approval)
        return resource, read, preview, approval, delivery

    def fault(self, code, action):
        with self.assertRaises(Fault) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def send(self, fixture, **kwargs):
        r, _, p, _, g = fixture
        return run.deliver(self.directory, r, p, g, **kwargs)

    def inspect(self, preview):
        return run.call(self.directory, 'receipt.inspect', {'disclosureId': preview['manifest']['disclosureId']})

    def summary(self):
        result = exchange(run.core.config(self.directory, 'monitor.local'), 'exchange.local', path='/farmy/v0/monitor/summary')
        return {c['label']: c['value'] for c in result['counts']}

    def test_01_exact_preview_and_durable_receipt(self):
        f = self.fixture()
        self.assertEqual(base64.b64decode(f[2]['contentBase64']), run.core.V1)
        self.assertEqual(f[2]['manifestHash'], digest(f[2]['manifest']))
        receipt = self.send(f)
        for name in ('exchange.local', 'recipient.local'):
            self.processes.stop(name)
            self.processes.start(name)
        self.assertEqual(self.send(f), receipt)
        self.assertEqual(self.inspect(f[2]), {'receipt': receipt, 'contentBase64': f[2]['contentBase64']})

    def test_02_missing_approval_and_separate_export_permissions(self):
        f = self.fixture(False)
        r, read, preview, approval, delivery = f
        self.fault('denied', lambda: self.send(f))
        self.fault('denied', lambda: run.approve(self.directory, r, preview, read))
        run.approve(self.directory, r, preview, approval)
        for grant in (read, approval, {'grantId': 'permission.missing'}):
            self.fault('denied', lambda: run.deliver(self.directory, r, preview, grant))
        self.fault('not_found', lambda: self.inspect(preview))

    def test_03_changed_manifest_never_delivers(self):
        r, _, preview, approval, delivery = self.fixture()
        for key, value in [('recipientId', 'other.local'), ('sha256', '0'*64), ('size', 1), ('recipientFingerprint', '0'*64),
                           ('source', dict(preview['manifest']['source'], versionId='version.other'))]:
            changed = copy.deepcopy(preview)
            changed['manifest'][key] = value
            changed['manifestHash'] = digest(changed['manifest'])
            self.fault('conflict', lambda: run.deliver(self.directory, r, changed, delivery))
            self.fault('conflict', lambda: run.approve(self.directory, r, changed, approval))
        changed = copy.deepcopy(preview)
        changed['manifest']['purpose'] = 'unapproved.purpose'
        self.fault('invalid_request', lambda: run.deliver(self.directory, r, changed, delivery))
        self.fault('not_found', lambda: self.inspect(preview))

    def test_04_subject_binding_and_unenrolled_callers(self):
        f = self.fixture()
        for identity, code in [('reader', 'denied'), ('denied', 'denied'), ('unknown', 'unauthenticated')]:
            self.fault(code, lambda: self.send(f, identity=identity))
        config = run.core.config(self.directory, 'reader')
        body = request(config, 'exchange.local', 'disclosure.deliver', run.selection(f[2]),
                       refs=run.core.refs(f[0]), grant=f[4]['grantId'], subject='owner')
        self.fault('denied', lambda: exchange(config, 'exchange.local', body))
        self.fault('denied', lambda: self.send(f, identity='monitor.local'))

    def test_05_revoked_read_approval_or_delivery_blocks_replay(self):
        for index, operation in [(1, 'grant.revoke'), (3, 'access.revoke'), (4, 'access.revoke')]:
            f = self.fixture()
            self.send(f)
            run.core.call(self.directory, operation, {'grantId': f[index]['grantId']}, revision=1)
            self.fault('denied', lambda: self.send(f))
            self.assertEqual(base64.b64decode(self.inspect(f[2])['contentBase64']), run.core.V1)

    def test_06_unavailable_authority_or_source_fails_closed(self):
        f = self.fixture()
        for target in ('wallet.local', 'connector.local'):
            self.processes.stop(target)
            try:
                self.fault('unavailable', lambda: self.send(f))
            finally:
                self.processes.start(target)
        self.fault('not_found', lambda: self.inspect(f[2]))

    def test_07_recipient_outage_records_uncertainty_then_recovers(self):
        f = self.fixture()
        before = self.summary()['Unconfirmed deliveries']
        self.processes.stop('recipient.local')
        try:
            self.fault('unavailable', lambda: self.send(f, key='key.outage'))
            self.processes.stop('exchange.local')
            self.processes.start('exchange.local')
            self.assertEqual(self.summary()['Unconfirmed deliveries'], before + 1)
        finally:
            self.processes.start('recipient.local')
        receipt = self.send(f, key='key.outage')
        self.assertEqual(self.send(f, key='key.outage'), receipt)
        self.assertEqual(self.summary()['Unconfirmed deliveries'], before)

    def test_08_lost_acknowledgement_survives_both_restarts(self):
        f = self.fixture()
        path = self.directory / 'recipient.local.json'
        config = json.loads(path.read_text())
        path.write_text(json.dumps(dict(config, simulateLostAcknowledgement=True)))
        self.processes.stop('recipient.local')
        self.processes.start('recipient.local')
        try:
            self.fault('unavailable', lambda: self.send(f, key='key.lost-ack'))
            accepted = self.inspect(f[2])
            for name in ('exchange.local', 'recipient.local'):
                self.processes.stop(name)
                self.processes.start(name)
            self.assertEqual(self.send(f, key='key.lost-ack'), accepted['receipt'])
            self.assertEqual(self.inspect(f[2]), accepted)
        finally:
            path.write_text(json.dumps(config))
            self.processes.stop('recipient.local')
            self.processes.start('recipient.local')

    def test_09_concurrent_delivery_and_idempotency_conflict(self):
        f = self.fixture()
        before = self.summary()['Acknowledged deliveries']
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda _: self.send(f, key='key.concurrent'), range(3)))
        self.assertTrue(all(r == results[0] for r in results))
        self.assertEqual(self.summary()['Acknowledged deliveries'], before + 1)
        other = self.fixture()
        self.fault('conflict', lambda: self.send(other, key='key.concurrent'))
        self.fault('not_found', lambda: self.inspect(other[2]))

    def test_10_source_update_does_not_replace_approved_version(self):
        f = self.fixture()
        (self.directory / 'source/record.txt').write_bytes(run.core.V2)
        updated = run.core.call(self.directory, 'resource.update', {'resourceId': f[0]['resourceId']},
                                refs=run.core.refs(f[0]), revision=1)
        self.assertNotEqual(updated['versionId'], f[0]['versionId'])
        self.send(f)
        self.assertEqual(base64.b64decode(self.inspect(f[2])['contentBase64']), run.core.V1)

    def test_11_approval_expiry_and_deadlines(self):
        r, _, p, a, g = self.fixture(False)
        payload = dict(run.selection(p), expiresAt=utc(-1))
        self.fault('expired', lambda: run.call(self.directory, 'disclosure.approve', payload,
            refs=run.core.refs(r), grant=a['grantId']))
        config = run.core.config(self.directory)
        body = request(config, 'exchange.local', 'disclosure.deliver', run.selection(p),
                       refs=run.core.refs(r), grant=g['grantId'])
        body['deadline'] = utc(-1)
        self.fault('expired', lambda: exchange(config, 'exchange.local', body))
        payload['expiresAt'] = utc(0.3)
        run.call(self.directory, 'disclosure.approve', payload, refs=run.core.refs(r), grant=a['grantId'])
        time.sleep(0.35)
        self.fault('expired', lambda: run.deliver(self.directory, r, p, g))
        self.fault('not_found', lambda: self.inspect(p))

    def test_12_recipient_checks_sender_and_exact_content(self):
        f = self.fixture()
        p = f[2]
        kwargs = dict(refs=run.core.refs(f[0]), grant='grant.configured-sender', key=p['manifest']['disclosureId'])
        self.fault('denied', lambda: run.call(self.directory, 'disclosure.receive', p, **kwargs))
        changed = copy.deepcopy(p)
        changed['contentBase64'] = base64.b64encode(b'changed').decode()
        self.fault('conflict', lambda: run.call(self.directory, 'disclosure.receive', changed,
                                               identity='exchange.local', **kwargs))
        self.fault('not_found', lambda: self.inspect(p))

    def test_13_bounded_content_and_recipient_allowlist(self):
        (self.directory / 'source/record.txt').write_bytes(b'x' * 16385)
        r = run.core.call(self.directory, 'resource.register', {'path': 'record.txt'})
        grant = run.core.grant(self.directory, r, 'exchange.local')
        payload = {'recipientId': 'recipient.local', 'purpose': 'synthetic.review', 'sourceReadGrant': grant['grantId']}
        self.fault('unsupported', lambda: run.call(self.directory, 'disclosure.prepare', payload, refs=run.core.refs(r)))
        payload['recipientId'] = 'https://external.invalid'
        self.fault('denied', lambda: run.call(self.directory, 'disclosure.prepare', payload, refs=run.core.refs(r)))
        payload['extra'] = True
        self.fault('invalid_request', lambda: run.call(self.directory, 'disclosure.prepare', payload, refs=run.core.refs(r)))

    def test_14_monitoring_descriptor_and_no_monitor_write(self):
        descriptor = exchange(run.core.config(self.directory), 'exchange.local', path='/farmy/v0/descriptor')
        self.assertEqual(descriptor['module']['family'], 'exchange')
        f = self.fixture()
        before = self.summary()['Acknowledged deliveries']
        self.send(f)
        self.assertEqual(self.summary()['Acknowledged deliveries'], before + 1)
        snapshot = run.monitor.bridge.snapshot(run.core.config(self.directory, 'monitor.local'))
        self.assertEqual(len(snapshot['nodes']), 3)
        self.assertNotIn('exchange', [item['family'] for item in snapshot['planned']])
        self.assertTrue(all(n['status'] == 'available' for n in snapshot['nodes']))
        self.assertNotIn(f[2]['contentBase64'], json.dumps(snapshot))
        self.fault('denied', lambda: exchange(run.core.config(self.directory, 'reader'),
            'exchange.local', path='/farmy/v0/monitor/summary'))


if __name__ == '__main__': unittest.main()
