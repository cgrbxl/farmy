"""Optional development persistence/transport helpers; no domain policy."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time

from .http import Fault, exchange, request, timestamp


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class LocalService:
    schema = ''
    dependencies = ()

    def __init__(self, config):
        self.config = config
        os.umask(0o077)
        self.state = Path(config['state'])
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self.db() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, time REAL, actor TEXT, event TEXT, outcome TEXT);' + self.schema)

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.state / 'state.sqlite', timeout=3)
        connection.row_factory = sqlite3.Row
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

    def ready(self):
        try:
            for target in self.dependencies:
                exchange(self.config, target, path='/farmy/v0/health/live')
            return True
        except Fault:
            return False

    def remote(self, target, operation, payload, body, **kwargs):
        query = request(self.config, target, operation, payload, refs=body['inputRefs'], **kwargs)
        query['deadline'] = body['deadline']
        query['correlationId'] = body['correlationId']
        return exchange(self.config, target, query)

    def access(self, peer, body):
        if peer != body['subjectId'] or len(body['inputRefs']) != 1:
            raise Fault('denied')
        return self.remote('wallet.local', 'access.check',
                           {'operation': body['operation'], 'purpose': body['purpose']}, body,
                           subject=peer, grant=body['grantRef'])

    def deadline(self, body):
        if timestamp(body['deadline']) <= time.time():
            raise Fault('expired')
