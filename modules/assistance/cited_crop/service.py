"""One bounded question with an independently checked exact-source citation."""
import argparse
import json
from pathlib import Path

from farmy_transport.http import Fault, descriptor, serve
from farmy_transport.local import LocalService, digest


class Assistance(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS answers
                (actor TEXT, key TEXT, input TEXT NOT NULL, result TEXT NOT NULL,
                 PRIMARY KEY(actor,key));'''
    dependencies = ('wallet.local', 'knowledge.local', 'model.local')

    def descriptor(self):
        return descriptor(self.config, 'assistance', {'farmy.assistance': ['answer.create']},
                          {'farmy.permissions': ['access.check'], 'farmy.knowledge': ['evidence.query'],
                           'farmy.models': ['model.invoke']})

    def handle(self, peer, body):
        if body['operation'] != 'answer.create':
            raise Fault('unsupported')
        self.access(peer, body)
        payload = body['payload']
        evidence = self.remote('knowledge.local', 'evidence.query', {'field': 'crop'}, body,
                               grant=payload['knowledgeGrant'])['evidence']
        if evidence['source'] != body['inputRefs'][0]:
            raise Fault('conflict')
        logical = digest({'refs': body['inputRefs'], 'payload': payload, 'grant': body['grantRef']})
        with self.db() as db:
            old = db.execute('SELECT * FROM answers WHERE actor=? AND key=?',
                             (peer, body['idempotencyKey'])).fetchone()
            if old and old['input'] != logical:
                raise Fault('conflict')
        # Replay still checks Model access (its cached invocation checks current
        # invocation and evidence grants). No answer cache bypasses revocation.
        model = self.remote('model.local', 'model.invoke',
                            {'routeId': payload['routeId'], 'evidenceGrant': payload['modelEvidenceGrant']},
                            body, grant=payload['modelGrant'],
                            key='invoke.' + digest({'actor': peer, 'key': body['idempotencyKey']}))
        if (model['evidence'] != evidence or model['selection']['crop'] != evidence['value']
                or model['selection']['citationId'] != evidence['proposalId']
                or model['route']['routeId'] != payload['routeId']):
            raise Fault('conflict')
        answer = {'answerId': 'answer.' + digest({'actor': peer, 'key': body['idempotencyKey']}),
                  'text': 'The recorded crop is ' + model['selection']['crop'] + '.',
                  'citation': evidence, 'route': model['route']}
        self.access(peer, body)
        latest = self.remote('knowledge.local', 'evidence.query', {'field': 'crop'}, body,
                             grant=payload['knowledgeGrant'])['evidence']
        if latest != evidence:
            raise Fault('conflict')
        self.deadline(body)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT * FROM answers WHERE actor=? AND key=?',
                             (peer, body['idempotencyKey'])).fetchone()
            if old and (old['input'] != logical or json.loads(old['result']) != answer):
                raise Fault('conflict')
            db.execute('INSERT OR IGNORE INTO answers VALUES(?,?,?,?)',
                       (peer, body['idempotencyKey'], logical, json.dumps(answer)))
            self.event(db, peer, 'answer.create', 'disclosed')
        return answer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Assistance(json.loads(Path(parser.parse_args().config).read_text())))
