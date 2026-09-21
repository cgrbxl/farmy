"""Loopback-only development transport. Not a production application server."""
import hashlib
import http.client
import json
import os
from pathlib import Path
import socket
import ssl
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[3]
FOUNDATION = json.loads((ROOT / 'contracts/v0.1-draft/foundation.schema.json').read_text())
OPERATIONS = json.loads((ROOT / 'contracts/uc001/operations.schema.json').read_text())
EXTRA_SCHEMA = json.loads((ROOT / 'contracts/uc002/operations.schema.json').read_text())
EXTRA_OPERATIONS = json.loads((ROOT / 'contracts/uc002/operations.json').read_text())
SENSOR_SCHEMA = json.loads((ROOT / 'contracts/uc003/operations.schema.json').read_text())
SENSOR_OPERATIONS = json.loads((ROOT / 'contracts/uc003/operations.json').read_text())
ANSWER_SCHEMA = json.loads((ROOT / 'contracts/uc004/operations.schema.json').read_text())
ANSWER_OPERATIONS = json.loads((ROOT / 'contracts/uc004/operations.json').read_text())
MONITOR_SCHEMA = json.loads((ROOT / 'contracts/uc005/monitoring.schema.json').read_text())
DISCLOSURE_SCHEMA = json.loads((ROOT / 'contracts/uc006/operations.schema.json').read_text())
DISCLOSURE_OPERATIONS = json.loads((ROOT / 'contracts/uc006/operations.json').read_text())
PROFILE = 'farmy.integration/0.1-draft'
MAX_BYTES = 1048576
MUTATIONS = {'resource.register', 'resource.move', 'resource.update', 'grant.issue', 'grant.revoke'}
CAPABILITY = {'snapshot.capture': 'farmy.storage', 'read.version': 'farmy.storage',
              'authorize.read': 'farmy.authorization'}
CODES = {'invalid_request': 400, 'unauthenticated': 401, 'denied': 403,
         'not_found': 404, 'conflict': 409, 'unsupported': 422, 'expired': 408,
         'unavailable': 503, 'internal': 500}


class Fault(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-finite number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def schema_check(schema, definition, data):
    Draft202012Validator(dict(schema, **{'$ref': '#/$defs/' + definition}),
                         format_checker=FormatChecker()).validate(data)


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def utc(seconds=0):
    return datetime.fromtimestamp(time.time() + seconds, timezone.utc).isoformat().replace('+00:00', 'Z')


def fingerprint(path):
    return hashlib.sha256(ssl.PEM_cert_to_DER_cert(Path(path).read_text())).hexdigest()


def request(config, target, operation, payload, *, refs=None, grant='grant.owner-bootstrap',
            subject=None, revision=None, key=None):
    actor = config['identity']
    _, namespace, version, capability, purpose, mutation = operation_spec(operation)
    result = {'profile': PROFILE, 'requestId': 'request.' + uuid4().hex,
              'correlationId': 'correlation.' + uuid4().hex, 'walletId': config['walletId'],
              'targetInstanceId': target, 'capabilityId': capability,
              'contractVersion': version, 'operation': operation,
              'purpose': purpose,
              'actorId': actor, 'subjectId': subject or actor, 'grantRef': grant,
              'deadline': utc(20), 'inputRefs': refs or [],
              'payloadSchema': 'urn:farmy:' + namespace + ':' + operation + '.input', 'payload': payload}
    if mutation:
        result['idempotencyKey'] = key or 'key.' + uuid4().hex
    if revision is not None:
        result['expectedRevision'] = revision
    return result


def operation_spec(operation):
    if operation in DISCLOSURE_OPERATIONS:
        data = DISCLOSURE_OPERATIONS[operation]
        return DISCLOSURE_SCHEMA, 'uc006', '0.6-draft', data['capabilityId'], data['purpose'], data['mutation']
    if operation == 'monitor.summary':
        return MONITOR_SCHEMA, 'uc005', '0.5-draft', 'farmy.monitoring', 'uc005.inspect', False
    if operation in ANSWER_OPERATIONS:
        data = ANSWER_OPERATIONS[operation]
        return ANSWER_SCHEMA, 'uc004', '0.4-draft', data['capabilityId'], data['purpose'], data['mutation']
    if operation in SENSOR_OPERATIONS:
        data = SENSOR_OPERATIONS[operation]
        return SENSOR_SCHEMA, 'uc003', '0.3-draft', data['capabilityId'], data['purpose'], data['mutation']
    if operation in EXTRA_OPERATIONS:
        data = EXTRA_OPERATIONS[operation]
        return EXTRA_SCHEMA, 'uc002', '0.2-draft', data['capabilityId'], data['purpose'], data['mutation']
    return (OPERATIONS, 'uc001', '0.1-draft', CAPABILITY.get(operation, 'farmy.wallet'),
            'uc001.read' if operation in {'read.version', 'authorize.read'} else 'uc001.manage',
            operation in MUTATIONS)


def client_context(config):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.load_verify_locations(config['ca'])
    context.load_cert_chain(config['cert'], config['key'])
    return context


def exchange(config, target, body=None, path=None):
    endpoint = config['endpoints'][target]
    parsed = urlsplit(endpoint['url'])
    if parsed.scheme != 'https' or parsed.hostname != '127.0.0.1' or parsed.path not in ('', '/'):
        raise Fault('unavailable')
    connection = http.client.HTTPSConnection(parsed.hostname, parsed.port,
                                              context=client_context(config), timeout=min(55, max(0.1, endpoint.get('timeoutSeconds', 3))))
    try:
        connection.connect()
        peer = hashlib.sha256(connection.sock.getpeercert(binary_form=True)).hexdigest()
        if peer != endpoint['fingerprint']:
            raise Fault('unauthenticated')
        headers = {'Content-Type': 'application/json'} if body is not None else {}
        connection.request('POST' if body is not None else 'GET',
                           path or '/farmy/v0/' + body['operation'],
                           json.dumps(body, allow_nan=False).encode() if body is not None else None,
                           headers)
        response = connection.getresponse()
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise Fault('unavailable')
        media = response.getheader('Content-Type', '')
        if media == 'application/octet-stream':
            if response.status != 200 or hashlib.sha256(raw).hexdigest() != response.getheader('X-Farmy-SHA256'):
                raise Fault('unavailable')
            if body is None or response.getheader('X-Farmy-Version') != body['inputRefs'][0]['versionId']:
                raise Fault('unavailable')
            return raw
        data = strict_json(raw)
        if response.status >= 400:
            raise Fault(data.get('error', {}).get('code', 'unavailable'))
        if body is None:
            return data
        schema_check(FOUNDATION, 'response', data)
        operation_schema, namespace, *_ = operation_spec(body['operation'])
        if (data['requestId'] != body['requestId'] or data['producerInstanceId'] != target
                or data['resultSchema'] != 'urn:farmy:' + namespace + ':' + body['operation'] + '.output'):
            raise Fault('unavailable')
        schema_check(operation_schema, body['operation'] + '.output', data['result'])
        return data['result']
    except (OSError, http.client.HTTPException, ValueError, ValidationError) as exc:
        raise Fault('unavailable') from exc
    finally:
        connection.close()


def check_request(config, peer, body, route):
    try:
        schema_check(FOUNDATION, 'request', body)
        operation = body['operation']
        operation_schema, namespace, version, capability, purpose, mutation = operation_spec(operation)
        if route != '/farmy/v0/' + operation or operation + '.input' not in operation_schema['$defs']:
            raise Fault('unsupported')
        schema_check(operation_schema, operation + '.input', body['payload'])
        if body['payloadSchema'] != 'urn:farmy:' + namespace + ':' + operation + '.input':
            raise Fault('invalid_request')
        if body['capabilityId'] != capability:
            raise Fault('unsupported')
        if body['contractVersion'] != version:
            raise Fault('unsupported')
        if body['actorId'] != peer or body['targetInstanceId'] != config['identity']:
            raise Fault('denied')
        if body['walletId'] != config['walletId'] or any(
                r['walletId'] != config['walletId'] for r in body['inputRefs']):
            raise Fault('denied')
        deadline = timestamp(body['deadline'])
        if deadline <= time.time() or deadline > time.time() + 60:
            raise Fault('expired')
        expected_purpose = purpose
        if body['purpose'] != expected_purpose:
            raise Fault('denied')
        if mutation and 'idempotencyKey' not in body:
            raise Fault('invalid_request')
        if operation in {'resource.move', 'resource.update', 'grant.revoke', 'access.revoke', 'source.revoke'} and 'expectedRevision' not in body:
            raise Fault('invalid_request')
    except (ValidationError, ValueError, KeyError):
        raise Fault('invalid_request') from None


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def get_request(self):
        sock, address = self.socket.accept()
        sock.settimeout(3)
        try:
            return self.context.wrap_socket(sock, server_side=True), address
        except Exception:
            sock.close()
            raise

    def handle_error(self, request, client_address):
        # No request bodies, paths or credentials in generic server logs.
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = 'Farmy-UC001'

    def log_message(self, *args):
        pass

    def send(self, status, data, extra=None):
        raw = data if isinstance(data, bytes) else json.dumps(data, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/octet-stream' if isinstance(data, bytes) else 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close')
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(raw)

    def run_request(self):
        body = None
        self.validated_body = None
        config = self.server.app.config
        peer = None
        try:
            digest = hashlib.sha256(self.connection.getpeercert(binary_form=True)).hexdigest()
            peer = config['peers'].get(digest)
            if peer is None:
                raise Fault('unauthenticated')
            if self.command == 'GET':
                if self.path == '/farmy/v0/monitor/summary':
                    if peer not in config.get('monitorSubjects', []):
                        raise Fault('denied')
                    result = self.server.app.monitoring_summary()
                    schema_check(MONITOR_SCHEMA, 'summary', result)
                    self.send(200, result)
                    return
                if self.path in ('/farmy/v0/health/live', '/farmy/v0/health/ready') and peer in config['operators']:
                    ready = self.path.endswith('/live') or self.server.app.ready()
                    self.send(200 if ready else 503, {'status': 'ready' if ready else 'degraded'})
                    return
                if self.path == '/farmy/v0/descriptor' and peer in config['operators']:
                    self.send(200, self.server.app.descriptor())
                    return
                raise Fault('denied')
            if self.headers.get_all('Transfer-Encoding') or len(self.headers.get_all('Content-Length', [])) != 1:
                raise Fault('invalid_request')
            if self.headers.get('Content-Type') != 'application/json':
                raise Fault('invalid_request')
            length = int(self.headers['Content-Length'])
            if length < 1 or length > 65536:
                raise Fault('invalid_request')
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise Fault('invalid_request')
            body = strict_json(raw)
            schema_check(FOUNDATION, 'request', body)
            self.validated_body = body
            check_request(config, peer, body, self.path)
            result = self.server.app.handle(peer, body)
            if isinstance(result, bytes):
                self.send(200, result, {'X-Farmy-SHA256': hashlib.sha256(result).hexdigest(),
                                       'X-Farmy-Version': body['inputRefs'][0]['versionId']})
            else:
                operation_schema, namespace, *_ = operation_spec(body['operation'])
                schema_check(operation_schema, body['operation'] + '.output', result)
                response = {'profile': PROFILE, 'requestId': body['requestId'],
                            'producerInstanceId': config['identity'], 'implementationVersion': config.get('implementationVersion', '0.1.0'),
                            'status': 'succeeded', 'inputRefs': body['inputRefs'], 'outputRefs': [],
                            'resultSchema': 'urn:farmy:' + namespace + ':' + body['operation'] + '.output', 'result': result}
                schema_check(FOUNDATION, 'response', response)
                self.send(200, response)
        except Fault as exc:
            self.server.app.failure(peer, exc.code)
            self.send_fault(exc.code)
        except (ValueError, TypeError, KeyError, ValidationError):
            self.server.app.failure(peer, 'invalid_request')
            self.send_fault('invalid_request')
        except Exception:
            self.server.app.failure(peer, 'internal')
            self.send_fault('internal')

    def send_fault(self, code):
        error = {'code': code, 'message': code.replace('_', ' '), 'retryable': code == 'unavailable'}
        body = self.validated_body
        response = {'error': error}
        if body is not None:
            response.update(profile=PROFILE, requestId=body['requestId'],
                            producerInstanceId=self.server.app.config['identity'],
                            implementationVersion=self.server.app.config.get('implementationVersion', '0.1.0'), status='failed',
                            inputRefs=body['inputRefs'], outputRefs=[])
            schema_check(FOUNDATION, 'response', response)
        self.send(CODES.get(code, 500), response)

    def do_GET(self):
        self.run_request()

    def do_POST(self):
        self.run_request()


def serve(app):
    os.umask(0o077)
    config = app.config
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(config['cert'], config['key'])
    context.load_verify_locations(config['ca'])
    server = Server(('127.0.0.1', config['port']), Handler)
    server.context = context
    server.app = app
    print(json.dumps({'instance': config['identity'], 'port': config['port'], 'status': 'listening'}), flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def descriptor(config, family, capabilities, dependencies):
    """Foundation records; target status is deliberately experimental."""
    implementation = config.get('implementationId', 'farmy.reference.' + ('local-folder' if family == 'connectors' else family))
    def capability(name, operations):
        return {'capabilityId': name, 'contractVersion': '0.1-draft', 'operations': operations,
                'features': ['exact-version'] if name == 'farmy.storage' else []}
    def declarations(items):
        result = []
        for name, operations in items.items():
            for version in sorted({operation_spec(op)[2] for op in operations}):
                item = capability(name, [op for op in operations if operation_spec(op)[2] == version])
                item['contractVersion'] = version
                result.append(item)
        return result
    if config.get('monitorSubjects'):
        capabilities = dict(capabilities, **{'farmy.monitoring': ['monitor.summary']})
    module = {'profile': PROFILE, 'implementationId': implementation, 'implementationVersion': config.get('implementationVersion', '0.1.0'),
              'family': family, 'capabilities': declarations(capabilities),
              'dependencies': [dict(item, required=True) for item in declarations(dependencies)],
              'securityProfiles': ['farmy.mtls-online/0.1-draft'], 'connectivityModes': ['direct-https'],
              'targets': [{'target': name, 'status': 'experimental' if name == 'macos' else 'unsupported'}
                          for name in ('macos', 'windows', 'linux', 'kubernetes')],
              'permissionsRequired': [config.get('bootstrapProfile', 'uc001.bootstrap')],
              'state': {'ownership': 'implementation-private', 'migration': 'none'}}
    instance = {'profile': PROFILE, 'instanceId': config['identity'], 'implementationId': implementation,
                'implementationVersion': config.get('implementationVersion', '0.1.0'), 'endpoint': config['endpoints'][config['identity']]['url'],
                'securityProfile': 'farmy.mtls-online/0.1-draft', 'connectivityMode': 'direct-https',
                'peerIdentity': 'urn:farmy:identity:' + config['identity'],
                'environmentId': config.get('environmentId', 'environment.uc001-local'), 'status': 'registered'}
    schema_check(FOUNDATION, 'module', module)
    schema_check(FOUNDATION, 'instance', instance)
    return {'module': module, 'instance': instance}
