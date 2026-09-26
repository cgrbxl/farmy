"""A stopped workspace must have no in-flight client mutation."""
import importlib.util
import json
from pathlib import Path
import threading
import unittest
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('persistent_runtime', ROOT/'runtime/local/farmy.py')
runtime = importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)


class Shutdown(unittest.TestCase):
    def test_shutdown_drains_an_inflight_request(self):
        entered=threading.Event();release=threading.Event();closed=threading.Event()
        class Client:
            allow_uploads=False
            lock=threading.Lock()
            def role(self, _):return 'owner'
            def action(self, *_):
                entered.set()
                if not release.wait(5):raise RuntimeError('Test timed out')
                return {'committed':True}
        http=runtime.Server(Client())
        serving=threading.Thread(target=http.serve_forever,daemon=True);serving.start()
        origin=f'http://127.0.0.1:{http.server_port}'
        result=[]
        def request():
            req=urllib.request.Request(origin+'/api/action',data=json.dumps({'action':'test','payload':{}}).encode(),
                headers={'Origin':origin,'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=8) as response:result.append(json.load(response))
        caller=threading.Thread(target=request,daemon=True);caller.start()
        try:
            self.assertTrue(entered.wait(3))
            def close():
                http.shutdown();http.server_close();closed.set()
            closer=threading.Thread(target=close,daemon=True);closer.start()
            self.assertFalse(closed.wait(.8),'Server released state while a mutation was still running')
            release.set();caller.join(5);closer.join(5)
            self.assertTrue(closed.is_set());self.assertEqual(result,[{'committed':True}])
        finally:
            release.set();http.shutdown();http.server_close()


if __name__=='__main__':unittest.main()
