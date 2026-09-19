"""UC-001 wallet authority; provider bytes remain owned by the connector."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
from uuid import uuid4

from bindings import resolve
from farmy_transport.http import Fault, PROFILE, descriptor, exchange, request, serve, timestamp


class Wallet:
    def __init__(self, config):
        config.setdefault('implementationVersion', '0.2.0')
        self.config = config
        os.umask(0o077)
        self.state = Path(config['state'])
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.binding = resolve(config['binding'], config['walletId'], 'farmy.storage', 'snapshot.capture')
        if self.binding['instanceId'] != 'connector.local':
            raise ValueError('Unsupported reference connector binding')
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS resources (id TEXT PRIMARY KEY, path TEXT NOT NULL,
                    current_version TEXT NOT NULL, revision INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS versions (id TEXT PRIMARY KEY, resource TEXT NOT NULL,
                    snapshot TEXT NOT NULL, digest TEXT NOT NULL, size INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS grants (id TEXT PRIMARY KEY, subject TEXT NOT NULL,
                    resource TEXT NOT NULL, version TEXT NOT NULL, expires REAL NOT NULL,
                    expiry_text TEXT NOT NULL, audience TEXT NOT NULL, purpose TEXT NOT NULL,
                    revoked INTEGER NOT NULL, revision INTEGER NOT NULL, binding_revision INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS permissions (id TEXT PRIMARY KEY, subject TEXT NOT NULL,
                    resource TEXT NOT NULL, version TEXT NOT NULL, audience TEXT NOT NULL,
                    operation TEXT NOT NULL, purpose TEXT NOT NULL, expires REAL NOT NULL,
                    revoked INTEGER NOT NULL, revision INTEGER NOT NULL, binding_revision INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS idempotency (actor TEXT, operation TEXT, key TEXT,
                    digest TEXT NOT NULL, result TEXT NOT NULL, PRIMARY KEY(actor,operation,key));
                CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, time REAL, actor TEXT,
                    event TEXT, outcome TEXT, resource TEXT);
            ''')

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.state / 'wallet.sqlite', timeout=3)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def event(self, db, actor, event, outcome, resource=None):
        db.execute('INSERT INTO audit(time,actor,event,outcome,resource) VALUES(?,?,?,?,?)',
                   (time.time(), actor, event, outcome, resource))

    def failure(self, actor, code):
        with self.db() as db:
            self.event(db, actor, 'request', code)

    def ready(self):
        try:
            exchange(self.config, 'connector.local', path='/farmy/v0/health/live')
            return True
        except Fault:
            return False

    def descriptor(self):
        return descriptor(self.config, 'wallet',
            {'farmy.wallet': ['resource.register', 'resource.inspect', 'resource.move',
                             'resource.update', 'grant.issue', 'grant.revoke'],
             'farmy.permissions': ['access.issue', 'access.revoke', 'access.check'],
             'farmy.authorization': ['authorize.read']},
            {'farmy.storage': ['snapshot.capture']})

    def snapshot(self, path, body):
        query = request(self.config, 'connector.local', 'snapshot.capture', {'path': path},
                        grant='grant.wallet-capture', subject=body['subjectId'])
        query['deadline'] = body['deadline']
        return exchange(self.config, 'connector.local', query)

    def inspect(self, db, resource):
        row = db.execute('''SELECT r.id resourceId,r.current_version versionId,r.revision,
                       v.digest sha256,v.size,r.path FROM resources r JOIN versions v
                       ON v.id=r.current_version WHERE r.id=?''', (resource,)).fetchone()
        if row is None:
            raise Fault('not_found')
        return dict(row)

    def current(self, db, body):
        resource = body['payload']['resourceId']
        result = self.inspect(db, resource)
        if body['expectedRevision'] != result['revision']:
            raise Fault('conflict')
        expected = [{'walletId': self.config['walletId'], 'resourceId': resource,
                     'versionId': result['versionId']}]
        if body['inputRefs'] != expected:
            raise Fault('conflict')
        return result

    def mutate(self, db, body):
        operation, payload = body['operation'], body['payload']
        if operation == 'resource.register':
            if body['inputRefs']:
                raise Fault('invalid_request')
            snap = self.snapshot(payload['path'], body)
            resource, version = 'resource.' + uuid4().hex, 'version.' + uuid4().hex
            db.execute('INSERT INTO resources VALUES(?,?,?,1)', (resource, payload['path'], version))
            db.execute('INSERT INTO versions VALUES(?,?,?,?,?)',
                       (version, resource, snap['snapshotId'], snap['sha256'], snap['size']))
            return self.inspect(db, resource)
        if operation in ('resource.move', 'resource.update'):
            old = self.current(db, body)
            path = payload.get('path', old['path'])
            snap = self.snapshot(path, body)
            version = old['versionId']
            if operation == 'resource.move' and snap['sha256'] != old['sha256']:
                raise Fault('conflict')
            if operation == 'resource.update':
                if snap['sha256'] == old['sha256']:
                    return old
                version = 'version.' + uuid4().hex
                db.execute('INSERT INTO versions VALUES(?,?,?,?,?)',
                           (version, old['resourceId'], snap['snapshotId'], snap['sha256'], snap['size']))
            db.execute('UPDATE resources SET path=?,current_version=?,revision=revision+1 WHERE id=?',
                       (path, version, old['resourceId']))
            return self.inspect(db, old['resourceId'])
        if operation == 'grant.issue':
            expires = timestamp(payload['expiresAt'])
            if not time.time() < expires <= time.time() + 3600:
                raise Fault('invalid_request')
            if payload['subjectId'] not in set(self.config.get('readSubjects', ['owner', 'reader', 'denied'])):
                raise Fault('denied')
            if db.execute('SELECT 1 FROM versions WHERE id=? AND resource=?',
                          (payload['versionId'], payload['resourceId'])).fetchone() is None:
                raise Fault('not_found')
            expected = [{'walletId': self.config['walletId'], 'resourceId': payload['resourceId'],
                         'versionId': payload['versionId']}]
            if body['inputRefs'] != expected:
                raise Fault('invalid_request')
            grant = 'grant.' + uuid4().hex
            db.execute('INSERT INTO grants VALUES(?,?,?,?,?,?,?,?,0,1,?)',
                       (grant, payload['subjectId'], payload['resourceId'], payload['versionId'],
                        expires, payload['expiresAt'], 'connector.local', payload['purpose'], self.binding['revision']))
            return {'grantId': grant, 'subjectId': payload['subjectId'], 'resourceId': payload['resourceId'],
                    'versionId': payload['versionId'], 'expiresAt': payload['expiresAt'], 'revision': 1}
        if operation == 'grant.revoke':
            row = db.execute('SELECT * FROM grants WHERE id=?', (payload['grantId'],)).fetchone()
            if row is None:
                raise Fault('not_found')
            if body['expectedRevision'] != row['revision']:
                raise Fault('conflict')
            db.execute('UPDATE grants SET revoked=1,revision=revision+1 WHERE id=?', (payload['grantId'],))
            return {'grantId': payload['grantId'], 'revoked': True, 'revision': row['revision'] + 1}
        if operation == 'access.issue':
            scope = {key: payload[key] for key in ('audience', 'operation', 'purpose')}
            if (scope not in self.config.get('permissionScopes', [])
                    or payload['subjectId'] not in set(self.config['peers'].values())):
                raise Fault('denied')
            expires = timestamp(payload['expiresAt'])
            if not time.time() < expires <= time.time() + 3600:
                raise Fault('invalid_request')
            expected = [{'walletId': self.config['walletId'], 'resourceId': payload['resourceId'],
                         'versionId': payload['versionId']}]
            if body['inputRefs'] != expected:
                raise Fault('invalid_request')
            if db.execute('SELECT 1 FROM versions WHERE id=? AND resource=?',
                          (payload['versionId'], payload['resourceId'])).fetchone() is None:
                raise Fault('not_found')
            grant = 'permission.' + uuid4().hex
            db.execute('INSERT INTO permissions VALUES(?,?,?,?,?,?,?,?,0,1,?)',
                       (grant, payload['subjectId'], payload['resourceId'], payload['versionId'],
                        payload['audience'], payload['operation'], payload['purpose'], expires,
                        self.config.get('compositionRevision', 1)))
            return {'grantId': grant, 'revision': 1}
        if operation == 'access.revoke':
            row = db.execute('SELECT * FROM permissions WHERE id=?', (payload['grantId'],)).fetchone()
            if row is None:
                raise Fault('not_found')
            if body['expectedRevision'] != row['revision']:
                raise Fault('conflict')
            db.execute('UPDATE permissions SET revoked=1,revision=revision+1 WHERE id=?', (payload['grantId'],))
            return {'grantId': payload['grantId'], 'revoked': True, 'revision': row['revision'] + 1}
        raise Fault('unsupported')

    def check_access(self, peer, body):
        if len(body['inputRefs']) != 1:
            raise Fault('denied')
        ref = body['inputRefs'][0]
        with self.db() as db:
            row = db.execute('SELECT * FROM permissions WHERE id=?', (body['grantRef'],)).fetchone()
            if (row is None or row['revoked'] or row['expires'] <= time.time()
                    or row['subject'] != body['subjectId'] or row['audience'] != peer
                    or row['operation'] != body['payload']['operation']
                    or row['purpose'] != body['payload']['purpose']
                    or row['resource'] != ref['resourceId'] or row['version'] != ref['versionId']
                    or row['binding_revision'] != self.config.get('compositionRevision', 1)):
                raise Fault('denied')
            self.event(db, body['subjectId'], 'access.check', 'allowed', ref['resourceId'])
            return {'allowed': True, 'decisionRevision': row['revision']}

    def authorize(self, peer, body):
        if peer != 'connector.local' or len(body['inputRefs']) != 1:
            raise Fault('denied')
        ref = body['inputRefs'][0]
        with self.db() as db:
            row = db.execute('SELECT * FROM grants WHERE id=?', (body['grantRef'],)).fetchone()
            if (row is None or row['revoked'] or row['expires'] <= time.time()
                    or row['subject'] != body['subjectId'] or row['audience'] != peer
                    or row['resource'] != ref['resourceId'] or row['version'] != ref['versionId']
                    or row['purpose'] != body['purpose'] or row['binding_revision'] != self.binding['revision']):
                raise Fault('denied')
            version = db.execute('SELECT * FROM versions WHERE id=? AND resource=?',
                                 (ref['versionId'], ref['resourceId'])).fetchone()
            if version is None:
                raise Fault('denied')
            self.event(db, body['subjectId'], 'authorize.read', 'allowed', ref['resourceId'])
            return {'allowed': True, 'snapshotId': version['snapshot'], 'sha256': version['digest'],
                    'size': version['size'], 'decisionRevision': row['revision']}

    def handle(self, peer, body):
        if body['operation'] == 'access.check':
            return self.check_access(peer, body)
        if body['operation'] == 'authorize.read':
            return self.authorize(peer, body)
        if peer != 'owner' or body['subjectId'] != peer or body['grantRef'] != 'grant.owner-bootstrap':
            raise Fault('denied')
        if body['operation'] == 'resource.inspect':
            with self.db() as db:
                result = self.inspect(db, body['payload']['resourceId'])
                self.event(db, peer, 'resource.inspect', 'succeeded', result['resourceId'])
                return result
        if body['operation'] not in {'resource.register', 'resource.move', 'resource.update', 'grant.issue', 'grant.revoke', 'access.issue', 'access.revoke'}:
            raise Fault('unsupported')
        canonical = {key: body.get(key) for key in ('operation','payload','inputRefs','expectedRevision','purpose','grantRef','subjectId')}
        canonical['bindingRevision'] = self.binding['revision']
        if body['operation'].startswith('access.'):
            canonical['compositionRevision'] = self.config.get('compositionRevision', 1)
        digest = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            args = (peer, body['operation'], body['idempotencyKey'])
            row = db.execute('SELECT * FROM idempotency WHERE actor=? AND operation=? AND key=?', args).fetchone()
            if row:
                if row['digest'] != digest:
                    raise Fault('conflict')
                self.event(db, peer, body['operation'], 'replayed')
                return json.loads(row['result'])
            result = self.mutate(db, body)
            if timestamp(body['deadline']) <= time.time():
                raise Fault('expired')
            self.event(db, peer, body['operation'], 'succeeded', result.get('resourceId'))
            db.execute('INSERT INTO idempotency VALUES(?,?,?,?,?)', (*args, digest, json.dumps(result)))
            return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    serve(Wallet(json.loads(Path(args.config).read_text())))
