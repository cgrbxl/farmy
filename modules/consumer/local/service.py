"""Independent local demo consumer: private receipts, own key and browser origin.

The owner sends grant receipts over mTLS. Browser reads are performed by this
consumer's mTLS identity; no owner service database or owner key is opened here.
"""
import argparse
import hmac
import importlib.util
import json
from pathlib import Path
import threading

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('consumer_ui', ROOT/'solutions/interactive/uc010/server.py')
ui = importlib.util.module_from_spec(spec);spec.loader.exec_module(ui)
from farmy_transport.http import Fault, descriptor, exchange, request, serve
from farmy_transport.local import LocalService, digest


class Consumer(LocalService):
    schema = '''CREATE TABLE IF NOT EXISTS receipts(resource TEXT PRIMARY KEY, payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS offers(actor TEXT, key TEXT, digest TEXT, PRIMARY KEY(actor,key));'''
    dependencies = ('wallet.local','connector.local')
    allow_uploads = False

    def __init__(self, config):
        super().__init__(config)
        self.lock = threading.Lock()

    def descriptor(self):
        return descriptor(self.config, 'exchange', {'farmy.consumer-inbox':['consumer.offer']},
                          {'farmy.storage':['read.version']})

    def handle(self, peer, body):
        if peer != 'owner' or body['subjectId'] != 'owner' or body['operation'] != 'consumer.offer' or body['grantRef'] != 'grant.owner-bootstrap':
            raise Fault('denied')
        payload = body['payload'];logical = digest(payload)
        if body['inputRefs'] != ui.managed.core.refs(payload['resource']): raise Fault('invalid_request')
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT digest FROM offers WHERE actor=? AND key=?',(peer,body['idempotencyKey'])).fetchone()
            if old:
                if old['digest'] != logical: raise Fault('conflict')
            else:
                self.deadline(body)
                db.execute('INSERT OR REPLACE INTO receipts VALUES(?,?)',(payload['resource']['resourceId'],json.dumps(payload)))
                db.execute('INSERT INTO offers VALUES(?,?,?)',(peer,body['idempotencyKey'],logical))
                self.event(db,peer,'consumer.offer','accepted')
        return dict(resourceId=payload['resource']['resourceId'],accepted=True)

    def role(self, authorization):
        if not hmac.compare_digest(authorization.encode(),('Bearer '+self.config['browserToken']).encode()):
            raise Fault('unauthenticated')
        return 'consumer'

    def view_state(self, role):
        with self.db() as db:
            rows=db.execute('SELECT resource FROM receipts ORDER BY rowid').fetchall()
        return dict(role='consumer',persistent=True,runtimeVersion=self.config['runtimeVersion'],
                    independentConsumer=True,identity=self.config['publicIdentity'],
                    items=[dict(id=row['resource'],title=f'Shared document {i+1}') for i,row in enumerate(rows)])

    def action(self, role, action, payload):
        if action != 'read': raise Fault('denied')
        if not isinstance(payload,dict) or set(payload)!={'id'} or not isinstance(payload['id'],str): raise Fault('invalid_request')
        with self.db() as db:
            row=db.execute('SELECT payload FROM receipts WHERE resource=?',(payload['id'],)).fetchone()
        if not row: raise Fault('not_found')
        receipt=json.loads(row['payload'])
        query=request(self.config,'connector.local','read.version',{},refs=ui.managed.core.refs(receipt['resource']),
                      grant=receipt['grantId'])
        data=exchange(self.config,'connector.local',query)
        return dict(text=data.decode('utf-8',errors='replace'),decision='Access allowed by Wallet')


class BrowserClient:
    allow_uploads=False
    def __init__(self, consumer):
        self.consumer=consumer
        self.lock=consumer.lock
    def role(self, authorization):return self.consumer.role(authorization)
    def state(self, role):return self.consumer.view_state(role)
    def action(self, role, action, payload):return self.consumer.action(role,action,payload)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);args=parser.parse_args()
    app=Consumer(json.loads(Path(args.config).read_text()))
    # Bind browser before declaring TLS readiness; a conflict fails the composition.
    with ui.Server(BrowserClient(app),app.config['browserPort']) as browser:
        threading.Thread(target=browser.serve_forever,daemon=True).start()
        try:serve(app)
        finally:browser.shutdown()
