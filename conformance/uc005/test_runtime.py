"""Read-only monitoring across real mTLS services and a local browser bridge."""
import errno
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uc005_run', ROOT / 'solutions/operations/uc005/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from farmy_transport.http import Fault, exchange, request


class PortSelection(unittest.TestCase):
    def test_automatic_fallback_preserves_existing_listener(self):
        with run.bridge.Server({}, 0) as occupied:
            port = occupied.server_port
            with patch.object(run.bridge, 'DEFAULT_PORT', port):
                with run.bridge.bind_server({}) as fallback:
                    self.assertNotEqual(fallback.server_port, port)
                    self.assertEqual(fallback.server_address[0], '127.0.0.1')
                with self.assertRaisesRegex(SystemExit, f'Port {port} is already in use'):
                    run.bridge.bind_server({}, port)
                self.assertEqual(occupied.socket.getsockname()[1], port)
        with patch.object(run.bridge, 'DEFAULT_PORT', port):
            with run.bridge.bind_server({}) as preferred:
                self.assertEqual(preferred.server_port, port)
        with run.bridge.bind_server({}, 0) as automatic:
            self.assertGreater(automatic.server_port, 0)

    def test_other_bind_errors_are_not_hidden(self):
        error = OSError(errno.EACCES, 'Permission denied')
        with patch.object(run.bridge, 'Server', side_effect=error) as constructor:
            with self.assertRaises(OSError) as caught:
                run.bridge.bind_server({})
            self.assertIs(caught.exception, error)
            constructor.assert_called_once()


class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='farmy-monitor-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = run.bootstrap(cls.temp.name)
        cls.processes = run.core.Processes(cls.directory, run.SERVICES)
        cls.addClassCleanup(cls.processes.__exit__, None, None, None)
        cls.processes.__enter__()
        run.seed(cls.directory)
        cls.config = run.core.config(cls.directory,'monitor.local')
        cls.server = run.bridge.Server(cls.config,0)
        cls.addClassCleanup(cls.server.server_close)
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.addClassCleanup(cls.server.shutdown)

    def http(self,path='/api/snapshot',token=True,headers=None,method='GET'):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=15)
        h={'Authorization':'Bearer '+self.config['browserToken']} if token else {}
        h.update(headers or {})
        conn.request(method,path,headers=h)
        reply=conn.getresponse();data=reply.read();status=reply.status;returned=dict(reply.getheaders());conn.close()
        return status,data,returned

    def node(self,state,identity):
        return next(n for n in state['nodes'] if n['instanceId']==identity)

    def deny(self,code,action):
        with self.assertRaises(Fault) as caught:action()
        self.assertEqual(caught.exception.code,code)

    def test_01_public_summaries_match_seeded_contents(self):
        status,raw,headers=self.http()
        self.assertEqual(status,200)
        state=json.loads(raw)
        self.assertEqual(len(state['nodes']),8)
        self.assertTrue(all(n['status']=='available' for n in state['nodes']))
        counts=lambda identity:{c['label']:c['value'] for c in self.node(state,identity)['counts']}
        self.assertEqual(counts('wallet.local')['Documents'],1)
        self.assertEqual(counts('wallet.local')['Sources'],1)
        self.assertEqual(counts('sensor.local')['Observations'],3)
        self.assertEqual(counts('knowledge.local')['Evidence entries'],1)
        self.assertEqual(counts('workflow.local')['Succeeded jobs'],1)
        self.assertEqual(counts('model.local')['Model invocations'],0)
        self.assertEqual(counts('assistance.local')['Accepted answers'],0)
        self.assertEqual(state['adapters'][0]['status'],'configuration only')
        self.assertEqual(state['planned'][0]['status'],'not deployed')
        for forbidden in [b'crop: wheat',b'BEGIN PRIVATE KEY',str(self.directory).encode(),self.config['browserToken'].encode(),b'report.txt']:
            self.assertNotIn(forbidden,raw)
        self.assertEqual(headers['Cache-Control'],'no-store')

    def test_02_summary_permission_is_receiver_enforced(self):
        for identity,code in [('reader','denied'),('owner','denied'),('denied','denied'),('unknown','unauthenticated')]:
            for target in run.SERVICES:
                with self.subTest(identity=identity,target=target):
                    self.deny(code,lambda:exchange(run.core.config(self.directory,identity),target,path='/farmy/v0/monitor/summary'))

    def test_03_monitor_identity_cannot_mutate_or_read_raw_content(self):
        body=request(self.config,'wallet.local','resource.register',{'path':'report.txt'})
        self.deny('denied',lambda:exchange(self.config,'wallet.local',body))
        body=request(self.config,'knowledge.local','evidence.query',{'field':'crop'})
        self.deny('denied',lambda:exchange(self.config,'knowledge.local',body))
        body=request(self.config,'assistance.local','answer.create',{'question':'Which crop is recorded?',
            'routeId':run.answer.ROUTE,'knowledgeGrant':'missing','modelGrant':'missing','modelEvidenceGrant':'missing'})
        self.deny('denied',lambda:exchange(self.config,'assistance.local',body))

    def test_04_browser_requires_token_and_same_origin(self):
        self.assertEqual(self.http(token=False)[0],401)
        self.assertEqual(self.http(headers={'Authorization':'Bearer wrong'})[0],401)
        self.assertEqual(self.http(headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.http(headers={'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.http(method='POST')[0],405)
        self.assertEqual(self.http(path='/api/snapshot?target=wallet.local')[0],404)
        status,body,headers=self.http(path='/',token=False)
        self.assertEqual(status,200)
        self.assertNotIn(self.config['browserToken'].encode(),body)
        self.assertNotIn('Access-Control-Allow-Origin',headers)
        self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
        for path in ['/../README.md','/monitor.local.json','/.farmy','/api/request']:
            self.assertEqual(self.http(path=path)[0],404)

    def test_05_unavailable_module_clears_counts_and_recovers(self):
        self.processes.stop('knowledge.local')
        try:
            state=json.loads(self.http()[1]);node=self.node(state,'knowledge.local')
            self.assertEqual(node['status'],'unavailable');self.assertEqual(node['counts'],[])
            self.assertEqual(node['activity'],[])
            self.assertEqual(self.node(state,'wallet.local')['status'],'available')
            self.assertEqual(self.node(state,'workflow.local')['status'],'degraded')
        finally:self.processes.start('knowledge.local')
        node=self.node(json.loads(self.http()[1]),'knowledge.local')
        self.assertEqual(node['status'],'available');self.assertEqual(node['counts'][0]['value'],1)

    def test_06_monitor_access_removal_hides_summary(self):
        path=self.directory/'knowledge.local.json';saved=path.read_text()
        try:
            config=json.loads(saved);config['monitorSubjects']=[];path.write_text(json.dumps(config))
            self.processes.stop('knowledge.local');self.processes.start('knowledge.local')
            node=self.node(json.loads(self.http()[1]),'knowledge.local')
            self.assertEqual(node['status'],'available');self.assertEqual(node['summaryStatus'],'denied')
            self.assertEqual(node['counts'],[]);self.assertEqual(node['activity'],[])
        finally:
            path.write_text(saved);self.processes.stop('knowledge.local');self.processes.start('knowledge.local')

    def test_07_new_content_and_limited_activity_are_observed(self):
        source=run.sensor.register(self.directory)
        run.sensor.append(self.directory,source,21)
        node=self.node(json.loads(self.http()[1]),'sensor.local')
        self.assertEqual(next(c['value'] for c in node['counts'] if c['label']=='Observations'),4)
        self.assertLessEqual(len(node['activity']),6)
        self.assertEqual(set(node['activity'][0]),{'at','event','outcome'})
        self.assertIn('wallet.local',node['dependencies'])
        self.assertNotIn('connectionsVerified',node)

    def test_08_bridge_lifecycle_does_not_own_services(self):
        server=run.bridge.Server(self.config,0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        server.shutdown();server.server_close();thread.join()
        for target in run.SERVICES:
            self.assertEqual(exchange(self.config,target,path='/farmy/v0/health/live')['status'],'ready')

    def test_09_existing_compositions_do_not_enable_monitoring(self):
        with tempfile.TemporaryDirectory(prefix='farmy-no-monitor-') as directory:
            directory=run.core.bootstrap(directory)
            with run.core.Processes(directory):
                config=run.core.config(directory)
                self.deny('denied',lambda:exchange(config,'wallet.local',path='/farmy/v0/monitor/summary'))
                info=exchange(config,'wallet.local',path='/farmy/v0/descriptor')
                self.assertNotIn('farmy.monitoring',[c['capabilityId'] for c in info['module']['capabilities']])


if __name__=='__main__':unittest.main()
