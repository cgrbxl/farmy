"""Versioned local snapshots behind a mutually authenticated loopback API."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import time

from farmy_transport.monitoring import summarize
from farmy_transport.http import Fault, MAX_BYTES, PROFILE, descriptor, exchange, request, serve, timestamp


def safe_read(root_fd, relative):
    parts = relative.split('/')
    if relative.startswith('/') or '\\' in relative or any(p in ('', '.', '..') for p in parts):
        raise Fault('denied')
    directory = os.dup(root_fd)
    file_fd = None
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise Fault('denied')
        def read_all():
            chunks = []
            size = 0
            while True:
                block = os.read(file_fd, min(65536, MAX_BYTES + 1 - size))
                if not block:
                    break
                chunks.append(block)
                size += len(block)
                if size > MAX_BYTES:
                    raise Fault('conflict')
            return b''.join(chunks)
        first = read_all()
        middle = os.fstat(file_fd)
        os.lseek(file_fd, 0, os.SEEK_SET)
        second = read_all()
        after = os.fstat(file_fd)
        def signature(s):
            return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns
        if signature(before) != signature(middle) or signature(before) != signature(after) or first != second:
            raise Fault('conflict')
        return first
    except OSError as exc:
        raise Fault('denied') from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(directory)


class Connector:
    def __init__(self, config):
        self.config = config
        os.umask(0o077)
        self.state = Path(config['state'])
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.snapshots = self.state / 'snapshots'
        self.snapshots.mkdir(mode=0o700, exist_ok=True)
        self.root_fd = os.open(config['sourceRoot'], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS snapshots (digest TEXT PRIMARY KEY, size INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, time REAL, actor TEXT, event TEXT, outcome TEXT);
            ''')

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.state / 'connector.sqlite', timeout=3)
        connection.execute('PRAGMA journal_mode=WAL')
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def event(self, db, actor, event, outcome):
        db.execute('INSERT INTO audit(time,actor,event,outcome) VALUES(?,?,?,?)',
                   (time.time(), actor, event, outcome))

    def failure(self, actor, code):
        with self.db() as db:
            self.event(db, actor, 'request', code)

    def monitoring_summary(self):
        return summarize(self, [
            ('Snapshots', 'SELECT count(*) FROM snapshots'),
            ('Snapshot bytes', 'SELECT coalesce(sum(size),0) FROM snapshots'),
        ], ('wallet.local',))

    def descriptor(self):
        return descriptor(self.config, 'connectors',
                          {'farmy.storage': ['snapshot.capture', 'read.version']},
                          {'farmy.authorization': ['authorize.read']})

    def ready(self):
        try:
            exchange(self.config, 'wallet.local', path='/farmy/v0/health/live')
            return True
        except Fault:
            return False

    def capture(self, body):
        data = safe_read(self.root_fd, body['payload']['path'])
        digest = hashlib.sha256(data).hexdigest()
        dest = self.snapshots / digest
        if dest.exists():
            with dest.open('rb') as existing:
                stored = existing.read(MAX_BYTES + 1)
            if len(stored) > MAX_BYTES or hashlib.sha256(stored).hexdigest() != digest:
                raise Fault('unavailable')
        else:
            fd, name = tempfile.mkstemp(dir=self.snapshots)
            try:
                with os.fdopen(fd, 'wb') as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
                os.replace(name, dest)
            finally:
                if os.path.exists(name):
                    os.unlink(name)
        with self.db() as db:
            db.execute('INSERT OR IGNORE INTO snapshots VALUES(?,?)', (digest, len(data)))
            self.event(db, body['actorId'], 'snapshot.capture', 'succeeded')
        return {'snapshotId': digest, 'sha256': digest, 'size': len(data)}

    def authorize(self, body):
        query = request(self.config, 'wallet.local', 'authorize.read', {}, refs=body['inputRefs'],
                        grant=body['grantRef'], subject=body['subjectId'])
        query['deadline'] = body['deadline']
        return exchange(self.config, 'wallet.local', query)

    def read(self, body):
        if len(body['inputRefs']) != 1:
            raise Fault('invalid_request')
        decision = self.authorize(body)
        with self.db() as db:
            row = db.execute('SELECT size FROM snapshots WHERE digest=?', (decision['snapshotId'],)).fetchone()
            if row is None or row[0] != decision['size']:
                raise Fault('unavailable')
        try:
            with (self.snapshots / decision['snapshotId']).open('rb') as snapshot:
                data = snapshot.read(MAX_BYTES + 1)
        except OSError as exc:
            raise Fault('unavailable') from exc
        if len(data) > MAX_BYTES or len(data) != decision['size'] or hashlib.sha256(data).hexdigest() != decision['sha256']:
            raise Fault('unavailable')
        again = self.authorize(body)
        if again['snapshotId'] != decision['snapshotId'] or timestamp(body['deadline']) <= time.time():
            raise Fault('expired')
        with self.db() as db:
            self.event(db, body['actorId'], 'read.version', 'succeeded')
        return data

    def handle(self, peer, body):
        if body['operation'] == 'snapshot.capture':
            if (peer != 'wallet.local' or body['subjectId'] != 'owner'
                    or body['grantRef'] != 'grant.wallet-capture' or body['inputRefs']):
                raise Fault('denied')
            return self.capture(body)
        if body['operation'] == 'read.version':
            if peer != body['subjectId']:
                raise Fault('denied')
            return self.read(body)
        raise Fault('unsupported')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    serve(Connector(json.loads(Path(args.config).read_text())))
