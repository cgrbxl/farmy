"""Local synthetic workbench: fixed actions, separate owner/consumer credentials."""
import base64
from datetime import datetime, timezone
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import re
import secrets
import sqlite3
import threading

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('managed_run', ROOT / 'solutions/managed-items/uc009/run.py')
managed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(managed)
Fault = managed.core.Fault
from farmy_transport.http import timestamp as bridge_time
ASSETS = {'/': ('index.html','text/html'), '/app.js': ('app.js','text/javascript'), '/style.css': ('style.css','text/css')}


class Workbench:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.lock = threading.Lock()
        self.path = self.directory / 'workbench.sqlite'
        with self.db() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS settings (name TEXT PRIMARY KEY, value TEXT);
                CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, metadata TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS permissions (resource TEXT PRIMARY KEY, permission TEXT NOT NULL, revision INTEGER, revoked INTEGER);
                CREATE TABLE IF NOT EXISTS actions (key TEXT PRIMARY KEY, digest TEXT NOT NULL, operation TEXT NOT NULL,
                    request TEXT NOT NULL, result TEXT);''')
            stored = db.execute("SELECT value FROM settings WHERE name='session'").fetchone()
            if stored:
                self.session = json.loads(stored[0])
            else:
                source = self.call('source.register', {'connectorId':'connector.local'}, key='key.workbench-source')
                self.call('folder.attach', managed.scope(source))
                grant = self.call('source.grant',dict(managed.scope(source),consumerId='owner',expiresAt=managed.core.utc(3600)))
                self.session = dict(source=source, sourceGrant=grant['grantId'], owner=secrets.token_urlsafe(32), consumer=secrets.token_urlsafe(32))
                db.execute('INSERT INTO settings VALUES(?,?)',('session',json.dumps(self.session)))

    def db(self):
        # This is the client's own receipt/catalogue state, never a service database.
        from contextlib import closing, contextmanager
        @contextmanager
        def connection():
            with closing(sqlite3.connect(self.path)) as db:
                with db: yield db
        return connection()

    def call(self, op, payload=None, **kwargs):
        return managed.call(self.directory,op,payload,**kwargs)

    def role(self, authorization):
        for role in ('owner','consumer'):
            if hmac.compare_digest(authorization.encode(),('Bearer '+self.session[role]).encode()): return role
        raise Fault('unauthenticated')

    def item(self, resource):
        with self.db() as db:
            row=db.execute('SELECT metadata FROM items WHERE id=?',(resource,)).fetchone()
        if not row: raise Fault('not_found')
        return json.loads(row[0])

    def permission(self, resource):
        with self.db() as db:
            row=db.execute('SELECT permission,revision,revoked FROM permissions WHERE resource=?',(resource,)).fetchone()
        return dict(grantId=row[0],revision=row[1],revoked=bool(row[2])) if row else None

    def state(self, role):
        with self.db() as db:
            rows=db.execute('SELECT id,metadata FROM items ORDER BY rowid').fetchall()
            pending=db.execute('SELECT request FROM actions WHERE result IS NULL').fetchone()
        if role == 'consumer':
            # Demo catalogue exposes only generic labels, never source metadata or credentials.
            return dict(role=role,items=[{'id':identity,'title':f'Demo document {i+1}'} for i,(identity,_) in enumerate(rows)])
        listing=self.call('folder.list',managed.scope(self.session['source']),grant=self.session['sourceGrant'])
        items=[]
        for identity,_ in rows:
            item=self.call('item.inspect',{'resourceId':identity})
            permission=self.permission(identity)
            item.update(id=identity, sharing='Revoked' if permission and permission['revoked'] else 'Granted (check as consumer)' if permission else 'Not granted')
            items.append(item)
        return dict(role=role,entries=listing['entries'],items=items,consumerToken=self.session['consumer'],
                    pending=json.loads(pending[0])['client'] if pending else None)

    def preview(self, entry):
        data=self.call('folder.read',dict(managed.scope(self.session['source']),entry=entry),grant=self.session['sourceGrant'])
        return dict(entry=entry,text=base64.b64decode(data['contentBase64']).decode('utf-8',errors='replace'),sha256=data['sha256'],size=data['size'])

    def read(self, role, resource):
        item=self.item(resource)
        permission=self.permission(resource)
        identity='reader'
        if role=='owner':
            identity='owner'
            expiry=datetime.fromtimestamp(bridge_time(item['importedAt'])+3600,timezone.utc).isoformat().replace('+00:00','Z')
            ref=item['resource']
            permission=self.call('grant.issue',dict(resourceId=ref['resourceId'],versionId=ref['versionId'],
                subjectId='owner',expiresAt=expiry,purpose='uc001.read'),refs=managed.core.refs(ref),key='key.owner-read-'+resource)
        # A missing grant still reaches the real authorisation boundary.
        data=managed.core.read(self.directory,item['resource'],permission or {'grantId':'grant.not-issued'},identity)
        return {'text':data.decode('utf-8',errors='replace'), 'decision':'Access allowed by Wallet'}

    def mutate(self, action, payload):
        key=payload['key']
        if not isinstance(key,str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,64}',key): raise Fault('invalid_request')
        digest=hashlib.sha256(json.dumps([action,payload],sort_keys=True).encode()).hexdigest()
        with self.db() as db:
            old=db.execute('SELECT digest,operation,request,result FROM actions WHERE key=?',(key,)).fetchone()
            if old:
                if old[0]!=digest: raise Fault('conflict')
                op,query,result=old[1],json.loads(old[2])['query'],old[3]
                if result: return json.loads(result)
            else:
                if db.execute('SELECT 1 FROM actions WHERE result IS NULL').fetchone(): raise Fault('conflict')
                if action=='admit':
                    if payload['policy'] not in ('private','restricted'): raise Fault('invalid_request')
                    op='item.admit'
                    data=dict(managed.scope(self.session['source']),entry=payload['entry'],sha256=payload['sha256'],
                        sourceGrant=self.session['sourceGrant'],title=payload['entry'],classification=payload['policy'],
                        allowedReaders=['owner'] if payload['policy']=='private' else ['owner','reader'])
                    query={'payload':data}
                else:
                    item=self.item(payload['id']); resource=item['resource']; permission=self.permission(payload['id'])
                    if action=='grant':
                        # Require revocation before replacement so one revoke covers every issued live grant.
                        if permission and not permission['revoked']: raise Fault('conflict')
                        op='grant.issue'
                        query={'payload':dict(resourceId=resource['resourceId'],versionId=resource['versionId'],subjectId='reader',expiresAt=managed.core.utc(3600),purpose='uc001.read'), 'refs':managed.core.refs(resource)}
                    else:
                        if not permission: raise Fault('not_found')
                        op='grant.revoke'
                        query={'payload':{'grantId':permission['grantId']},'revision':permission['revision']}
                db.execute('INSERT INTO actions VALUES(?,?,?,?,NULL)',(key,digest,op,json.dumps({'query':query,'client':{'action':action,'payload':payload}})))
        # Commit intent first: retries use exactly the same expiry, grant and operation key.
        try:
            result=self.call(op,key='key.ui-'+key,**query)
        except Fault as exc:
            if exc.code in ('denied','invalid_request','unsupported','not_found','expired','conflict'):
                with self.db() as db: db.execute('DELETE FROM actions WHERE key=?',(key,))
            raise
        with self.db() as db:
            if action=='admit':
                db.execute('INSERT OR IGNORE INTO items VALUES(?,?)',(result['resource']['resourceId'],json.dumps(result)))
            elif action=='grant':
                db.execute('INSERT OR REPLACE INTO permissions VALUES(?,?,?,0)',(payload['id'],result['grantId'],result['revision']))
            else:
                db.execute('UPDATE permissions SET revision=?,revoked=1 WHERE resource=?',(result['revision'],payload['id']))
            # Browser receives a receipt without reusable service-grant identifiers.
            receipt={'id':result['resource']['resourceId']} if action=='admit' else {'id':payload['id'],'status':'Granted' if action=='grant' else 'Revoked'}
            db.execute('UPDATE actions SET result=? WHERE key=?',(json.dumps(receipt),key))
        return receipt

    def action(self, role, action, payload):
        fields={'preview':{'entry'},'read':{'id'},'admit':{'entry','sha256','policy','key'},'grant':{'id','key'},'revoke':{'id','key'}}
        if action not in fields or not isinstance(payload,dict) or set(payload)!=fields[action] or not all(isinstance(v,str) for v in payload.values()):
            raise Fault('invalid_request')
        if action=='read': return self.read(role,payload['id'])
        if role!='owner': raise Fault('denied')
        if action=='preview': return self.preview(payload['entry'])
        return self.mutate(action,payload)


class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, workbench, port=0):
        self.workbench=workbench
        super().__init__(('127.0.0.1',port),Handler)
    def handle_error(self,*args): pass


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup(); self.connection.settimeout(5)
    def log_message(self,*args): pass
    def send(self,status,data,media='application/json'):
        raw=data if isinstance(data,bytes) else json.dumps(data).encode()
        self.send_response(status)
        for k,v in {'Content-Type':media+'; charset=utf-8','Content-Length':str(len(raw)), 'Cache-Control':'no-store',
            'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Connection':'close',
            'Content-Security-Policy':"default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"}.items(): self.send_header(k,v)
        self.end_headers(); self.wfile.write(raw)
    def dispatch(self,post=False):
        origin=f'http://127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host')!=origin[7:] or self.headers.get('Origin',None if post else origin)!=origin:
            self.send(403,{'error':'origin_denied'}); return
        if not post and self.path in ASSETS:
            name,media=ASSETS[self.path]; self.send(200,(ROOT/'dashboard/workbench'/name).read_bytes(),media); return
        try:
            role=self.server.workbench.role(self.headers.get('Authorization',''))
            if post:
                if self.path!='/api/action': self.send(404,{'error':'not_found'}); return
                if self.headers.get('Content-Type')!='application/json' or self.headers.get('Transfer-Encoding'):
                    raise Fault('invalid_request')
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=4096: raise Fault('invalid_request')
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict) or set(data)!={'action','payload'}: raise Fault('invalid_request')
            elif self.path!='/api/state': self.send(404,{'error':'not_found'}); return
            with self.server.workbench.lock:
                result=self.server.workbench.action(role,data['action'],data['payload']) if post else self.server.workbench.state(role)
            self.send(200,result)
        except Fault as exc:
            self.send({'unauthenticated':401,'denied':403,'not_found':404,'conflict':409,'unavailable':503}.get(exc.code,400),{'error':exc.code})
        except (ValueError,TypeError,KeyError): self.send(400,{'error':'invalid_request'})
        except Exception: self.send(503,{'error':'unavailable'})
    def do_GET(self): self.dispatch()
    def do_POST(self): self.dispatch(True)
    def do_PUT(self): self.send(405,{'error':'unsupported'})
    do_DELETE=do_PATCH=do_PUT
