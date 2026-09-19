"""UC-005 live, read-only installation dashboard. No model inference by default."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

answer = load('uc004_run', 'solutions/assisted-answer/uc004/run.py')
sensor = load('uc003_run', 'solutions/sensor-path/uc003/run.py')
bridge = load('uc005_server', 'solutions/operations/uc005/server.py')
core = answer.core
SERVICES = dict(answer.SERVICES, **{'sensor.local': 'modules/connectors/synthetic_sensor/service.py'})
INVENTORY = {name: {'family': family, 'name': label} for name, family, label in [
    ('wallet.local', 'wallet', 'Wallet'), ('connector.local', 'connectors', 'Local Folder'),
    ('sensor.local', 'connectors', 'Synthetic Sensor'), ('processing.local', 'processing', 'Text Processing'),
    ('knowledge.local', 'knowledge', 'Evidence Knowledge'), ('workflow.local', 'workflow', 'Workflow'),
    ('model.local', 'model-access', 'Model access'), ('assistance.local', 'assistance', 'Cited Assistance')]}


def bootstrap(directory, with_model=False):
    profile = None if with_model else {'routeId': answer.ROUTE, 'model': answer.MODEL,
        'endpoint': answer.ENDPOINT, 'modelDigest': '357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b'}
    # The bridge gets its own enrolled certificate, never the owner's key.
    directory = answer.bootstrap(directory, profile=profile,
                                 services=dict(SERVICES, **{'monitor.local': 'solutions/operations/uc005/server.py'}))
    for identity in [*SERVICES, 'monitor.local', 'owner', 'reader', 'denied', 'unknown']:
        path = directory / (identity + '.json')
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc005-local', bootstrapProfile='uc005.bootstrap')
        if identity in SERVICES:
            config['monitorSubjects'] = ['monitor.local']
            config['implementationVersion'] = '0.4.0' if identity == 'wallet.local' else '0.1.1'
        if identity == 'wallet.local':
            config['sourceConnectors'] = ['sensor.local']
        if identity == 'sensor.local':
            config['implementationId'] = 'farmy.reference.synthetic-sensor'
        if identity == 'monitor.local':
            config.update(inventory=INVENTORY, browserToken=secrets.token_urlsafe(32))
            # Only this bridge's own credential and explicitly inventoried targets remain.
            config = {k: config[k] for k in ('identity','walletId','ca','cert','key','endpoints','inventory','browserToken')}
            config['endpoints'] = {k: dict(v, timeoutSeconds=3) for k, v in config['endpoints'].items() if k in SERVICES}
        path.write_text(json.dumps(config, indent=2))
    return directory


def seed(directory, with_model=False):
    resource, payload, permission = answer.fixture(directory)
    if with_model:
        answer.answer(directory, resource, payload, permission)
    source = sensor.register(directory)
    for value in (18.5, 19.0, 19.5):
        sensor.append(directory, source, value)
    sensor.read(directory, source, sensor.grant(directory, source))
    core.expect_fault('denied', lambda: sensor.read(directory, source, {'grantId': 'grant.missing'}, identity='denied'))


def ui(directory, port):
    config = core.config(directory, 'monitor.local')
    server = bridge.Server(config, port)
    print(f'Open http://127.0.0.1:{server.server_port}/#access={config["browserToken"]}', flush=True)
    print('Read-only synthetic installation. Ctrl-C stops this runner; closing the browser does not.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def demo(directory, with_model=False):
    with core.Processes(directory, SERVICES) as processes:
        seed(directory, with_model)
        config = core.config(directory, 'monitor.local')
        state = bridge.snapshot(config)
        assert len(state['nodes']) == 8 and all(n['status'] == 'available' for n in state['nodes'])
        counts = {n['instanceId']: {c['label']: c['value'] for c in n['counts']} for n in state['nodes']}
        assert counts['sensor.local']['Observations'] == 3 and counts['knowledge.local']['Evidence entries'] == 1
        print('PASS eight authenticated service summaries show real synthetic contents')
        core.expect_fault('denied', lambda: answer.exchange(core.config(directory,'reader'), 'wallet.local', path='/farmy/v0/monitor/summary'))
        print('PASS ordinary readers cannot inspect installation summaries')
        processes.stop('knowledge.local')
        failed = bridge.snapshot(config)
        assert next(n for n in failed['nodes'] if n['instanceId']=='knowledge.local')['counts'] == []
        assert next(n for n in failed['nodes'] if n['instanceId']=='knowledge.local')['status'] == 'unavailable'
        processes.start('knowledge.local')
        assert next(n for n in bridge.snapshot(config)['nodes'] if n['instanceId']=='knowledge.local')['status'] == 'available'
        print('PASS stopped module is unavailable without stale counts; restart recovers')
    print('Demo complete. All eight Farmy processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo','launch','bootstrap','serve','dashboard','seed'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--with-local-model', action='store_true')
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--service', choices=list(SERVICES))
    args = parser.parse_args()
    if args.action in ('demo','launch'):
        if args.directory: parser.error('demo/launch own temporary state; omit --directory')
        with tempfile.TemporaryDirectory(prefix='farmy-uc005-') as temp:
            directory = bootstrap(temp, args.with_local_model)
            if args.action == 'demo': demo(directory, args.with_local_model)
            else:
                with core.Processes(directory, SERVICES):
                    seed(directory, args.with_local_model)
                    ui(directory, args.port)
    elif args.directory is None: parser.error('--directory is required')
    elif args.action == 'bootstrap': print(bootstrap(args.directory, args.with_local_model))
    elif args.action == 'serve':
        if not args.service: parser.error('--service is required')
        os.execve(sys.executable, core.command(args.directory, args.service, SERVICES), core.environment())
    elif args.action == 'dashboard': ui(args.directory, args.port)
    else: seed(args.directory, args.with_local_model)


if __name__ == '__main__': main()
