"""Launch the first usable Farmy journey against real synthetic services."""
import argparse
import tempfile
import server


def demo(directory):
    workbench=server.Workbench(directory)
    document=workbench.preview('inspection.eml')
    admitted=workbench.action('owner','admit',{'entry':document['entry'],'sha256':document['sha256'],'policy':'restricted','key':'demo-admit'})
    resource=admitted['id']
    server.managed.core.expect_fault('denied',lambda:workbench.action('consumer','read',{'id':resource}))
    workbench.action('owner','grant',{'id':resource,'key':'demo-grant'})
    assert workbench.action('consumer','read',{'id':resource})['text']==server.managed.MAIL.decode()
    workbench=server.Workbench(directory)
    workbench.action('owner','revoke',{'id':resource,'key':'demo-revoke'})
    server.managed.core.expect_fault('denied',lambda:workbench.action('consumer','read',{'id':resource}))
    print('PASS browse, admit, denied read, grant, allowed read, bridge restart and revoke through workbench actions')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['launch','demo'])
    parser.add_argument('--port',type=int,default=0,help='Default: a free loopback port; use the printed URL.')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='farmy-uc010-') as temp:
        directory=server.managed.bootstrap(temp)
        with server.managed.core.Processes(directory,server.managed.SERVICES):
            if args.action=='demo': demo(directory); return
            workbench=server.Workbench(directory)
            with server.Server(workbench,args.port) as http:
                print(f'Open http://127.0.0.1:{http.server_port}/#access={workbench.session["owner"]}',flush=True)
                print('Real local services · synthetic documents · owner and consumer demo views. Ctrl-C ends and clears this session.',flush=True)
                try: http.serve_forever()
                except KeyboardInterrupt: pass


if __name__=='__main__': main()
