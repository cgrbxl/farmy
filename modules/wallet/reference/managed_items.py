"""Opt-in managed-copy admission. Metadata belongs to Wallet; bytes to Connector."""
import json
import time
from uuid import uuid4
from farmy_transport.http import Fault, exchange, request, timestamp, utc
from farmy_transport.local import digest

SCHEMA = '''CREATE TABLE IF NOT EXISTS managed_items (
    resource TEXT PRIMARY KEY, metadata TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS admissions (
    actor TEXT, key TEXT, input TEXT NOT NULL, result TEXT NOT NULL, PRIMARY KEY(actor,key));'''


def inspect(wallet, db, resource):
    row = db.execute('SELECT metadata FROM managed_items WHERE resource=?', (resource,)).fetchone()
    if not row:
        raise Fault('not_found')
    return json.loads(row['metadata'])


def restrict(wallet, db, body):
    """A raw-read MVP: no derived/export capability grant for admitted items yet."""
    resource = body['payload'].get('resourceId')
    row = db.execute('SELECT metadata FROM managed_items WHERE resource=?', (resource,)).fetchone()
    if row is None:
        return
    metadata = json.loads(row['metadata'])
    if body['operation'] in ('resource.move', 'resource.update', 'access.issue'):
        raise Fault('unsupported')
    if body['operation'] == 'grant.issue' and body['payload']['subjectId'] not in metadata['allowedReaders']:
        raise Fault('denied')


def admit(wallet, body):
    payload = body['payload']
    if body['inputRefs'] or payload['ownerId'] != body['subjectId']:
        raise Fault('denied')
    readers = payload['allowedReaders']
    if (not set(readers) <= set(wallet.config['peers'].values())
            or (payload['classification'] == 'private' and readers != [payload['ownerId']])):
        raise Fault('denied')
    key = (body['actorId'], body['idempotencyKey'])
    logical = digest(payload)
    def previous(db):
        row = db.execute('SELECT input,result FROM admissions WHERE actor=? AND key=?', key).fetchone()
        if row:
            if row['input'] != logical: raise Fault('conflict')
            return json.loads(row['result'])
    with wallet.db() as db:
        prior = previous(db)
        if prior: return prior  # Owner's historical receipt, not a fresh read of bytes.
    # No Wallet transaction across a source permission callback.
    query = request(wallet.config, 'connector.local', 'folder.capture',
        {k: payload[k] for k in ('sourceId', 'ownerId', 'entry', 'sha256')},
        subject=payload['ownerId'], grant=payload['sourceGrant'])
    query['deadline'] = body['deadline']
    captured = exchange(wallet.config, 'connector.local', query)
    if not set(readers) <= set(captured['inheritedReaders']):
        raise Fault('denied')
    snap = captured['snapshot']
    if snap['sha256'] != payload['sha256'] or snap['snapshotId'] != snap['sha256']:
        raise Fault('conflict')
    with wallet.db() as db:
        db.execute('BEGIN IMMEDIATE')
        prior = previous(db)
        if prior: return prior
        if timestamp(body['deadline']) <= time.time(): raise Fault('expired')
        resource, version = 'resource.' + uuid4().hex, 'version.' + uuid4().hex
        db.execute('INSERT INTO resources VALUES(?,?,?,1)', (resource, payload['entry'], version))
        db.execute('INSERT INTO versions VALUES(?,?,?,?,?)',
                   (version, resource, snap['snapshotId'], snap['sha256'], snap['size']))
        result = {k: payload[k] for k in ('sourceId','ownerId','entry','title','classification','allowedReaders')}
        result.update(resource=wallet.inspect(db, resource), inheritedReaders=captured['inheritedReaders'],
                      importedAt=utc(), mode='managed-copy')
        db.execute('INSERT INTO managed_items VALUES(?,?)', (resource, json.dumps(result)))
        db.execute('INSERT INTO admissions VALUES(?,?,?,?)', (*key, logical, json.dumps(result)))
        wallet.event(db, body['actorId'], 'item.admit', 'succeeded', resource)
        return result
