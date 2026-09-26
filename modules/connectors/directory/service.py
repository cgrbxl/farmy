"""Read-only bounded directory provider for the existing managed-item contracts."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

PARENT = Path(__file__).parents[1] / 'managed_folder'
sys.path.insert(0, str(PARENT))
spec = importlib.util.spec_from_file_location('managed_folder', PARENT / 'service.py')
managed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(managed)
from farmy_transport.http import Fault, descriptor, serve

TEXT_TYPES = {'.txt', '.md', '.csv', '.eml', '.json', '.geojson', '.xml'}


class Directory(managed.ManagedFolder):
    def __init__(self, config):
        if config.get('allowUploads'):
            raise ValueError('Directory sources are read-only')
        super().__init__(config)
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS entries (handle TEXT PRIMARY KEY, path TEXT UNIQUE NOT NULL)')

    def descriptor(self):
        return descriptor(self.config, 'connectors', {
            'farmy.folder-source': ['folder.attach', 'folder.list', 'folder.read', 'folder.capture'],
            'farmy.directory': ['folder.browse'], 'farmy.storage': ['read.version']},
            {'farmy.sources': ['source.authorize'], 'farmy.authorization': ['authorize.read']})

    def inventory(self):
        entries = []
        visited = 0
        def walk(fd, prefix='', depth=0):
            nonlocal visited
            if depth > 8:
                raise Fault('unsupported')
            with os.scandir(fd) as children:
                for child in children:
                    visited += 1
                    if visited > 2000:
                        raise Fault('unsupported')
                    if child.name.startswith('.'):
                        continue
                    path = prefix + child.name
                    if len(path) > 160 or any(ord(c) < 32 for c in path) or '\\' in path:
                        raise Fault('unsupported')
                    mode = child.stat(follow_symlinks=False).st_mode
                    if stat.S_ISDIR(mode):
                        nested = os.open(child.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                        try:
                            walk(nested, path + '/', depth + 1)
                        finally:
                            os.close(nested)
                    elif stat.S_ISREG(mode):
                        size = child.stat(follow_symlinks=False).st_size
                        reason = 'File exceeds 16 KiB' if size > 16384 else 'Unsupported preview format' if Path(path).suffix.lower() not in TEXT_TYPES else ''
                        entries.append(dict(entry='entry-' + hashlib.sha256(path.encode()).hexdigest(), path=path, size=size, reason=reason))
                        if len(entries) > 100:
                            raise Fault('unsupported')
        try:
            walk(self.root_fd)
        except OSError as exc:
            raise Fault('conflict') from exc
        with self.db() as db:
            for item in entries:
                old = db.execute('SELECT path FROM entries WHERE handle=?', (item['entry'],)).fetchone()
                if old and old[0] != item['path']:
                    raise Fault('conflict')
                db.execute('INSERT OR IGNORE INTO entries VALUES(?,?)', (item['entry'], item['path']))
        return sorted(entries, key=lambda item: item['path'])

    def read_source(self, handle):
        with self.db() as db:
            row = db.execute('SELECT path FROM entries WHERE handle=?', (handle,)).fetchone()
        if not row:
            raise Fault('not_found')
        if Path(row[0]).suffix.lower() not in TEXT_TYPES:
            raise Fault('unsupported')
        data = super().read_source(row[0])
        if len(data) > 16384:
            raise Fault('unsupported')
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise Fault('unsupported') from exc
        if any(ord(c) < 32 and c not in '\n\r\t' for c in text):
            raise Fault('unsupported')
        return data

    def handle(self, peer, body):
        if body['operation'] == 'folder.upload':
            raise Fault('denied')
        if body['operation'] not in ('folder.list', 'folder.browse'):
            return super().handle(peer, body)
        if peer != body['subjectId'] or body['inputRefs']:
            raise Fault('denied')
        self.authority(body)
        payload = body['payload']
        with self.db() as db:
            if not db.execute('SELECT 1 FROM mount WHERE source=? AND owner=?', (payload['sourceId'], payload['ownerId'])).fetchone():
                raise Fault('denied')
        entries = self.inventory()
        self.authority(body)
        with self.db() as db:
            self.event(db, peer, body['operation'], 'succeeded')
        return {'entries': entries if body['operation'] == 'folder.browse' else [item['entry'] for item in entries]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    serve(Directory(json.loads(Path(parser.parse_args().config).read_text())))
