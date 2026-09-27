"""Persistent local composition. No required Farmy cloud service."""
import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
import plistlib
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
VERSION = '0.3.0'
SCHEMA = 1
spec = importlib.util.spec_from_file_location('directory_solution', ROOT / 'solutions/directory/uc012/run.py')
solution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solution)
core = solution.server.managed.core
Fault = solution.server.Fault
messaging_spec=importlib.util.spec_from_file_location('farmy_messaging',ROOT/'modules/workflow/messaging/planner.py')
messaging=importlib.util.module_from_spec(messaging_spec);messaging_spec.loader.exec_module(messaging)


def default_home():
    return Path(os.environ.get('FARMY_HOME', str(Path.home() / 'Library/Application Support/Farmy'))).absolute()


def save(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.' + uuid4().hex + '.tmp')
    try:
        with temporary.open('x') as output:
            os.chmod(temporary, 0o600)
            json.dump(value, output, indent=2)
            output.flush(); os.fsync(output.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)


def settings(home):
    value = json.loads((home / 'installation.json').read_text())
    if value.get('schema') != SCHEMA:
        raise ValueError('Unsupported workspace schema; use its compatible release or restore a backup.')
    return value


def initialise(home, source, port):
    source = Path(source).absolute()
    home = home.absolute()
    if source.is_symlink() or not source.is_dir():
        raise ValueError('Source must be an existing directory, not a symlink.')
    if home.resolve() == source.resolve() or home.resolve().is_relative_to(source.resolve()) or source.resolve().is_relative_to(home.resolve()):
        raise ValueError('Source and runtime data must be separate directory trees.')
    if home.exists() and (home.is_symlink() or any(home.iterdir())):
        raise ValueError('Initialisation requires a new or empty data directory; existing state is never overwritten.')
    if not 1024 <= port <= 65535:
        raise ValueError('Choose an unprivileged port between 1024 and 65535.')
    home.mkdir(parents=True, mode=0o700, exist_ok=True);home.chmod(0o700)
    save(home / 'installation.json', dict(schema=SCHEMA, version=VERSION, source=str(source), port=port, installationId=uuid4().hex))


@contextmanager
def exclusive(home):
    if home.is_symlink() or home.stat().st_mode & 0o077:
        raise ValueError('Runtime directory must be private (mode 0700) and not a symlink.')
    with (home / 'runtime.lock').open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise ValueError('This workspace is already running or undergoing maintenance.') from exc
        try: yield
        finally: fcntl.flock(lock, fcntl.LOCK_UN)


def identities(home):
    """Persistent P-256 keys. Local pairing pins SHA-256 public-key fingerprints."""
    result = {}
    for name in ('owner','reader'):
        folder = home / 'identities' / name
        folder.mkdir(mode=0o700,parents=True,exist_ok=True)
        key = folder / 'private.pem'
        if not key.exists():
            temporary=folder / ('key.'+uuid4().hex)
            subprocess.run(['openssl','genpkey','-algorithm','EC','-pkeyopt','ec_paramgen_curve:P-256','-out',str(temporary)],check=True,capture_output=True)
            temporary.chmod(0o600);os.replace(temporary,key)
        public=subprocess.run(['openssl','pkey','-in',str(key),'-pubout','-outform','DER'],check=True,capture_output=True).stdout
        result[name]=dict(id=name,name='Local owner' if name=='owner' else 'Paired demo consumer',fingerprint=hashlib.sha256(public).hexdigest())
    pairing=home/'identities'/'pairing.json'
    if pairing.exists():
        if json.loads(pairing.read_text()) != result:
            raise ValueError('A paired identity key changed. Restore its key or explicitly re-pair; automatic replacement is refused.')
    else: save(pairing,result)
    return result


def transport(home, consumer_token=None):
    """Fresh local certificates/configuration, with stable private service state."""
    config = settings(home)
    parent = home / 'transport';parent.mkdir(mode=0o700, exist_ok=True)
    generation = parent / uuid4().hex
    if not 1024 <= config['port'] <= 65534: raise ValueError('Owner port must leave the following port available for the consumer.')
    public=identities(home)
    # Exclude both fixed browser ports while assigning ephemeral service ports.
    with socket.socket() as owner_port, socket.socket() as consumer_port:
        for sock,port in ((owner_port,config['port']),(consumer_port,config['port']+1)):
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.bind(('127.0.0.1',port));sock.listen()
        solution.bootstrap(generation, config['source'], identity_keys={name:home/'identities'/name/'private.pem' for name in public}, extra_services={'reader':'modules/consumer/local/service.py'})
    for path in generation.glob('*.json'):
        if path.name == 'binding.json': continue
        value = json.loads(path.read_text())
        if 'state' in value:
            value['state'] = str(home / ('state-' + value['identity']))
        if value.get('identity')=='reader':
            value.update(browserToken=consumer_token or secrets.token_urlsafe(32), browserPort=config['port']+1,publicIdentity=public['reader'],runtimeVersion=VERSION)
        save(path, value)
    return generation


class Workbench(solution.Workbench):
    max_request_bytes=16384
    def __init__(self, generation, home, stop_event, tokens):
        self.stop_event = stop_event
        self.home = home
        self.messaging=messaging.Planner(home/'state-messaging')
        super().__init__(generation, state_directory=home)
        self.session.update(owner=tokens[0], consumer=tokens[1])
        self.source_expires = 0
        self.renew_source()
        self.public_identities=identities(home)
        self.consumer_origin='http://127.0.0.1:'+str(settings(home)['port']+1)
        self.sync_consumer()

    def role(self, authorization):
        role=super().role(authorization)
        if role != 'owner': raise Fault('unauthenticated')
        return role

    def offer(self, item, permission):
        client=core.config(self.directory,'owner')
        query=core.request(client,'reader','consumer.offer',dict(resource=item['resource'],grantId=permission['grantId']),refs=core.refs(item['resource']),key='key.offer-'+permission['grantId'])
        return core.exchange(client,'reader',query)

    def sync_consumer(self):
        with self.db() as db:
            rows=db.execute('SELECT i.metadata,p.permission FROM items i JOIN permissions p ON i.id=p.resource WHERE p.revoked=0').fetchall()
        for metadata,permission in rows: self.offer(json.loads(metadata),permission={"grantId":permission})

    def persist_session(self):
        with self.db() as db:
            db.execute("UPDATE settings SET value=? WHERE name='session'", (json.dumps(self.session),))

    def renew_source(self):
        if time.time() < self.source_expires - 60:
            return
        expiry = int(time.time()) + 1800
        permission = self.call('source.grant', dict(solution.server.managed.scope(self.session['source']), consumerId='owner',
            expiresAt=datetime.fromtimestamp(expiry, timezone.utc).isoformat().replace('+00:00','Z')))
        self.session['sourceGrant'] = permission['grantId']
        self.source_expires = expiry
        self.persist_session()

    def state(self, role):
        if role != 'owner':raise Fault('denied')
        self.renew_source()
        result = super().state(role)
        try:
            self.sync_consumer();delivery_pending=False
        except Fault:
            delivery_pending=True
        result.update(messaging=self.messaging.snapshot(),persistent=True, runtimeVersion=VERSION, identities=self.public_identities, consumerOrigin=self.consumer_origin, independentConsumer=True, consumerDeliveryPending=delivery_pending)
        return result

    def preview(self, entry):
        self.renew_source()
        return super().preview(entry)

    def action(self, role, action, payload):
        if not isinstance(action,str):raise Fault('invalid_request')
        if action.startswith('messaging.'):
            if role != 'owner': raise Fault('denied')
            try:
                operation=action.removeprefix('messaging.')
                if operation=='sender.check':return self.messaging.check_sender(payload)
                return self.messaging.change(operation,payload)
            except messaging.Conflict as exc:raise Fault('conflict') from exc
            except messaging.Invalid as exc:raise Fault('invalid_request') from exc
        if action in ('runtime.status', 'runtime.stop'):
            if role != 'owner': raise Fault('denied')
            if payload != {}: raise Fault('invalid_request')
            if action == 'runtime.stop': self.stop_event.set()
            return dict(running=True, version=VERSION)
        if role == 'owner' and action == 'admit': self.renew_source()
        if role != 'owner': raise Fault('denied')
        result=super().action(role, action, payload)
        if action == 'grant':
            try:self.sync_consumer()
            except Fault:result=dict(result,deliveryPending=True)
        return result

    def read(self, role, resource):
        if role != 'owner': return super().read(role, resource)
        item = self.item(resource)
        permission = self.call('grant.issue', dict(resourceId=item['resource']['resourceId'], versionId=item['resource']['versionId'],
            subjectId='owner', expiresAt=core.utc(300), purpose='uc001.read'), refs=core.refs(item['resource']))
        data = core.read(self.directory, item['resource'], permission, 'owner')
        return dict(text=data.decode('utf-8', errors='replace'), decision='Access allowed by Wallet')


class Server(solution.server.Server):
    # Drain in-flight client mutations before releasing the workspace for backup.
    daemon_threads = False


class Processes(core.Processes):
    def __init__(self, generation, home):
        super().__init__(generation, dict(solution.SERVICES,reader='modules/consumer/local/service.py'))
        self.home = home

    def spawn(self, identity, log):
        return subprocess.Popen([sys.executable, str(ROOT / 'runtime/local/guard.py'),
            str(self.home / (identity + '.lock')), *core.command(self.directory, identity, self.services)],
            env=core.environment(), stdin=subprocess.PIPE, stdout=log, stderr=log)

    def stop(self, identity):
        child = self.children.get(identity)
        super().stop(identity)
        if child is not None and child.stdin is not None: child.stdin.close()


def serve(home, run_id):
    os.umask(0o077)
    config = settings(home)
    stopping = threading.Event()
    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, lambda *_: stopping.set())
    tokens = (secrets.token_urlsafe(32), secrets.token_urlsafe(32))
    with exclusive(home):
        # Only generated transports are disposable; service/client state is outside this directory.
        shutil.rmtree(home / 'transport', ignore_errors=True)
        try:
            while not stopping.is_set():
                generation = transport(home, tokens[1])
                try:
                    with Processes(generation, home) as processes:
                        workbench = Workbench(generation, home, stopping, tokens)
                        with Server(workbench, config['port']) as http:
                            threading.Thread(target=http.serve_forever, daemon=True).start()
                            try:
                                save(home / 'running.json', dict(pid=os.getpid(), runId=run_id, port=http.server_port, token=tokens[0], version=VERSION))
                                rotate_at = time.time() + 12 * 3600
                                next_messaging_tick=0
                                while not stopping.wait(.2):
                                    if any(child.poll() is not None for child in processes.children.values()):
                                        raise RuntimeError('A module exited unexpectedly; the composition stopped. Check runtime.log.')
                                    if time.time()>=next_messaging_tick:
                                        workbench.messaging.tick();next_messaging_tick=time.time()+1
                                    if time.time() >= rotate_at: break
                            finally:
                                http.shutdown()
                finally:
                    # Retain module logs outside short-lived certificate generations.
                    for log in generation.glob('*.log'):
                        with (home / 'modules.log').open('ab') as output: output.write(log.read_bytes())
                    shutil.rmtree(generation, ignore_errors=True)
        finally:
            (home / 'running.json').unlink(missing_ok=True)


def control(home, operation='runtime.status'):
    running = json.loads((home / 'running.json').read_text())
    origin = f'http://127.0.0.1:{running["port"]}'
    request = urllib.request.Request(origin + '/api/action', data=json.dumps(dict(action=operation, payload={})).encode(),
        headers={'Authorization':'Bearer ' + running['token'], 'Origin':origin, 'Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=5) as response:
        return running, json.load(response)


def start(home):
    settings(home)
    with exclusive(home):
        (home / 'running.json').unlink(missing_ok=True)
    run_id = uuid4().hex
    with (home / 'runtime.log').open('ab') as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--home', str(home), 'serve', '--run-id', run_id],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True, close_fds=True)
    for _ in range(200):
        if child.poll() is not None:
            raise RuntimeError('Runtime failed to start; inspect ' + str(home / 'runtime.log'))
        try:
            running, _ = control(home)
            if running['runId'] == run_id:
                threading.Thread(target=child.wait, daemon=True).start()
                return
        except (OSError, ValueError): pass
        time.sleep(.1)
    child.terminate()
    try: child.wait(timeout=10)
    except subprocess.TimeoutExpired: child.kill();child.wait()
    raise RuntimeError('Runtime startup timed out; inspect runtime.log.')


def stop(home):
    control(home, 'runtime.stop')
    for _ in range(150):
        try:
            with exclusive(home): return
        except ValueError: time.sleep(.1)
    raise RuntimeError('Shutdown has not completed; inspect runtime.log before retrying.')


def backup(home, destination):
    destination = destination.absolute()
    if destination.exists(): raise ValueError('Backup destination must not exist.')
    if destination.is_relative_to(home.resolve()): raise ValueError('Backup must be outside the runtime directory.')
    with exclusive(home):
        settings(home)
        destination.mkdir(parents=True, mode=0o700)
        try:
            for name in ['installation.json', 'workbench.sqlite', 'state-wallet.local', 'state-connector.local', 'state-reader', 'identities', 'state-messaging']:
                source = home / name
                if source.is_dir(): shutil.copytree(source, destination / name, symlinks=False)
                elif source.is_file(): shutil.copy2(source, destination / name)
            files = {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.rglob('*') if p.is_file()}
            save(destination / 'backup.json', dict(schema=SCHEMA, version=VERSION, createdAt=core.utc(), files=files))
        except BaseException:
            shutil.rmtree(destination)
            raise


def restore(home, source):
    source = source.absolute()
    marker = json.loads((source / 'backup.json').read_text())
    if marker.get('schema') != SCHEMA: raise ValueError('Unsupported backup schema.')
    settings(source)
    if home.exists(): raise ValueError('Restore needs a new data directory; nothing is overwritten.')
    if home.is_relative_to(source): raise ValueError('Restore target must be outside the backup.')
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')): raise ValueError('Symlinks are not permitted in backups.')
    actual = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file() and p.name != 'backup.json'}
    if actual != marker.get('files'): raise ValueError('Backup content does not match its checksums.')
    home.mkdir(parents=True, mode=0o700)
    try:
        for name in ['installation.json', 'workbench.sqlite', 'state-wallet.local', 'state-connector.local', 'state-reader', 'identities', 'state-messaging']:
            item = source / name
            if item.is_dir(): shutil.copytree(item, home / name)
            elif item.is_file(): shutil.copy2(item, home / name)
    except BaseException:
        shutil.rmtree(home)
        raise


def login_service(home, remove=False):
    if sys.platform != 'darwin': raise ValueError('Login service integration is currently macOS-only.')
    config = settings(home)
    label = 'eu.farmy.local.' + config['installationId'][:12]
    path = Path.home() / 'Library/LaunchAgents' / (label + '.plist')
    domain = f'gui/{os.getuid()}'
    if remove:
        subprocess.run(['launchctl', 'bootout', domain + '/' + label], capture_output=True)
        path.unlink(missing_ok=True)
        for _ in range(150):
            try:
                with exclusive(home):
                    print('Removed login service. Workspace data is retained.')
                    return
            except ValueError: time.sleep(.1)
        raise RuntimeError('Login registration removed but workspace is still busy; inspect runtime.log.')
    launcher = os.environ.get('FARMY_LAUNCHER')
    if not launcher or not Path(launcher).is_file():
        raise ValueError('Install Farmy first, then invoke service-install through its installed launcher.')
    with exclusive(home):
        if path.exists(): raise ValueError('Login service already configured; use service-remove before reinstalling it.')
        path.parent.mkdir(parents=True, exist_ok=True)
        definition = dict(Label=label, ProgramArguments=[launcher, '--home', str(home), 'serve'],
            RunAtLoad=True, KeepAlive=False, WorkingDirectory=str(home),
            StandardOutPath=str(home/'runtime.log'), StandardErrorPath=str(home/'runtime.log'),
            EnvironmentVariables={'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'})
        with path.open('xb') as output:
            os.chmod(path, 0o600);plistlib.dump(definition, output)
    result = subprocess.run(['launchctl', 'bootstrap', domain, str(path)], capture_output=True, text=True)
    if result.returncode:
        path.unlink(missing_ok=True)
        raise RuntimeError('Login service could not start: ' + result.stderr.strip())
    for _ in range(150):
        try:
            control(home)
            print('Installed and started login service:', label)
            return
        except (OSError, ValueError): time.sleep(.1)
    raise RuntimeError('Login service is registered but not healthy; inspect runtime.log or use service-remove.')


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=default_home(), help='Private persistent workspace directory')
    parser.add_argument('--version', action='version', version=VERSION)
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init');init.add_argument('--source', type=Path, required=True);init.add_argument('--port', type=int, default=54800)
    for action in ('start','stop','status','open','doctor','service-install','service-remove'): sub.add_parser(action)
    serving = sub.add_parser('serve');serving.add_argument('--run-id', default='foreground')
    copying = sub.add_parser('backup');copying.add_argument('destination', type=Path)
    restoring = sub.add_parser('restore');restoring.add_argument('source', type=Path)
    args = parser.parse_args();home = args.home.absolute()
    try:
        if args.action == 'init':
            initialise(home, args.source, args.port);print('Initialised private workspace:', home)
        elif args.action == 'serve': serve(home, args.run_id)
        elif args.action == 'service-install': login_service(home)
        elif args.action == 'service-remove': login_service(home, remove=True)
        elif args.action == 'start': start(home);print('Farmy is running. Use farmy open to open your private local interface.')
        elif args.action == 'stop': stop(home);print('Stopped. Workspace data is retained.')
        elif args.action == 'status':
            _, result = control(home);print('Running Farmy', result['version'], 'at', home)
        elif args.action == 'open':
            running, _ = control(home)
            url = f'http://127.0.0.1:{running["port"]}/#access={running["token"]}'
            if sys.platform == 'darwin': subprocess.run(['open', url], check=True)
            else: print(url)
        elif args.action == 'doctor':
            config = settings(home)
            print('Version:', VERSION, '\nWorkspace:', home, '\nSource available:', Path(config['source']).is_dir())
            print('OpenSSL available:', bool(shutil.which('openssl')))
            try: control(home);print('Runtime: healthy')
            except (OSError, ValueError): print('Runtime: stopped or unavailable')
        elif args.action == 'backup': backup(home, args.destination);print('Stopped-workspace backup saved:', args.destination)
        elif args.action == 'restore': restore(home, args.source);print('Restored into:', home, '(fresh credentials on next start)')
    except (OSError, ValueError, RuntimeError, Fault) as exc:
        parser.exit(1, f'Farmy: {exc}\n')


if __name__ == '__main__': main()
