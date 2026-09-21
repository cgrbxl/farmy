"""Read-only, loopback browser bridge. Uses only public mTLS service APIs."""
import argparse
import errno
from concurrent.futures import ThreadPoolExecutor
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'sdk/python'))
from farmy_transport.http import Fault, MONITOR_SCHEMA, exchange, schema_check, utc

ASSETS = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
          '/style.css': ('style.css', 'text/css')}


DEFAULT_PORT = 8766


def bind_server(config, port=None):
    """Bind atomically; only the implicit default may fall back to a free port."""
    try:
        return Server(config, DEFAULT_PORT if port is None else port)
    except OSError as error:
        if error.errno != errno.EADDRINUSE:
            raise
        if port is not None:
            raise SystemExit(f'Port {port} is already in use. Omit --port or use --port 0 to choose a free port.') from None
        return Server(config, 0)


def inspect(config, identity, declared):
    node = dict(declared, instanceId=identity, endpoint=config['endpoints'][identity]['url'],
                status='unavailable', summaryStatus='unavailable', counts=[], activity=[],
                dependencies=[], observedAt=utc())
    try:
        info = exchange(config, identity, path='/farmy/v0/descriptor')
        if info['instance']['instanceId'] != identity or info['module']['family'] != declared['family']:
            raise Fault('conflict')
        node.update(version=info['module']['implementationVersion'], status='available')
        try:
            exchange(config, identity, path='/farmy/v0/health/ready')
            node['readiness'] = 'passed'
        except Fault:
            node.update(status='degraded', readiness='failed or unavailable')
        try:
            summary = exchange(config, identity, path='/farmy/v0/monitor/summary')
            schema_check(MONITOR_SCHEMA, 'summary', summary)
            if summary['instanceId'] != identity:
                raise Fault('conflict')
            node.update(counts=summary['counts'], activity=summary['activity'],
                        dependencies=summary['dependencies'], summaryStatus='available',
                        observedAt=summary['observedAt'])
        except Fault as exc:
            node['summaryStatus'] = exc.code
    except Fault as exc:
        node['error'] = exc.code
    return node


def snapshot(config):
    with ThreadPoolExecutor(max_workers=8) as pool:
        nodes = list(pool.map(lambda item: inspect(config, *item), config['inventory'].items()))
    return {'observedAt': utc(), 'environment': 'Synthetic local development', 'nodes': nodes,
            'adapters': [{'family': 'registry', 'name': 'Registry binding-file adapter', 'status': 'configuration only'}],
            'planned': [{'family': 'exchange', 'name': 'Exchange', 'status': 'not deployed'}]}


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    def __init__(self, config, port):
        super().__init__(('127.0.0.1', port), Handler)
        self.config = config
        self.snapshot_lock = threading.Lock()
    def handle_error(self, *args):
        pass


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)
    def log_message(self, *args):
        pass
    def send(self, code, data, media='application/json'):
        raw = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', media + '; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        host = '127.0.0.1:' + str(self.server.server_port)
        if self.headers.get('Host') != host or self.headers.get('Origin', 'http://' + host) != 'http://' + host:
            self.send(403, {'error': 'origin_denied'})
            return
        if self.path in ASSETS:
            file, media = ASSETS[self.path]
            self.send(200, (ROOT / 'dashboard/live' / file).read_bytes(), media)
            return
        if self.path != '/api/snapshot':
            self.send(404, {'error': 'not_found'})
            return
        expected = 'Bearer ' + self.server.config['browserToken']
        supplied = self.headers.get('Authorization', '')
        if not hmac.compare_digest(supplied.encode(), expected.encode()):
            self.send(401, {'error': 'unauthorised'})
            return
        if not self.server.snapshot_lock.acquire(blocking=False):
            self.send(503, {'error': 'snapshot_busy'})
            return
        try:
            self.send(200, snapshot(self.server.config))
        except Exception:
            self.send(503, {'error': 'snapshot_unavailable'})
        finally:
            self.server.snapshot_lock.release()
    def do_POST(self):
        self.send(405, {'error': 'read_only'})
    do_PUT = do_DELETE = do_PATCH = do_POST


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--port', type=int, help='Fixed port; 0 chooses a free port. Default: 8766 with automatic fallback.')
    args = parser.parse_args()
    server = bind_server(json.loads(args.config.read_text()), args.port)
    print(f'Operational dashboard: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
