"""Upload a small UTF-8 document, then use the existing Wallet journey."""
import argparse
import base64
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('workbench_server',ROOT/'solutions/interactive/uc010/server.py')
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)


def bootstrap(directory):
    directory=server.managed.bootstrap(directory)
    path=directory/'connector.local.json';config=json.loads(path.read_text())
    config.update(allowUploads=True,implementationVersion='0.2.0');path.write_text(json.dumps(config,indent=2))
    return directory


def demo(workbench):
    data=b'Farmy upload test\nCrop: oats\n'
    payload={'name':'My field notes.txt','contentBase64':base64.b64encode(data).decode(),'key':'upload-demo'}
    result=workbench.action('owner','upload',payload)
    assert workbench.action('owner','upload',payload)==result
    assert workbench.preview(result['entry'])['text']==data.decode()
    item=workbench.action('owner','admit',dict(entry=result['entry'],sha256=result['sha256'],policy='restricted',key='admit-upload'))
    workbench.action('owner','grant',dict(id=item['id'],key='grant-upload'))
    assert workbench.action('consumer','read',{'id':item['id']})['text']==data.decode()
    workbench.action('owner','revoke',dict(id=item['id'],key='revoke-upload'))
    server.managed.core.expect_fault('denied',lambda:workbench.action('consumer','read',{'id':item['id']}))
    print('PASS uploaded exact bytes, retried without duplication, admitted, shared and revoked')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['launch','demo']);parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='farmy-uc011-') as temp:
        directory=bootstrap(temp)
        with server.managed.core.Processes(directory,server.managed.SERVICES):
            workbench=server.Workbench(directory,allow_uploads=True)
            if args.action=='demo':demo(workbench);return
            with server.Server(workbench,args.port) as http:
                print(f'Open http://127.0.0.1:{http.server_port}/#access={workbench.session["owner"]}',flush=True)
                print('Local file upload enabled · UTF-8 text, Markdown, CSV or email exports · 16 KiB maximum. Ctrl-C clears this temporary workspace.',flush=True)
                try:http.serve_forever()
                except KeyboardInterrupt:pass

if __name__=='__main__':main()
