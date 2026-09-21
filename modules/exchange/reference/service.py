"""Bounded, approved exact-document disclosure to configured synthetic recipients."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import time

from farmy_transport.http import Fault, descriptor, serve, timestamp
from farmy_transport.local import LocalService, digest
from farmy_transport.monitoring import summarize


class Exchange(LocalService):
    dependencies = ('wallet.local', 'connector.local')
    schema = '''CREATE TABLE IF NOT EXISTS disclosures
        (id TEXT PRIMARY KEY, actor TEXT NOT NULL, input TEXT NOT NULL,
         preview TEXT NOT NULL, source_grant TEXT NOT NULL, approval TEXT, receipt TEXT, approval_grant TEXT);
        CREATE TABLE IF NOT EXISTS requests
        (actor TEXT, operation TEXT, key TEXT, input TEXT NOT NULL,
         PRIMARY KEY(actor,operation,key));
        CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, status TEXT NOT NULL);'''

    def __init__(self, config):
        super().__init__(config)
        self.dependencies = ('wallet.local', 'connector.local', *config['recipients'])

    def descriptor(self):
        return descriptor(self.config, 'exchange',
            {'farmy.disclosure': ['disclosure.prepare', 'disclosure.approve', 'disclosure.deliver']},
            {'farmy.permissions': ['access.check'], 'farmy.storage': ['read.version'],
             'farmy.disclosure': ['disclosure.receive']})

    def monitoring_summary(self):
        return summarize(self, [('Prepared disclosures', 'SELECT count(*) FROM disclosures'),
            ('Approved disclosures', 'SELECT count(*) FROM disclosures WHERE approval IS NOT NULL'),
            ('Acknowledged deliveries', 'SELECT count(*) FROM disclosures WHERE receipt IS NOT NULL'),
            ('Unconfirmed deliveries', "SELECT count(*) FROM attempts WHERE status='unconfirmed'")],
            self.dependencies)

    def owner(self, peer, body):
        if peer != 'owner' or body['subjectId'] != peer or len(body['inputRefs']) != 1:
            raise Fault('denied')

    def content(self, body, grant):
        raw = self.remote('connector.local', 'read.version', {}, body, grant=grant)
        if len(raw) > 16384:
            raise Fault('unsupported')
        return raw

    def remember(self, db, peer, body):
        logical = digest({k: body[k] for k in ('payload', 'inputRefs', 'grantRef', 'purpose')})
        args = (peer, body['operation'], body['idempotencyKey'])
        old = db.execute('SELECT input FROM requests WHERE actor=? AND operation=? AND key=?', args).fetchone()
        if old and old['input'] != logical:
            raise Fault('conflict')
        db.execute('INSERT OR IGNORE INTO requests VALUES(?,?,?,?)', (*args, logical))

    def handle(self, peer, body):
        op, payload = body['operation'], body['payload']
        if op not in ('disclosure.prepare', 'disclosure.approve', 'disclosure.deliver'):
            raise Fault('unsupported')
        if op == 'disclosure.prepare':
            self.owner(peer, body)
            if body['grantRef'] != 'grant.owner-bootstrap':
                raise Fault('denied')
            recipient = payload['recipientId']
            if recipient not in self.config['recipients']:
                raise Fault('denied')
            raw = self.content(body, payload['sourceReadGrant'])
            identifier = 'disclosure.' + digest({'actor': peer, 'key': body['idempotencyKey']})
            manifest = {'disclosureId': identifier, 'source': body['inputRefs'][0],
                        'recipientId': recipient, 'recipientFingerprint': self.config['endpoints'][recipient]['fingerprint'],
                        'purpose': payload['purpose'],
                        'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw)}
            result = {'manifest': manifest, 'manifestHash': digest(manifest),
                      'contentBase64': base64.b64encode(raw).decode()}
            self.deadline(body)
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE')
                self.remember(db, peer, body)
                old = db.execute('SELECT preview FROM disclosures WHERE id=?', (identifier,)).fetchone()
                if old and json.loads(old['preview']) != result:
                    raise Fault('conflict')
                db.execute('INSERT OR IGNORE INTO disclosures VALUES(?,?,?,?,?,NULL,NULL,NULL)',
                           (identifier, peer, digest(payload), json.dumps(result), payload['sourceReadGrant']))
                self.event(db, peer, op, 'prepared')
            return result

        self.access(peer, body)
        if op == 'disclosure.approve':
            self.owner(peer, body)
        identifier = payload['manifest']['disclosureId']
        # Commit the intent before sending. The recipient deduplicates concurrent retries
        # and a resend after a process crash before the local receipt commit.
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM disclosures WHERE id=?', (identifier,)).fetchone()
            if row is None:
                raise Fault('not_found')
            preview = json.loads(row['preview'])
            manifest = preview['manifest']
            if (payload['manifest'] != manifest or payload['manifestHash'] != preview['manifestHash']
                    or body['inputRefs'] != [manifest['source']]):
                raise Fault('conflict')
            if (manifest['recipientId'] not in self.config['recipients']
                    or manifest['recipientFingerprint'] != self.config['endpoints'][manifest['recipientId']]['fingerprint']):
                raise Fault('denied')
            self.remember(db, peer, body)
            raw = self.content(body, row['source_grant'])
            if base64.b64encode(raw).decode() != preview['contentBase64']:
                raise Fault('conflict')
            if op == 'disclosure.approve':
                expires = timestamp(payload['expiresAt'])
                if not time.time() < expires <= time.time() + 600:
                    raise Fault('expired')
                result = {'disclosureId': identifier, 'manifestHash': preview['manifestHash'],
                          'expiresAt': payload['expiresAt'], 'status': 'approved'}
                if row['approval'] and json.loads(row['approval']) != result:
                    raise Fault('conflict')
                self.access(peer, body)
                self.deadline(body)
                db.execute('UPDATE disclosures SET approval=?,approval_grant=? WHERE id=?',
                           (json.dumps(result), body['grantRef'], identifier))
                self.event(db, peer, op, 'approved')
                return result
            if row['approval'] is None:
                raise Fault('denied')
            self.remote('wallet.local', 'access.check',
                        {'operation': 'disclosure.approve', 'purpose': 'uc006.approve'}, body,
                        subject=row['actor'], grant=row['approval_grant'])
            approval = json.loads(row['approval'])
            if timestamp(approval['expiresAt']) <= time.time():
                raise Fault('expired')
            self.access(peer, body)
            self.deadline(body)
            if row['receipt']:
                self.event(db, peer, op, 'replayed')
                return json.loads(row['receipt'])
            db.execute("INSERT OR IGNORE INTO attempts VALUES(?,'unconfirmed')", (identifier,))
            self.event(db, peer, op, 'unconfirmed')
        # This journal state intentionally survives an unavailable/malformed response.
        self.access(peer, body)
        self.deadline(body)
        if timestamp(approval['expiresAt']) <= time.time():
            raise Fault('expired')
        result = self.remote(manifest['recipientId'], 'disclosure.receive', preview, body,
                             grant='grant.configured-sender', key=identifier)
        if (result['disclosureId'] != identifier or result['manifestHash'] != preview['manifestHash']
                or result['recipientId'] != manifest['recipientId'] or result['status'] != 'received'):
            raise Fault('conflict')
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT receipt FROM disclosures WHERE id=?', (identifier,)).fetchone()
            if old['receipt'] and json.loads(old['receipt']) != result:
                raise Fault('conflict')
            db.execute('UPDATE disclosures SET receipt=? WHERE id=?', (json.dumps(result), identifier))
            db.execute("UPDATE attempts SET status='received' WHERE id=?", (identifier,))
            self.event(db, peer, op, 'received')
        return result



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Exchange(json.loads(Path(parser.parse_args().config).read_text())))
