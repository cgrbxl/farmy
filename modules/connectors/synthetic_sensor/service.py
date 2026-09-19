"""Synthetic immutable observations with enforced source membership."""
import argparse
import json
from pathlib import Path
from uuid import uuid4

from farmy_transport.http import Fault, descriptor, serve, utc
from farmy_transport.local import LocalService, digest


class Sensor(LocalService):
    schema = '''
        CREATE TABLE IF NOT EXISTS observations (id TEXT PRIMARY KEY, source TEXT NOT NULL,
            owner TEXT NOT NULL, sequence INTEGER NOT NULL, result TEXT NOT NULL, UNIQUE(source,sequence));
        CREATE TABLE IF NOT EXISTS appends (actor TEXT, key TEXT, input TEXT NOT NULL, result TEXT NOT NULL,
                                           PRIMARY KEY(actor,key));
        CREATE TABLE IF NOT EXISTS deliveries (id TEXT PRIMARY KEY, source TEXT NOT NULL, receipt TEXT NOT NULL);
    '''
    dependencies = ('wallet.local',)

    def descriptor(self):
        return descriptor(self.config, 'connectors',
                          {'farmy.observations': ['sensor.append', 'sensor.read', 'sensor.audit']},
                          {'farmy.sources': ['source.authorize']})

    def authorize(self, peer, body, action):
        if peer != body['subjectId'] or body['inputRefs']:
            raise Fault('denied')
        payload = body['payload']
        return self.remote('wallet.local', 'source.authorize',
                           {'sourceId': payload['sourceId'], 'ownerId': payload['ownerId'], 'action': action},
                           body, subject=peer, grant=body['grantRef'])

    def handle(self, peer, body):
        operation = body['operation']
        if operation not in ('sensor.append', 'sensor.read', 'sensor.audit'):
            raise Fault('unsupported')
        action = operation.split('.')[1]
        self.authorize(peer, body, action)
        payload = body['payload']
        if action == 'append':
            logical = digest(payload)
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE')
                old = db.execute('SELECT * FROM appends WHERE actor=? AND key=?',
                                 (peer, body['idempotencyKey'])).fetchone()
                if old:
                    if old['input'] != logical:
                        raise Fault('conflict')
                    return json.loads(old['result'])
                sequence = db.execute('SELECT COALESCE(MAX(sequence),0)+1 FROM observations WHERE source=?',
                                      (payload['sourceId'],)).fetchone()[0]
                result = dict(payload, observationId='observation.' + uuid4().hex, sequence=sequence)
                self.deadline(body)
                db.execute('INSERT INTO observations VALUES(?,?,?,?,?)',
                           (result['observationId'], payload['sourceId'], payload['ownerId'], sequence, json.dumps(result)))
                db.execute('INSERT INTO appends VALUES(?,?,?,?)',
                           (peer, body['idempotencyKey'], logical, json.dumps(result)))
                self.event(db, peer, operation, 'accepted')
            return result
        if action == 'audit':
            with self.db() as db:
                rows = db.execute('SELECT receipt FROM deliveries WHERE source=? ORDER BY rowid DESC LIMIT ?',
                                  (payload['sourceId'], payload['limit'])).fetchall()
            self.authorize(peer, body, action)
            self.deadline(body)
            with self.db() as db:
                self.event(db, peer, operation, 'disclosed')
            return {'receipts': [json.loads(row['receipt']) for row in rows]}
        with self.db() as db:
            rows = db.execute('''SELECT * FROM observations WHERE source=? AND owner=? AND sequence>?
                                 ORDER BY sequence LIMIT ?''',
                              (payload['sourceId'], payload['ownerId'], payload['afterSequence'], payload['limit'])).fetchall()
        observations = [json.loads(row['result']) for row in rows]
        # Never relabel a stored observation as belonging to the requested source.
        for row, observation in zip(rows, observations):
            if (observation['sourceId'] != payload['sourceId'] or observation['ownerId'] != payload['ownerId']
                    or observation['observationId'] != row['id'] or observation['sequence'] != row['sequence']):
                raise Fault('unavailable')
        decision = self.authorize(peer, body, 'read')
        self.deadline(body)
        delivery = 'delivery.' + uuid4().hex
        receipt = {'deliveryId': delivery, 'sourceId': payload['sourceId'], 'ownerId': payload['ownerId'],
                   'consumerId': peer, 'grantId': body['grantRef'], 'decisionRevision': decision['decisionRevision'],
                   'recordedAt': utc(), 'event': 'release_authorized',
                   'observations': [{'observationId': o['observationId'], 'sequence': o['sequence'], 'sha256': digest(o)}
                                    for o in observations]}
        # Persist the authorised release before returning bytes. This is not a
        # claim that the remote client received or subsequently used them.
        with self.db() as db:
            db.execute('INSERT INTO deliveries VALUES(?,?,?)', (delivery, payload['sourceId'], json.dumps(receipt)))
            self.event(db, peer, operation, 'release_authorized')
        return {'sourceId': payload['sourceId'], 'ownerId': payload['ownerId'],
                'deliveryId': delivery, 'observations': observations}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Sensor(json.loads(Path(parser.parse_args().config).read_text())))
