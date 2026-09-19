"""Deterministic bounded text extraction. No authoritative record writes."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from farmy_transport.http import Fault, descriptor, serve
from farmy_transport.local import LocalService, digest

EXTRACTOR = 'farmy.text-field/0.1.0'


def extract(data):
    if len(data) > 16384:
        raise Fault('invalid_request')
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        raise Fault('invalid_request') from None
    matches = []
    offset = 0
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        raw = line.rstrip('\r\n')
        if raw.startswith('crop:'):
            match = re.fullmatch(r'crop: ([a-z][a-z -]{0,63})', raw)
            if match is None:
                raise Fault('invalid_request')
            matches.append({'field': 'crop', 'value': match[1], 'quote': raw, 'line': number,
                            'byteStart': offset, 'byteEnd': offset + len(raw.encode('utf-8'))})
        offset += len(line.encode('utf-8'))
    if len(matches) != 1:
        raise Fault('invalid_request')
    return matches[0]


class Processing(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS proposals (id TEXT PRIMARY KEY, source TEXT NOT NULL, result TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS requests (actor TEXT, key TEXT, input TEXT NOT NULL, proposal TEXT NOT NULL,
                                                    PRIMARY KEY(actor,key));'''
    dependencies = ('wallet.local', 'connector.local')

    def descriptor(self):
        return descriptor(self.config, 'processing', {'farmy.processing': ['extraction.compute', 'extraction.get']},
                          {'farmy.storage': ['read.version'], 'farmy.permissions': ['access.check']})

    def handle(self, peer, body):
        operation = body['operation']
        if operation == 'extraction.compute':
            if (peer != 'workflow.local' or body['subjectId'] != 'owner'
                    or body['grantRef'] != 'grant.workflow-extract' or len(body['inputRefs']) != 1):
                raise Fault('denied')
            data = self.remote('connector.local', 'read.version', {}, body,
                               grant=body['payload']['sourceReadGrant'])
            result = dict(extract(data), source=body['inputRefs'][0], sourceSha256=hashlib.sha256(data).hexdigest(),
                          extractor=EXTRACTOR)
            proposal = 'proposal.' + digest(result)
            result['proposalId'] = proposal
            logical = digest({'refs': body['inputRefs'], 'payload': body['payload'], 'extractor': EXTRACTOR})
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE')
                old = db.execute('SELECT * FROM requests WHERE actor=? AND key=?', (peer, body['idempotencyKey'])).fetchone()
                if old and old['input'] != logical:
                    raise Fault('conflict')
                self.deadline(body)
                db.execute('INSERT OR IGNORE INTO proposals VALUES(?,?,?)',
                           (proposal, json.dumps(body['inputRefs'][0], sort_keys=True), json.dumps(result)))
                db.execute('INSERT OR IGNORE INTO requests VALUES(?,?,?,?)', (peer, body['idempotencyKey'], logical, proposal))
                self.event(db, peer, operation, 'accepted')
            return {'proposalId': proposal}
        if operation == 'extraction.get':
            self.access(peer, body)
            with self.db() as db:
                row = db.execute('SELECT * FROM proposals WHERE id=?', (body['payload']['proposalId'],)).fetchone()
                if row is None:
                    raise Fault('not_found')
                if json.loads(row['source']) != body['inputRefs'][0]:
                    raise Fault('denied')
                result = json.loads(row['result'])
            self.access(peer, body)
            self.deadline(body)
            with self.db() as db:
                self.event(db, peer, operation, 'disclosed')
            return result
        raise Fault('unsupported')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Processing(json.loads(Path(parser.parse_args().config).read_text())))
