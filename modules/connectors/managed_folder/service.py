"""One source-governed flat folder plus separately governed immutable copies."""
import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import time

from farmy_transport.http import Fault, descriptor, exchange, request, serve, timestamp
from farmy_transport.monitoring import summarize

spec = importlib.util.spec_from_file_location('local_folder', Path(__file__).parents[1] / 'local_folder/service.py')
folder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(folder)


class ManagedFolder(folder.Connector):
    def __init__(self, config):
        super().__init__(config)
        with self.db() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS mount (source TEXT PRIMARY KEY, owner TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS releases (time REAL, consumer TEXT, source TEXT, entry TEXT, digest TEXT);''')

    def descriptor(self):
        return descriptor(self.config, 'connectors',
            {'farmy.folder-source': ['folder.attach', 'folder.list', 'folder.read', 'folder.capture'],
             'farmy.storage': ['read.version']},
            {'farmy.sources': ['source.authorize'], 'farmy.authorization': ['authorize.read']})

    def monitoring_summary(self):
        return summarize(self, [('Connected folders', 'SELECT count(*) FROM mount'),
            ('Managed snapshots', 'SELECT count(*) FROM snapshots'),
            ('Source reads', 'SELECT count(*) FROM releases')], ('wallet.local',))

    def authority(self, body, action='read'):
        payload = body['payload']
        query = request(self.config, 'wallet.local', 'source.authorize',
            {'sourceId': payload['sourceId'], 'ownerId': payload['ownerId'], 'action': action},
            subject=body['subjectId'], grant=body['grantRef'])
        query['deadline'] = body['deadline']
        exchange(self.config, 'wallet.local', query)
        if timestamp(body['deadline']) <= time.time():
            raise Fault('expired')

    def handle(self, peer, body):
        op, payload = body['operation'], body['payload']
        if op == 'read.version':
            return super().handle(peer, body)
        if op not in ('folder.attach', 'folder.list', 'folder.read', 'folder.capture'):
            raise Fault('unsupported')
        if body['inputRefs']:
            raise Fault('invalid_request')
        if op == 'folder.capture':
            if peer != 'wallet.local' or body['subjectId'] != payload['ownerId']:
                raise Fault('denied')
        elif peer != body['subjectId']:
            raise Fault('denied')
        self.authority(body, 'audit' if op == 'folder.attach' else 'read')
        with self.db() as db:
            if op == 'folder.attach':
                db.execute('BEGIN IMMEDIATE')
                existing = db.execute('SELECT source,owner FROM mount').fetchone()
                if existing and existing != (payload['sourceId'], payload['ownerId']):
                    raise Fault('conflict')
                db.execute('INSERT OR IGNORE INTO mount VALUES(?,?)', (payload['sourceId'], payload['ownerId']))
                return payload
            if not db.execute('SELECT 1 FROM mount WHERE source=? AND owner=?',
                              (payload['sourceId'], payload['ownerId'])).fetchone():
                raise Fault('denied')
        if op == 'folder.list':
            entries = []
            for name in os.listdir(self.root_fd):
                if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}', name):
                    try:
                        mode = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False).st_mode
                    except OSError:
                        raise Fault('conflict') from None
                    if stat.S_ISREG(mode): entries.append(name)
            if len(entries) > 100:
                raise Fault('unsupported')
            self.authority(body)
            with self.db() as db: self.event(db, peer, op, 'succeeded')
            return {'entries': sorted(entries)}
        data = self.read_source(payload['entry'])
        if len(data) > 16384:
            raise Fault('unsupported')
        digest = hashlib.sha256(data).hexdigest()
        if op == 'folder.capture' and digest != payload['sha256']:
            raise Fault('conflict')
        self.authority(body)
        with self.db() as db:
            db.execute('INSERT INTO releases VALUES(?,?,?,?,?)',
                       (time.time(), body['subjectId'], payload['sourceId'], payload['entry'], digest))
        if op == 'folder.capture':
            return {'snapshot': self.store_snapshot(data, body),
                    'inheritedReaders': self.config['sourceReaderCeiling']}
        return {'contentBase64': base64.b64encode(data).decode(), 'sha256': digest, 'size': len(data)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(ManagedFolder(json.loads(Path(parser.parse_args().config).read_text())))
