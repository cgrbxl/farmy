"""Exact-source derived evidence; disclosure requires online permission."""
import argparse
import json
from pathlib import Path

from farmy_transport.monitoring import summarize
from farmy_transport.http import Fault, descriptor, serve
from farmy_transport.local import LocalService, digest


class Knowledge(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS evidence (source TEXT PRIMARY KEY, proposal TEXT UNIQUE NOT NULL, result TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS requests (actor TEXT, key TEXT, input TEXT NOT NULL, result TEXT NOT NULL,
                                                    PRIMARY KEY(actor,key));'''
    dependencies = ('wallet.local', 'processing.local')

    def monitoring_summary(self):
        return summarize(self, [
            ('Evidence entries', 'SELECT count(*) FROM evidence'),
        ], self.dependencies)

    def descriptor(self):
        return descriptor(self.config, 'knowledge', {'farmy.knowledge': ['evidence.index', 'evidence.query']},
                          {'farmy.processing': ['extraction.get'], 'farmy.permissions': ['access.check']})

    def handle(self, peer, body):
        if body['operation'] not in ('evidence.index', 'evidence.query'):
            raise Fault('unsupported')
        self.access(peer, body)
        source = json.dumps(body['inputRefs'][0], sort_keys=True)
        if body['operation'] == 'evidence.index':
            if peer != 'workflow.local':
                raise Fault('denied')
            payload = body['payload']
            result = self.remote('processing.local', 'extraction.get', {'proposalId': payload['proposalId']},
                                 body, grant=payload['disclosureGrant'])
            if result['source'] != body['inputRefs'][0] or result['proposalId'] != payload['proposalId']:
                raise Fault('conflict')
            logical = digest({'refs': body['inputRefs'], 'payload': payload, 'grant': body['grantRef']})
            self.access(peer, body)
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE')
                prior = db.execute('SELECT * FROM requests WHERE actor=? AND key=?', (peer, body['idempotencyKey'])).fetchone()
                if prior and prior['input'] != logical:
                    raise Fault('conflict')
                old = db.execute('SELECT * FROM evidence WHERE source=?', (source,)).fetchone()
                if old and json.loads(old['result']) != result:
                    raise Fault('conflict')
                self.deadline(body)
                db.execute('INSERT OR IGNORE INTO evidence VALUES(?,?,?)', (source, result['proposalId'], json.dumps(result)))
                receipt = {'proposalId': result['proposalId']}
                db.execute('INSERT OR IGNORE INTO requests VALUES(?,?,?,?)', (peer, body['idempotencyKey'], logical, json.dumps(receipt)))
                self.event(db, peer, 'evidence.index', 'accepted')
            return receipt
        with self.db() as db:
            row = db.execute('SELECT result FROM evidence WHERE source=?', (source,)).fetchone()
            if row is None:
                raise Fault('not_found')
            result = json.loads(row['result'])
        self.access(peer, body)
        self.deadline(body)
        with self.db() as db:
            self.event(db, peer, 'evidence.query', 'disclosed')
        return {'evidence': result}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Knowledge(json.loads(Path(parser.parse_args().config).read_text())))
