"""Alternative Knowledge domain implementation; shared optional HTTP/mTLS SDK.

An append-only journal owns evidence and idempotency records in one transaction.
It never imports the evidence provider or opens another implementation's database.
"""
import argparse
import json
from pathlib import Path

from farmy_transport.http import Fault, descriptor, serve
from farmy_transport.local import LocalService, digest
from farmy_transport.monitoring import summarize


class LedgerKnowledge(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS journal (
        sequence INTEGER PRIMARY KEY, actor TEXT NOT NULL, request_key TEXT NOT NULL,
        request_hash TEXT NOT NULL, source_hash TEXT NOT NULL, proposal TEXT NOT NULL,
        document TEXT NOT NULL, UNIQUE(actor, request_key));
        CREATE INDEX IF NOT EXISTS source_lookup ON journal(source_hash);'''
    dependencies = ('wallet.local', 'processing.local')

    def descriptor(self):
        return descriptor(self.config, 'knowledge',
                          {'farmy.knowledge': ['evidence.index', 'evidence.query']},
                          {'farmy.permissions': ['access.check'], 'farmy.processing': ['extraction.get']})

    def monitoring_summary(self):
        return summarize(self, [('Evidence entries', 'SELECT count(DISTINCT source_hash) FROM journal'),
                                ('Accepted index requests', 'SELECT count(*) FROM journal')], self.dependencies)

    def handle(self, peer, body):
        operation = body['operation']
        if operation not in ('evidence.index', 'evidence.query'):
            raise Fault('unsupported')
        self.access(peer, body)
        source = body['inputRefs'][0]
        source_key = digest(source)
        if operation == 'evidence.query':
            with self.db() as connection:
                row = connection.execute('SELECT document FROM journal WHERE source_hash=? ORDER BY sequence LIMIT 1',
                                         (source_key,)).fetchone()
            if row is None:
                raise Fault('not_found')
            evidence = json.loads(row['document'])
            if evidence['source'] != source:
                raise Fault('conflict')
            self.access(peer, body)
            self.deadline(body)
            with self.db() as connection:
                self.event(connection, peer, operation, 'disclosed')
            return {'evidence': evidence}
        if peer != 'workflow.local':
            raise Fault('denied')
        inputs = body['payload']
        proposed = self.remote('processing.local', 'extraction.get', {'proposalId': inputs['proposalId']},
                               body, grant=inputs['disclosureGrant'])
        if proposed['source'] != source or proposed['proposalId'] != inputs['proposalId']:
            raise Fault('conflict')
        fingerprint = digest({'refs': body['inputRefs'], 'payload': inputs, 'grant': body['grantRef']})
        self.access(peer, body)
        with self.db() as connection:
            connection.execute('BEGIN IMMEDIATE')
            prior = connection.execute('SELECT request_hash FROM journal WHERE actor=? AND request_key=?',
                                       (peer, body['idempotencyKey'])).fetchone()
            if prior and prior['request_hash'] != fingerprint:
                raise Fault('conflict')
            previous = connection.execute('SELECT document FROM journal WHERE source_hash=? OR proposal=?',
                                          (source_key, proposed['proposalId'])).fetchall()
            if any(json.loads(row['document']) != proposed for row in previous):
                raise Fault('conflict')
            self.deadline(body)
            if prior is None:
                connection.execute('INSERT INTO journal(actor,request_key,request_hash,source_hash,proposal,document) VALUES(?,?,?,?,?,?)',
                                   (peer, body['idempotencyKey'], fingerprint, source_key,
                                    proposed['proposalId'], json.dumps(proposed)))
            self.event(connection, peer, operation, 'accepted')
        return {'proposalId': proposed['proposalId']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(LedgerKnowledge(json.loads(Path(parser.parse_args().config).read_text())))
