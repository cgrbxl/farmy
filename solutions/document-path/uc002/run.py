"""UC-002: a synthetic text report to permission-checked exact-source evidence."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('core_runtime', ROOT / 'solutions/core/uc001/run.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
from farmy_transport.http import exchange, request, utc

SERVICES = dict(core.SERVICES, **{'processing.local': 'modules/processing/text_field/service.py',
                                'knowledge.local': 'modules/knowledge/evidence/service.py',
                                'workflow.local': 'modules/workflow/reference/service.py'})
REPORT = b'Farmy synthetic report\ncrop: wheat\n'
SCOPES = [{'audience': 'processing.local', 'operation': 'extraction.get', 'purpose': 'uc002.index'},
          {'audience': 'knowledge.local', 'operation': 'evidence.index', 'purpose': 'uc002.index'},
          {'audience': 'knowledge.local', 'operation': 'evidence.query', 'purpose': 'uc002.query'}]
TARGETS = {'extraction': 'processing.local', 'evidence': 'knowledge.local', 'job': 'workflow.local'}


def bootstrap(directory):
    directory = core.bootstrap(directory, SERVICES)
    (directory / 'source/report.txt').write_bytes(REPORT)
    for identity in [*SERVICES, 'owner', 'reader', 'denied', 'unknown']:
        path = directory / (identity + '.json')
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc002-local', bootstrapProfile='uc002.bootstrap',
                      compositionRevision=1)
        if identity == 'wallet.local':
            config.update(readSubjects=['owner', 'reader', 'denied', 'processing.local'], permissionScopes=SCOPES,
                          implementationVersion='0.2.0')
        path.write_text(json.dumps(config, indent=2))
    return directory


def call(directory, operation, payload=None, identity='owner', **kwargs):
    target = TARGETS.get(operation.split('.')[0], 'wallet.local')
    config = core.config(directory, identity)
    return exchange(config, target, request(config, target, operation, payload or {}, **kwargs))


def scoped(directory, resource, subject, audience, operation, purpose):
    return call(directory, 'access.issue', {'resourceId': resource['resourceId'], 'versionId': resource['versionId'],
                'subjectId': subject, 'audience': audience, 'operation': operation, 'purpose': purpose,
                'expiresAt': utc(600)}, refs=core.refs(resource))


def permissions(directory, resource):
    source = core.grant(directory, resource, 'processing.local')
    disclosure = scoped(directory, resource, 'knowledge.local', 'processing.local', 'extraction.get', 'uc002.index')
    index = scoped(directory, resource, 'workflow.local', 'knowledge.local', 'evidence.index', 'uc002.index')
    query = scoped(directory, resource, 'reader', 'knowledge.local', 'evidence.query', 'uc002.query')
    return {'sourceReadGrant': source['grantId'], 'disclosureGrant': disclosure['grantId'],
            'indexGrant': index['grantId']}, query


def query(directory, resource, permission, identity='reader'):
    return call(directory, 'evidence.query', {'field': 'crop'}, identity=identity,
                refs=core.refs(resource), grant=permission['grantId'])['evidence']


def demo(directory):
    with core.Processes(directory, SERVICES) as processes:
        resource = core.call(directory, 'resource.register', {'path': 'report.txt'})
        grants, permission = permissions(directory, resource)
        result = call(directory, 'job.run', grants, refs=core.refs(resource), key='key.demo')
        evidence = query(directory, resource, permission)
        assert evidence['value'] == 'wheat' and evidence['source'] == core.refs(resource)[0]
        assert REPORT[evidence['byteStart']:evidence['byteEnd']].decode() == evidence['quote']
        print('PASS extracted crop=wheat with exact source version, digest and quoted evidence')
        duplicate = call(directory, 'job.run', grants, refs=core.refs(resource), key='key.demo')
        second_job = call(directory, 'job.run', grants, refs=core.refs(resource), key='key.second-delivery')
        assert result == duplicate and result['proposalId'] == second_job['proposalId']
        print('PASS duplicate jobs converge on one accepted evidence entry')
        for service in ('processing.local', 'knowledge.local', 'workflow.local'):
            processes.stop(service)
            processes.start(service)
        assert query(directory, resource, permission) == evidence
        print('PASS extraction, job state and evidence survive service restarts')
        recovery = core.call(directory, 'resource.register', {'path': 'report.txt'})
        recovery_grants, recovery_permission = permissions(directory, recovery)
        processes.stop('knowledge.local')
        core.expect_fault('unavailable', lambda: call(directory, 'job.run', recovery_grants,
                                                     refs=core.refs(recovery), key='key.recovery'))
        processes.stop('workflow.local')
        processes.start('workflow.local')
        processes.start('knowledge.local')
        resumed = call(directory, 'job.run', recovery_grants, refs=core.refs(recovery), key='key.recovery')
        assert resumed['status'] == 'succeeded' and query(directory, recovery, recovery_permission)['value'] == 'wheat'
        print('PASS interrupted indexing resumes after Workflow restart')
        core.expect_fault('denied', lambda: query(directory, resource, permission, 'denied'))
        call(directory, 'access.revoke', {'grantId': permission['grantId']}, revision=1)
        core.expect_fault('denied', lambda: query(directory, resource, permission))
        processes.stop('wallet.local')
        core.expect_fault('unavailable', lambda: query(directory, recovery, recovery_permission))
        print('PASS denied/revoked readers and unavailable authority disclose no evidence')
    print('Demo complete. All five processes stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo', 'bootstrap', 'serve', 'request'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--service', choices=[name.split('.')[0] for name in SERVICES])
    parser.add_argument('--operation')
    parser.add_argument('--payload', default='{}')
    parser.add_argument('--refs', default='[]')
    parser.add_argument('--identity', choices=['owner', 'reader', 'denied'], default='owner')
    parser.add_argument('--grant', default='grant.owner-bootstrap')
    parser.add_argument('--key')
    parser.add_argument('--revision', type=int)
    args = parser.parse_args()
    if args.action == 'demo':
        if args.directory:
            parser.error('demo uses its own temporary state')
        with tempfile.TemporaryDirectory(prefix='farmy-uc002-') as directory:
            demo(bootstrap(directory))
    elif args.directory is None:
        parser.error('--directory is required')
    elif args.action == 'bootstrap':
        print(bootstrap(args.directory))
    elif args.action == 'serve':
        if not args.service:
            parser.error('--service is required')
        os.execve(sys.executable, core.command(args.directory, args.service + '.local', SERVICES), core.environment())
    else:
        if not args.operation:
            parser.error('--operation is required')
        print(json.dumps(call(args.directory, args.operation, json.loads(args.payload), args.identity,
                              refs=json.loads(args.refs), grant=args.grant, key=args.key, revision=args.revision), indent=2))


if __name__ == '__main__':
    main()
