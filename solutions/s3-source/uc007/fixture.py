"""Small local S3 HTTP double. Never evidence of Scaleway compatibility."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from urllib.parse import parse_qs, unquote, urlsplit


class Fixture(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self):
        super().__init__(('127.0.0.1', 0), Handler)
        self.lock = threading.Lock()
        self.objects = {}
        self.versions = {}
        self.calls = []
        self.versioned = True
        self.denied = False
        self.available = True
        self.after_head = None
        self.bad_length = False
        self.put('report.txt', b'Farmy synthetic report\ncrop: wheat\n')

    def put(self, name, raw):
        key = 'farmy-tests/' + name
        with self.lock:
            version = str(len(self.versions) + 1)
            record = {'version': version, 'etag': '"opaque-' + version + '"', 'raw': raw}
            self.objects[key] = record
            self.versions[(key, version)] = record

    def settings(self):
        return {'region': 'fr-par', 'endpoint': f'http://127.0.0.1:{self.server_port}',
                'bucket': 'farmy-fixture', 'prefix': 'farmy-tests/', 'fixture': True}

    @contextmanager
    def running(self):
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        try:
            yield self
        finally:
            self.shutdown()
            self.server_close()
            thread.join()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def serve_object(self, head=False):
        server = self.server
        parsed = urlsplit(self.path)
        path = unquote(parsed.path)
        if not path.startswith('/farmy-fixture/'):
            self.send_error(404)
            return
        key = path[len('/farmy-fixture/'):]
        with server.lock:
            server.calls.append((self.command, key, self.headers.get('Authorization', '').startswith('AWS4-HMAC-SHA256 ')))
            version = parse_qs(parsed.query).get('versionId', [None])[0]
            record = server.versions.get((key, version)) if version else server.objects.get(key)
            status = 503 if not server.available else 403 if server.denied else 404 if record is None else 200
            if status == 200 and self.headers.get('If-Match', record['etag']) != record['etag']:
                status = 412
            if status != 200:
                self.send_response(status)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            callback = server.after_head if head else None
            if callback:
                server.after_head = None
        if callback:
            callback()
        self.send_response(200)
        self.send_header('ETag', record['etag'])
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(len(record['raw']) + (1 if server.bad_length and not head else 0)))
        self.send_header('Connection', 'close')
        if server.versioned:
            self.send_header('x-amz-version-id', record['version'])
        self.end_headers()
        if not head:
            self.wfile.write(record['raw'])
    def do_HEAD(self): self.serve_object(True)
    def do_GET(self): self.serve_object()
