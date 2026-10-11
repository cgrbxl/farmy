"""Local draft-only messaging planner; no provider, network, or source-file access."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from uuid import uuid4

CHANNELS=('email','sms','whatsapp','signal')
class Invalid(ValueError):pass
class Conflict(ValueError):pass


def text(value, limit=200):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or any(ord(c)<32 and c not in '\n\t' for c in value):raise Invalid('Invalid text')
    return value.strip()


def address(value):
    value=text(value)
    if any(c.isspace() for c in value):raise Invalid('Use an exact provider identifier without spaces')
    return value


class Planner:
    def __init__(self, directory):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        with self.db() as db:
            if db.execute('PRAGMA user_version').fetchone()[0] not in (0,1):raise Invalid('Unsupported planner schema')
            db.executescript('''CREATE TABLE IF NOT EXISTS channels(id TEXT PRIMARY KEY, revision INTEGER, senders TEXT, recipients TEXT);
            CREATE TABLE IF NOT EXISTS rules(id TEXT PRIMARY KEY, channel TEXT, recipient TEXT, topic TEXT, content TEXT, period INTEGER, next_due INTEGER, paused INTEGER, revision INTEGER);
            CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY, rule_id TEXT, due INTEGER, channel TEXT, recipient TEXT, topic TEXT, content TEXT, created INTEGER, UNIQUE(rule_id,due));
            CREATE TABLE IF NOT EXISTS requests(key TEXT PRIMARY KEY, digest TEXT, result TEXT);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, time INTEGER, action TEXT, reference TEXT);''')
            db.execute('PRAGMA user_version=1')
            for channel in CHANNELS:db.execute('INSERT OR IGNORE INTO channels VALUES(?,0,?,?)',(channel,'[]','[]'))

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.directory/'planner.sqlite',timeout=5);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()

    def snapshot(self):
        with self.db() as db:
            channels=[dict(row,senders=json.loads(row['senders']),recipients=json.loads(row['recipients'])) for row in db.execute('SELECT * FROM channels ORDER BY rowid')]
            rules=[dict(row) for row in db.execute('SELECT * FROM rules ORDER BY rowid')]
            drafts=[dict(row) for row in db.execute('SELECT * FROM drafts ORDER BY created DESC,rowid DESC LIMIT 50')]
            audit=[dict(row) for row in db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 30')]
        return dict(channels=channels,rules=rules,drafts=drafts,audit=audit,mode='local-drafts-only')

    def check_sender(self, payload):
        if not isinstance(payload,dict) or set(payload)!={'channel','sender'} or payload['channel'] not in CHANNELS:raise Invalid('Invalid sender check')
        sender=address(payload['sender'])
        with self.db() as db:row=db.execute('SELECT senders,revision FROM channels WHERE id=?',(payload['channel'],)).fetchone()
        # Only a metadata decision. No body is received, retained or passed to AI.
        return dict(allowed=sender in json.loads(row['senders']),revision=row['revision'])

    def change(self, action, payload, now=None):
        now=int(time.time() if now is None else now)
        fields={'channel.save':{'key','channel','revision','senders','recipients'},
                'rule.create':{'key','channel','recipient','topic','content','period','firstDue'},
                'rule.pause':{'key','id','revision','paused'}}
        if action not in fields or not isinstance(payload,dict) or set(payload)!=fields[action]:raise Invalid('Invalid fields')
        key=payload['key']
        if not isinstance(key,str) or not re.fullmatch('[A-Za-z0-9-]{1,64}',key):raise Invalid('Invalid request key')
        logical=hashlib.sha256(json.dumps([action,payload],sort_keys=True).encode()).hexdigest()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            previous=db.execute('SELECT digest,result FROM requests WHERE key=?',(key,)).fetchone()
            if previous:
                if previous['digest']!=logical:raise Conflict('Request key reused')
                return json.loads(previous['result'])
            if db.execute('SELECT count(*) FROM requests').fetchone()[0]>=10000:raise Invalid('Request history limit reached; maintenance required')
            if action=='channel.save':
                if payload['channel'] not in CHANNELS or type(payload['revision']) is not int:raise Invalid('Invalid channel')
                row=db.execute('SELECT * FROM channels WHERE id=?',(payload['channel'],)).fetchone()
                if payload['revision']!=row['revision']:raise Conflict('Channel changed')
                lists={}
                for field in ('senders','recipients'):
                    values=payload[field]
                    if not isinstance(values,list) or len(values)>50:raise Invalid('At most 50 identifiers')
                    lists[field]=sorted(set(address(v) for v in values))
                db.execute('UPDATE channels SET senders=?,recipients=?,revision=revision+1 WHERE id=?',(json.dumps(lists['senders']),json.dumps(lists['recipients']),payload['channel']))
                for rule in db.execute('SELECT id,recipient FROM rules WHERE channel=? AND paused=0',(payload['channel'],)).fetchall():
                    if rule['recipient'] not in lists['recipients']:db.execute('UPDATE rules SET paused=1,revision=revision+1 WHERE id=?',(rule['id'],))
                result=dict(id=payload['channel'],revision=row['revision']+1)
            elif action=='rule.create':
                if payload['channel'] not in CHANNELS or type(payload['period']) is not int or payload['period'] not in (3600,86400,604800):raise Invalid('Unsupported interval')
                due=payload['firstDue']
                if type(due) is not int or not now-60<=due<=now+366*86400:raise Invalid('First run must be within one year')
                recipient=address(payload['recipient']);topic=text(payload['topic'],120);content=payload['content'];text(content,2000)
                approved=json.loads(db.execute('SELECT recipients FROM channels WHERE id=?',(payload['channel'],)).fetchone()[0])
                if recipient not in approved:raise Invalid('Recipient must be approved first')
                if db.execute('SELECT count(*) FROM rules').fetchone()[0]>=50:raise Invalid('At most 50 rules')
                identity='rule.'+uuid4().hex
                db.execute('INSERT INTO rules VALUES(?,?,?,?,?,?,?,0,1)',(identity,payload['channel'],recipient,topic,content,payload['period'],due))
                result=dict(id=identity,revision=1)
            else:
                if not isinstance(payload['id'],str) or type(payload['revision']) is not int or type(payload['paused']) is not bool:raise Invalid('Invalid rule change')
                row=db.execute('SELECT * FROM rules WHERE id=?',(payload['id'],)).fetchone()
                if row is None or row['revision']!=payload['revision']:raise Conflict('Rule changed')
                if not payload['paused']:
                    approved=json.loads(db.execute('SELECT recipients FROM channels WHERE id=?',(row['channel'],)).fetchone()[0])
                    if row['recipient'] not in approved:raise Invalid('Recipient is no longer approved')
                db.execute('UPDATE rules SET paused=?,revision=revision+1 WHERE id=?',(int(payload['paused']),row['id']))
                result=dict(id=row['id'],revision=row['revision']+1)
            db.execute('INSERT INTO requests VALUES(?,?,?)',(key,logical,json.dumps(result)))
            db.execute('INSERT INTO audit(time,action,reference) VALUES(?,?,?)',(now,action,result['id']))
            return result

    def tick(self, now=None):
        now=int(time.time() if now is None else now)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            for row in db.execute('SELECT * FROM rules WHERE paused=0 AND next_due<=?',(now,)).fetchall():
                approved=json.loads(db.execute('SELECT recipients FROM channels WHERE id=?',(row['channel'],)).fetchone()[0])
                if row['recipient'] not in approved:
                    db.execute('UPDATE rules SET paused=1,revision=revision+1 WHERE id=?',(row['id'],));continue
                # Coalesce downtime into the most recent slot; do not flood old drafts.
                due=row['next_due']+((now-row['next_due'])//row['period'])*row['period']
                db.execute('INSERT OR IGNORE INTO drafts VALUES(?,?,?,?,?,?,?,?)',('draft.'+uuid4().hex,row['id'],due,row['channel'],row['recipient'],row['topic'],row['content'],now))
                db.execute('UPDATE rules SET next_due=? WHERE id=?',(due+row['period'],row['id']))
                db.execute('INSERT INTO audit(time,action,reference) VALUES(?,?,?)',(now,'draft.created',row['id']))
            # Explicit bounded local retention: latest 200 drafts and 500 audit events.
            db.execute('DELETE FROM drafts WHERE rowid NOT IN (SELECT rowid FROM drafts ORDER BY created DESC,rowid DESC LIMIT 200)')
            db.execute('DELETE FROM audit WHERE id NOT IN (SELECT id FROM audit ORDER BY id DESC LIMIT 500)')
