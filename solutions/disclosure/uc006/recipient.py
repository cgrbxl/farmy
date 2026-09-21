"""Synthetic external recipient fixture, not a production delivery adapter."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from farmy_transport.http import Fault, descriptor, fingerprint, serve, utc
from farmy_transport.local import LocalService, digest


class Recipient(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS receipts
        (id TEXT PRIMARY KEY, manifest_hash TEXT NOT NULL, content TEXT NOT NULL, result TEXT NOT NULL);'''

    def descriptor(self):
        return descriptor(self.config, 'exchange', {'farmy.disclosure': ['disclosure.receive', 'receipt.inspect']}, {})

    def handle(self, peer, body):
        op, payload = body['operation'], body['payload']
        if op == 'receipt.inspect':
            if peer != 'owner' or body['subjectId'] != peer or body['grantRef'] != 'grant.owner-bootstrap':
                raise Fault('denied')
            with self.db() as db:
                row = db.execute('SELECT * FROM receipts WHERE id=?', (payload['disclosureId'],)).fetchone()
                if row is None:
                    raise Fault('not_found')
                return {'receipt': json.loads(row['result']), 'contentBase64': row['content']}
        if op != 'disclosure.receive':
            raise Fault('unsupported')
        if peer != 'exchange.local' or body['subjectId'] != peer or body['grantRef'] != 'grant.configured-sender':
            raise Fault('denied')
        manifest = payload['manifest']
        raw = base64.b64decode(payload['contentBase64'], validate=True)
        if (manifest['recipientId'] != self.config['identity']
                or manifest['recipientFingerprint'] != fingerprint(self.config['cert']) or body['inputRefs'] != [manifest['source']]
                or body['idempotencyKey'] != manifest['disclosureId']
                or digest(manifest) != payload['manifestHash']
                or hashlib.sha256(raw).hexdigest() != manifest['sha256'] or len(raw) != manifest['size']):
            raise Fault('conflict')
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT * FROM receipts WHERE id=?', (manifest['disclosureId'],)).fetchone()
            if old:
                if old['manifest_hash'] != payload['manifestHash'] or old['content'] != payload['contentBase64']:
                    raise Fault('conflict')
                return json.loads(old['result'])
            result = {'disclosureId': manifest['disclosureId'], 'manifestHash': payload['manifestHash'],
                      'recipientId': self.config['identity'], 'status': 'received', 'receivedAt': utc()}
            self.deadline(body)
            db.execute('INSERT INTO receipts VALUES(?,?,?,?)', (manifest['disclosureId'], payload['manifestHash'],
                       payload['contentBase64'], json.dumps(result)))
            self.event(db, peer, op, 'received')
        # Explicit fixture mode: persist first, then simulate losing its acknowledgement.
        if self.config.get('simulateLostAcknowledgement'):
            raise Fault('unavailable')
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Recipient(json.loads(Path(parser.parse_args().config).read_text())))
