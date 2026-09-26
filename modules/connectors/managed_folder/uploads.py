"""Bounded owner upload into the connector-owned source; never overwrites."""
import base64
import binascii
import hashlib
import json
import os
import re
import time
import unicodedata
from uuid import uuid4
from farmy_transport.http import Fault, timestamp


def upload(connector, body):
    payload=body['payload'];name=payload['name']
    if any(c in name for c in ('/','\\','\0')) or name in ('.','..'):
        raise Fault('invalid_request')
    extension=name.rsplit('.',1)[-1].lower()
    if extension not in ('txt','md','csv','eml'): raise Fault('unsupported')
    try:
        data=base64.b64decode(payload['contentBase64'],validate=True)
        decoded=data.decode('utf-8')
    except (ValueError,binascii.Error,UnicodeDecodeError): raise Fault('invalid_request') from None
    if len(data)>16384: raise Fault('unsupported')
    if any(ord(c)<32 and c not in '\n\r\t' for c in decoded): raise Fault('unsupported')
    sha=hashlib.sha256(data).hexdigest()
    stem=unicodedata.normalize('NFKD',name.rsplit('.',1)[0]).encode('ascii','ignore').decode()
    stem=re.sub('[^A-Za-z0-9_-]+','-',stem).strip('-_')[:35] or 'document'
    entry=f'{stem}-{sha}.{extension}'
    logical=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    receipt={'entry':entry,'sha256':sha,'size':len(data)}
    with connector.db() as db:
        db.execute('BEGIN IMMEDIATE')
        old=db.execute('SELECT digest,receipt FROM uploads WHERE key=?',(body['idempotencyKey'],)).fetchone()
        if old:
            if old[0]!=logical: raise Fault('conflict')
            return json.loads(old[1])
        if timestamp(body['deadline'])<=time.time(): raise Fault('expired')
        try:
            os.stat(entry,dir_fd=connector.root_fd,follow_symlinks=False)
            if connector.read_source(entry)!=data: raise Fault('conflict')
        except FileNotFoundError:
            if len(os.listdir(connector.root_fd))>=100: raise Fault('unsupported')
            temporary='.upload-'+uuid4().hex
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=connector.root_fd)
            try:
                with os.fdopen(fd,'wb') as stream:
                    stream.write(data);stream.flush();os.fsync(stream.fileno())
                try: os.link(temporary,entry,src_dir_fd=connector.root_fd,dst_dir_fd=connector.root_fd,follow_symlinks=False)
                except FileExistsError:
                    if connector.read_source(entry)!=data: raise Fault('conflict')
                os.fsync(connector.root_fd)
            finally: os.unlink(temporary,dir_fd=connector.root_fd)
        db.execute('INSERT INTO uploads VALUES(?,?,?)',(body['idempotencyKey'],logical,json.dumps(receipt)))
        connector.event(db,body['subjectId'],'folder.upload','succeeded')
    return receipt
