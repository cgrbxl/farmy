"""UC-008: two Knowledge instances, explicit binding, replacement and public rebuild."""
import argparse
import importlib.util
import json
from pathlib import Path
import secrets
import tempfile

ROOT = Path(__file__).resolve().parents[3]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

path = load('uc008_document_path', 'solutions/document-path/uc002/run.py')
monitor = load('uc008_monitor', 'solutions/operations/uc005/run.py')
core = path.core
from bindings import resolve, admit
from farmy_transport.http import exchange, request

A, B = 'knowledge.local', 'knowledge.secondary'
ALTERNATIVE = 'modules/knowledge/ledger/service.py'
SERVICES = dict(path.SERVICES, **{B: 'modules/knowledge/evidence/service.py'})
INVENTORY = {name: {'family': family, 'name': label} for name, family, label in [
    ('wallet.local', 'wallet', 'Wallet'), ('connector.local', 'connectors', 'Local Folder'),
    ('processing.local', 'processing', 'Text Processing'), ('workflow.local', 'workflow', 'Bound Workflow'),
    (A, 'knowledge', 'Knowledge A · evidence'), (B, 'knowledge', 'Knowledge B')]}


def binding(target, revision=1):
    return {'profile': 'farmy.integration/0.1-draft', 'bindingId': 'binding.knowledge',
            'revision': revision, 'walletId': 'wallet.demo', 'instanceId': target,
            'capabilityId': 'farmy.knowledge', 'contractVersion': '0.2-draft',
            'operations': ['evidence.index', 'evidence.query'], 'requiredFeatures': [],
            'scopeId': 'collection.local'}


def write_config(directory, identity, **values):
    config = core.config(directory, identity)
    config.update(values)
    (directory / (identity + '.json')).write_text(json.dumps(config, indent=2))


def bootstrap(directory):
    directory = core.bootstrap(directory, dict(SERVICES, **{'monitor.local': 'solutions/operations/uc005/server.py'}))
    (directory / 'source/report.txt').write_bytes(path.REPORT)
    (directory / 'knowledge-binding.json').write_text(json.dumps(binding(A), indent=2))
    for identity in [*SERVICES, 'monitor.local', 'owner', 'reader', 'denied', 'unknown']:
        write_config(directory, identity, environmentId='environment.uc008-local',
                     bootstrapProfile='uc008.bootstrap', compositionRevision=1)
        if identity in SERVICES:
            write_config(directory, identity, monitorSubjects=['monitor.local'],
                         implementationVersion='0.4.0' if identity == 'wallet.local' else '0.1.1')
        if identity in (A, B):
            write_config(directory, identity, operators=[*core.config(directory, identity)['operators'], 'reader'])
    write_config(directory, 'wallet.local', readSubjects=['owner', 'reader', 'denied', 'processing.local'],
                 permissionScopes=path.SCOPES + [dict(s, audience=B) for s in path.SCOPES if s['audience'] == A])
    write_config(directory, 'workflow.local', knowledgeBinding=str(directory / 'knowledge-binding.json'),
                 implementationVersion='0.2.0')
    config = core.config(directory, 'monitor.local')
    config = {k: config[k] for k in ('identity', 'walletId', 'ca', 'cert', 'key', 'endpoints')}
    config.update(inventory=INVENTORY, browserToken=secrets.token_urlsafe(32))
    config['endpoints'] = {k: dict(v, timeoutSeconds=3) for k, v in config['endpoints'].items() if k in SERVICES}
    (directory / 'monitor.local.json').write_text(json.dumps(config, indent=2))
    return directory


def select(directory, processes, target, revision):
    # Explicit quiesce/restart: running jobs never observe a partially rewritten binding.
    processes.stop('workflow.local')
    (directory / 'knowledge-binding.json').write_text(json.dumps(binding(target, revision), indent=2))
    processes.start('workflow.local')


def permissions(directory, resource, target):
    source = core.grant(directory, resource, 'processing.local')
    disclosure = path.scoped(directory, resource, target, 'processing.local', 'extraction.get', 'uc002.index')
    index = path.scoped(directory, resource, 'workflow.local', target, 'evidence.index', 'uc002.index')
    query = path.scoped(directory, resource, 'reader', target, 'evidence.query', 'uc002.query')
    return {'sourceReadGrant': source['grantId'], 'disclosureGrant': disclosure['grantId'],
            'indexGrant': index['grantId']}, query


def query(directory, resource, permission, target, identity='reader'):
    client = core.config(directory, identity)
    return exchange(client, target, request(client, target, 'evidence.query', {'field': 'crop'},
                    refs=core.refs(resource), grant=permission['grantId']))['evidence']


def bound_query(directory, resource, permission):
    client = core.config(directory, 'reader')
    selected = resolve(directory / 'knowledge-binding.json', client['walletId'],
                       'farmy.knowledge', 'evidence.query', '0.2-draft')
    return query(directory, resource, permission, admit(client, selected))


def execute(directory, resource, grants, key):
    return path.call(directory, 'job.run', grants, refs=core.refs(resource), key=key)


def replace(directory, processes):
    # Private stores are neither inspected nor translated by the solution.
    processes.stop(B)
    write_config(directory, B, state=str(directory / 'state-ledger-secondary'),
                 implementationId='farmy.reference.knowledge-ledger', implementationVersion='0.1.0')
    processes.services[B] = ALTERNATIVE
    processes.start(B)
    monitor_config = core.config(directory, 'monitor.local')
    monitor_config['inventory'][B]['name'] = 'Knowledge B · ledger'
    write_config(directory, 'monitor.local', inventory=monitor_config['inventory'])


def exercise(directory, processes):
    resource = core.call(directory, 'resource.register', {'path': 'report.txt'})
    grants_a, query_a = permissions(directory, resource, A)
    grants_b, query_b = permissions(directory, resource, B)
    execute(directory, resource, grants_a, 'key.a')
    evidence = bound_query(directory, resource, query_a)
    select(directory, processes, B, 2)
    core.expect_fault('denied', lambda: bound_query(directory, resource, query_a))
    execute(directory, resource, grants_b, 'key.b')
    assert bound_query(directory, resource, query_b) == evidence
    print('PASS two separately authorised Knowledge instances return identical exact-source evidence', flush=True)
    replace(directory, processes)
    core.expect_fault('not_found', lambda: bound_query(directory, resource, query_b))
    assert query(directory, resource, query_a, A) == evidence
    # Pin a new binding revision and use a fresh job key for a deliberate rebuild.
    select(directory, processes, B, 3)
    core.expect_fault('conflict', lambda: execute(directory, resource, grants_b, 'key.b'))
    execute(directory, resource, grants_b, 'key.rebuild')
    assert bound_query(directory, resource, query_b) == evidence
    print('PASS replacement starts empty; public-API rebuild restores evidence without opening the previous store', flush=True)
    processes.stop(B)
    processes.start(B)
    assert bound_query(directory, resource, query_b) == evidence
    path.call(directory, 'access.revoke', {'grantId': query_b['grantId']}, revision=1)
    core.expect_fault('denied', lambda: bound_query(directory, resource, query_b))
    assert query(directory, resource, query_a, A) == evidence
    fresh = path.scoped(directory, resource, 'reader', B, 'evidence.query', 'uc002.query')
    processes.stop('wallet.local')
    try:
        for target, permission in [(A, query_a), (B, fresh)]:
            core.expect_fault('unavailable', lambda: query(directory, resource, permission, target))
    finally:
        processes.start('wallet.local')
    print('PASS restart, audience separation, binding pinning, revocation and authority outage', flush=True)
    state = monitor.bridge.snapshot(core.config(directory, 'monitor.local'))
    assert len(state['nodes']) == 6 and all(n['status'] == 'available' for n in state['nodes'])
    print('PASS live monitor discovers both Knowledge instances through their public summaries', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo', 'launch'])
    parser.add_argument('--port', type=int, help='Dashboard port; default falls back to a free port if occupied')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='farmy-uc008-') as temp:
        directory = bootstrap(temp)
        with core.Processes(directory, dict(SERVICES)) as processes:
            exercise(directory, processes)
            if args.action == 'launch':
                monitor.ui(directory, args.port)
    print('Demo complete. All six module processes stopped.')


if __name__ == '__main__':
    main()
