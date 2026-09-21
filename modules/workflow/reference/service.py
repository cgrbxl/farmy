"""A fixed durable two-step workflow. Owner retries drive recovery."""
import argparse
import json
from pathlib import Path
import threading

from bindings import resolve, admit
from farmy_transport.monitoring import summarize
from farmy_transport.http import Fault, descriptor, serve
from farmy_transport.local import LocalService, digest


class Workflow(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, key TEXT NOT NULL,
                  input TEXT NOT NULL, status TEXT NOT NULL, proposal TEXT, UNIQUE(owner,key));'''
    dependencies = ('processing.local', 'knowledge.local')

    def __init__(self, config):
        super().__init__(config)
        self.lock = threading.Lock()
        self.knowledge_binding = None
        if config.get('knowledgeBinding'):
            self.knowledge_binding = resolve(config['knowledgeBinding'], config['walletId'],
                                             'farmy.knowledge', 'evidence.index', '0.2-draft')
        self.knowledge_target = self.knowledge_binding['instanceId'] if self.knowledge_binding else 'knowledge.local'
        self.dependencies = ('processing.local', self.knowledge_target)

    def monitoring_summary(self):
        return summarize(self, [
            ('Jobs', 'SELECT count(*) FROM jobs'),
            ('Succeeded jobs', "SELECT count(*) FROM jobs WHERE status='succeeded'"),
            ('Incomplete jobs', "SELECT count(*) FROM jobs WHERE status!='succeeded'"),
        ], self.dependencies)

    def descriptor(self):
        return descriptor(self.config, 'workflow', {'farmy.workflow': ['job.run', 'job.inspect']},
                          {'farmy.processing': ['extraction.compute'], 'farmy.knowledge': ['evidence.index']})

    def handle(self, peer, body):
        if peer != 'owner' or body['subjectId'] != peer or body['grantRef'] != 'grant.owner-bootstrap':
            raise Fault('denied')
        if body['operation'] == 'job.inspect':
            with self.db() as db:
                row = db.execute('SELECT * FROM jobs WHERE id=? AND owner=?', (body['payload']['jobId'], peer)).fetchone()
                if row is None:
                    raise Fault('not_found')
                self.event(db, peer, 'job.inspect', 'succeeded')
                return self.receipt(row)
        if body['operation'] != 'job.run':
            raise Fault('unsupported')
        if len(body['inputRefs']) != 1:
            raise Fault('invalid_request')
        if not self.lock.acquire(timeout=.5):
            raise Fault('unavailable')
        try:
            return self.run_job(peer, body)
        finally:
            self.lock.release()

    def receipt(self, row):
        return {'jobId': row['id'], 'status': row['status'], 'proposalId': row['proposal']}

    def run_job(self, peer, body):
        logical_input = {'refs': body['inputRefs'], 'payload': body['payload'],
                         'compositionRevision': self.config['compositionRevision']}
        if self.knowledge_binding:
            logical_input['knowledgeBinding'] = self.knowledge_binding
        logical = digest(logical_input)
        job = 'job.' + digest({'owner': peer, 'key': body['idempotencyKey']})
        with self.db() as db:
            row = db.execute('SELECT * FROM jobs WHERE id=?', (job,)).fetchone()
            if row and row['input'] != logical:
                raise Fault('conflict')
            if row is None:
                self.deadline(body)
                db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,NULL)', (job, peer, body['idempotencyKey'], logical, 'pending'))
                self.event(db, peer, 'job.run', 'pending')
        # Do not hold a database transaction while calling another service.
        with self.db() as db:
            row = db.execute('SELECT * FROM jobs WHERE id=?', (job,)).fetchone()
        payload = body['payload']
        if row['status'] == 'succeeded':
            return self.receipt(row)
        if row['status'] == 'pending':
            result = self.remote('processing.local', 'extraction.compute',
                                 {'sourceReadGrant': payload['sourceReadGrant']}, body,
                                 grant='grant.workflow-extract', subject='owner', key='extract.' + job)
            self.deadline(body)
            with self.db() as db:
                db.execute("UPDATE jobs SET status='extracted',proposal=? WHERE id=?", (result['proposalId'], job))
                self.event(db, peer, 'job.run', 'extracted')
        with self.db() as db:
            row = db.execute('SELECT * FROM jobs WHERE id=?', (job,)).fetchone()
        if self.knowledge_binding:
            admit(self.config, self.knowledge_binding)
        result = self.remote(self.knowledge_target, 'evidence.index',
                             {'proposalId': row['proposal'], 'disclosureGrant': payload['disclosureGrant']}, body,
                             grant=payload['indexGrant'], key='index.' + job)
        if result['proposalId'] != row['proposal']:
            raise Fault('conflict')
        self.deadline(body)
        with self.db() as db:
            db.execute("UPDATE jobs SET status='succeeded' WHERE id=?", (job,))
            self.event(db, peer, 'job.run', 'succeeded')
            return self.receipt(db.execute('SELECT * FROM jobs WHERE id=?', (job,)).fetchone())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Workflow(json.loads(Path(parser.parse_args().config).read_text())))
