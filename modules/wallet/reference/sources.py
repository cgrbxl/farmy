"""Source ownership and consumer permissions within the Wallet implementation."""
import time
from uuid import uuid4

from farmy_transport.http import Fault, timestamp

SCHEMA = '''
CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, owner TEXT NOT NULL, connector TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_grants (id TEXT PRIMARY KEY, source TEXT NOT NULL, owner TEXT NOT NULL,
    consumer TEXT NOT NULL, connector TEXT NOT NULL, expires REAL NOT NULL, revoked INTEGER NOT NULL,
    revision INTEGER NOT NULL);
'''


def source(db, payload):
    row = db.execute('SELECT * FROM sources WHERE id=?', (payload['sourceId'],)).fetchone()
    if row is None or row['owner'] != payload['ownerId']:
        raise Fault('denied')
    return row


def mutate(wallet, db, body):
    op, payload = body['operation'], body['payload']
    if body['inputRefs']:
        raise Fault('invalid_request')
    if op == 'source.register':
        if payload['connectorId'] not in wallet.config.get('sourceConnectors', []):
            raise Fault('denied')
        identity = 'source.' + uuid4().hex
        db.execute('INSERT INTO sources VALUES(?,?,?)', (identity, body['subjectId'], payload['connectorId']))
        return {'sourceId': identity, 'ownerId': body['subjectId'], 'connectorId': payload['connectorId']}
    if op == 'source.grant':
        row = source(db, payload)
        if row['owner'] != body['subjectId'] or payload['consumerId'] not in wallet.config['peers'].values():
            raise Fault('denied')
        expiry = timestamp(payload['expiresAt'])
        if not time.time() < expiry <= time.time() + 3600:
            raise Fault('invalid_request')
        identity = 'source-grant.' + uuid4().hex
        db.execute('INSERT INTO source_grants VALUES(?,?,?,?,?,?,0,1)',
                   (identity, row['id'], row['owner'], payload['consumerId'], row['connector'], expiry))
        return {'grantId': identity, 'revision': 1}
    if op == 'source.revoke':
        row = db.execute('SELECT * FROM source_grants WHERE id=?', (payload['grantId'],)).fetchone()
        if row is None or row['owner'] != body['subjectId']:
            raise Fault('denied')
        if body['expectedRevision'] != row['revision']:
            raise Fault('conflict')
        db.execute('UPDATE source_grants SET revoked=1, revision=revision+1 WHERE id=?', (row['id'],))
        return {'grantId': row['id'], 'revision': row['revision'] + 1, 'revoked': True}
    raise Fault('unsupported')


def authorize(wallet, peer, body):
    if body['inputRefs']:
        raise Fault('invalid_request')
    payload = body['payload']
    with wallet.db() as db:
        row = source(db, payload)
        if peer != row['connector'] or peer not in wallet.config.get('sourceConnectors', []):
            raise Fault('denied')
        revision = 1
        if payload['action'] in ('append', 'audit'):
            if body['subjectId'] != row['owner'] or body['grantRef'] != 'grant.owner-bootstrap':
                raise Fault('denied')
        else:
            grant = db.execute('SELECT * FROM source_grants WHERE id=?', (body['grantRef'],)).fetchone()
            if (grant is None or grant['source'] != row['id'] or grant['owner'] != row['owner']
                    or grant['consumer'] != body['subjectId'] or grant['connector'] != peer
                    or grant['revoked'] or grant['expires'] <= time.time()):
                raise Fault('denied')
            revision = grant['revision']
        wallet.event(db, body['subjectId'], 'source.' + payload['action'], 'allowed', row['id'])
        return {'allowed': True, 'decisionRevision': revision}
