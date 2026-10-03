"""One-shot trusted local processor. No SDK, file reads or network in its implementation."""
import base64
import hashlib
import json
import re
import sys

# This independent parser deliberately does not import the producer's validators.
def execute(query, receiver="processor.local"):
    if not isinstance(query,dict) or set(query)!={'contract','operation','requestId','payload'}:raise ValueError('invalid request')
    if query['contract']!='farmy.processing.text/0.1-draft' or query['operation']!='text.stats':raise ValueError('unsupported contract')
    if not isinstance(query['requestId'],str) or not re.fullmatch('[A-Za-z0-9_-]{8,100}',query['requestId']):raise ValueError('invalid request ID')
    payload=query['payload']
    if not isinstance(payload,dict) or set(payload)!={'receiverId','purpose','evidence'}:raise ValueError('invalid payload')
    if payload['receiverId']!=receiver or payload['purpose']!='text-statistics':raise ValueError('wrong receiver or purpose')
    evidence=payload['evidence']
    if set(evidence)!={'schema','resource','contentBase64'} or evidence['schema']!='farmy.evidence/0.1-draft':raise ValueError('invalid evidence')
    ref=evidence['resource']
    if set(ref)!={'id','sha256','size','mediaType'} or ref['mediaType']!='text/plain;charset=utf-8' or type(ref['size']) is not int or not 0<=ref['size']<=16384:raise ValueError('invalid reference')
    data=base64.b64decode(evidence['contentBase64'],validate=True)
    if base64.b64encode(data).decode()!=evidence['contentBase64'] or len(data)!=ref['size'] or hashlib.sha256(data).hexdigest()!=ref['sha256'] or ref['id']!='sha256:'+ref['sha256']:raise ValueError('digest mismatch')
    text=data.decode('utf-8')
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('unsupported text')
    return dict(contract=query['contract'],operation=query['operation'],requestId=query['requestId'],producerId=receiver,input=ref,
        output=dict(bytes=len(data),lines=data.count(b'\n')+int(bool(data) and not data.endswith(b'\n')),words=len(re.findall(r'[^ \t\r\n]+',text))))

def pairs(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('duplicate field')
        result[key]=value
    return result

if __name__=='__main__':
    try:
        data=sys.stdin.buffer.read(65537)
        if len(data)>65536:raise ValueError('oversized request')
        print(json.dumps(execute(json.loads(data,object_pairs_hook=pairs)),sort_keys=True))
    except (ValueError,TypeError,KeyError,RecursionError):
        print('Invalid or incompatible processing request.',file=sys.stderr);sys.exit(1)
