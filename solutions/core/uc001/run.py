"""Bootstrap, independently serve, or demonstrate the synthetic UC-001 slice."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'sdk/python'), str(ROOT / 'modules/registry/reference')]
from farmy_transport.http import Fault, PROFILE, exchange, fingerprint, request, utc

V1 = b'Farmy synthetic record v1\n'
V2 = b'Farmy synthetic record v2\n'
SERVICES = {'wallet.local': 'modules/wallet/reference/service.py',
            'connector.local': 'modules/connectors/local_folder/service.py'}


def bootstrap(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if any(directory.iterdir()):
        raise ValueError('Bootstrap needs an empty directory; existing state is never overwritten.')
    os.umask(0o077)
    directory.chmod(0o700)
    certs = directory / 'certs'
    certs.mkdir(mode=0o700)
    def openssl(*args):
        subprocess.run(['openssl', *map(str, args)], check=True, capture_output=True)
    ca, cakey = certs / 'ca.pem', certs / 'ca.key'
    openssl('req', '-x509', '-newkey', 'ec', '-pkeyopt', 'ec_paramgen_curve:P-256',
            '-nodes', '-days', '2', '-subj', '/CN=Farmy UC001 development CA',
            '-addext', 'basicConstraints=critical,CA:TRUE',
            '-addext', 'keyUsage=critical,keyCertSign,cRLSign', '-keyout', cakey, '-out', ca)
    identities = ['wallet.local', 'connector.local', 'owner', 'reader', 'denied', 'unknown']
    for serial, identity in enumerate(identities, 1):
        key, csr, cert = [certs / (identity + suffix) for suffix in ('.key', '.csr', '.pem')]
        openssl('req', '-new', '-newkey', 'ec', '-pkeyopt', 'ec_paramgen_curve:P-256',
                '-nodes', '-subj', '/CN=' + identity, '-keyout', key, '-out', csr)
        ext = certs / (identity + '.ext')
        ext.write_text('basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\n'
                       'extendedKeyUsage=serverAuth,clientAuth\n'
                       'subjectAltName=IP:127.0.0.1,URI:urn:farmy:identity:' + identity + '\n')
        openssl('x509', '-req', '-in', csr, '-CA', ca, '-CAkey', cakey,
                '-set_serial', str(serial), '-days', '2', '-extfile', ext, '-out', cert)
    # The bootstrap CA cannot mint more identities after setup.
    cakey.unlink()
    held = []
    try:
        for _ in SERVICES:
            sock = socket.socket()
            sock.bind(('127.0.0.1', 0))
            held.append(sock)
        ports = dict(zip(SERVICES, [s.getsockname()[1] for s in held]))
    finally:
        for sock in held:
            sock.close()
    endpoints = {name: {'url': f'https://127.0.0.1:{port}',
                       'fingerprint': fingerprint(certs / (name + '.pem'))} for name, port in ports.items()}
    peers = {fingerprint(certs / (name + '.pem')): name for name in identities if name != 'unknown'}
    source = directory / 'source'
    source.mkdir(mode=0o700)
    (source / 'record.txt').write_bytes(V1)
    binding = {'profile': PROFILE, 'bindingId': 'binding.local', 'revision': 1,
               'walletId': 'wallet.demo', 'instanceId': 'connector.local',
               'capabilityId': 'farmy.storage', 'contractVersion': '0.1-draft',
               'operations': ['snapshot.capture', 'read.version'],
               'requiredFeatures': ['exact-version'], 'scopeId': 'collection.local'}
    (directory / 'binding.json').write_text(json.dumps(binding, indent=2))
    for identity in identities:
        config = {'identity': identity, 'walletId': 'wallet.demo', 'ca': str(ca),
                  'cert': str(certs / (identity + '.pem')), 'key': str(certs / (identity + '.key')),
                  'endpoints': endpoints, 'peers': peers,
                  'operators': ['owner', 'wallet.local', 'connector.local'],
                  'state': str(directory / ('state-' + identity)), 'sourceRoot': str(source),
                  'binding': str(directory / 'binding.json')}
        if identity in ports:
            config['port'] = ports[identity]
        (directory / (identity + '.json')).write_text(json.dumps(config, indent=2))
    return directory


def config(directory, identity='owner'):
    return json.loads((Path(directory) / (identity + '.json')).read_text())


def command(directory, identity):
    return [sys.executable, str(ROOT / SERVICES[identity]), '--config',
            str(Path(directory).resolve() / (identity + '.json'))]


def environment():
    return dict(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT / 'sdk/python'),
                                                      str(ROOT / 'modules/registry/reference')]))


class Processes:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.children = {}

    def start(self, identity):
        if identity in self.children:
            raise ValueError('Process already owned by this runner')
        with (self.directory / (identity + '.log')).open('ab') as log:
            child = subprocess.Popen(command(self.directory, identity), env=environment(), stdout=log, stderr=log)
        self.children[identity] = child
        until = time.monotonic() + 10
        while time.monotonic() < until:
            if child.poll() is not None:
                raise RuntimeError(f'{identity} exited; see its log in {self.directory}')
            try:
                exchange(config(self.directory), identity, path='/farmy/v0/health/live')
                return
            except Fault:
                time.sleep(.05)
        raise RuntimeError(f'{identity} did not become live')

    def stop(self, identity):
        child = self.children.pop(identity, None)
        if child is not None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()

    def __enter__(self):
        try:
            for identity in SERVICES:
                self.start(identity)
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *args):
        for identity in list(self.children):
            self.stop(identity)


def call(directory, operation, payload=None, identity='owner', **kwargs):
    target = 'connector.local' if operation in ('read.version', 'snapshot.capture') else 'wallet.local'
    client = config(directory, identity)
    return exchange(client, target, request(client, target, operation, payload or {}, **kwargs))


def refs(resource):
    return [{'walletId': 'wallet.demo', 'resourceId': resource['resourceId'], 'versionId': resource['versionId']}]


def grant(directory, resource, subject='reader'):
    return call(directory, 'grant.issue', {'resourceId': resource['resourceId'],
                'versionId': resource['versionId'], 'subjectId': subject,
                'expiresAt': utc(600), 'purpose': 'uc001.read'}, refs=refs(resource))


def read(directory, resource, permission, identity='reader'):
    return call(directory, 'read.version', identity=identity, refs=refs(resource), grant=permission['grantId'])


def expect_fault(code, action):
    try:
        action()
    except Fault as exc:
        if exc.code != code:
            raise AssertionError(f'Expected {code}, got {exc.code}') from exc
    else:
        raise AssertionError(f'Expected {code}, request succeeded')


def demo(directory):
    with Processes(directory) as processes:
        original = call(directory, 'resource.register', {'path': 'record.txt'})
        permission = grant(directory, original)
        assert read(directory, original, permission) == V1
        print('PASS registered and read exact version under a scoped grant')
        expect_fault('denied', lambda: read(directory, original, permission, 'denied'))
        expect_fault('unauthenticated', lambda: read(directory, original, permission, 'unknown'))
        print('PASS denied and unenrolled callers rejected')
        source = Path(directory) / 'source'
        (source / 'record.txt').rename(source / 'moved.txt')
        moved = call(directory, 'resource.move', {'resourceId': original['resourceId'], 'path': 'moved.txt'},
                     refs=refs(original), revision=original['revision'])
        assert moved['versionId'] == original['versionId']
        (source / 'moved.txt').write_bytes(V2)
        updated = call(directory, 'resource.update', {'resourceId': moved['resourceId']},
                       refs=refs(moved), revision=moved['revision'])
        assert updated['resourceId'] == original['resourceId'] and updated['versionId'] != original['versionId']
        new_permission = grant(directory, updated)
        assert read(directory, updated, new_permission) == V2
        assert read(directory, original, permission) == V1
        print('PASS move preserves identity; update preserves both immutable versions')
        for identity in SERVICES:
            processes.stop(identity)
        for identity in SERVICES:
            processes.start(identity)
        assert read(directory, original, permission) == V1
        call(directory, 'grant.revoke', {'grantId': permission['grantId']}, revision=1)
        expect_fault('denied', lambda: read(directory, original, permission))
        print('PASS restart preserves state; revoked grant denied on next read')
        processes.stop('wallet.local')
        expect_fault('unavailable', lambda: read(directory, updated, new_permission))
        print('PASS unavailable authority fails closed')
    print('Demo complete. Both processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['bootstrap', 'serve', 'demo', 'request'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--service', choices=['wallet', 'connector'])
    parser.add_argument('--identity', choices=['owner', 'reader', 'denied', 'unknown'], default='owner')
    parser.add_argument('--operation')
    parser.add_argument('--payload', default='{}', help='JSON operation payload')
    parser.add_argument('--refs', default='[]', help='JSON exact resource references')
    parser.add_argument('--grant', default='grant.owner-bootstrap')
    parser.add_argument('--revision', type=int)
    parser.add_argument('--key', help='Idempotency key; generated if omitted')
    args = parser.parse_args()
    if args.action == 'demo':
        if args.directory is not None:
            parser.error('demo creates and cleans its own temporary synthetic state')
        with tempfile.TemporaryDirectory(prefix='farmy-uc001-') as directory:
            demo(bootstrap(directory))
    elif args.directory is None:
        parser.error('--directory is required for bootstrap/serve')
    elif args.action == 'bootstrap':
        print(bootstrap(args.directory))
    elif args.action == 'request':
        if args.operation is None:
            parser.error('--operation is required for request')
        result = call(args.directory, args.operation, json.loads(args.payload), identity=args.identity,
                      refs=json.loads(args.refs), grant=args.grant, revision=args.revision, key=args.key)
        if isinstance(result, bytes):
            sys.stdout.buffer.write(result)
        else:
            print(json.dumps(result, indent=2))
    elif args.service is None:
        parser.error('--service is required for serve')
    else:
        os.execve(sys.executable, command(args.directory, args.service + '.local'), environment())


if __name__ == '__main__':
    main()
