"""Stateless HTTP adapter. Deploy behind an authenticated private ingress only."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from worker import execute, pairs

RECEIVER = 'processor.scaleway'

class Handler(BaseHTTPRequestHandler):
    # Single worker bounds concurrency; Scaleway supplies TLS and authentication.
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *args):
        pass  # Never record headers, request bodies or source text.

    def reply(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.reply(200 if self.path == '/health' else 404,
                   {'status': 'ok'} if self.path == '/health' else {'error': 'not_found'})

    def do_POST(self):
        if self.path != '/process':
            return self.reply(404, {'error': 'not_found'})
        lengths = self.headers.get_all('Content-Length', [])
        if self.headers.get('Transfer-Encoding') or len(lengths) != 1:
            return self.reply(400, {'error': 'invalid_framing'})
        if self.headers.get_content_type() != 'application/json':
            return self.reply(415, {'error': 'json_required'})
        try:
            length = int(lengths[0])
            if not 0 < length <= 65536:
                return self.reply(413, {'error': 'request_too_large'})
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError()
            value = execute(json.loads(raw, object_pairs_hook=pairs), RECEIVER)
        except (ValueError, TypeError, KeyError, RecursionError, TimeoutError):
            return self.reply(400, {'error': 'invalid_request'})
        self.reply(200, value)

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
