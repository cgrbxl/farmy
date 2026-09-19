"""UC-004: a permission-checked, cited crop answer through a selected local model."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

previous = load('uc002_run', 'solutions/document-path/uc002/run.py')
core = previous.core
adapter = load('ollama_adapter', 'modules/model-access/ollama/service.py')
from farmy_transport.http import exchange, request, utc
from farmy_transport.local import digest

SERVICES = dict(previous.SERVICES, **{'model.local': 'modules/model-access/ollama/service.py',
                                     'assistance.local': 'modules/assistance/cited_crop/service.py'})
MODEL = 'qwen2.5:3b'
ENDPOINT = 'http://127.0.0.1:11434'
ROUTE = 'route.local-crop'
SCOPES = previous.SCOPES + [
    {'audience': 'model.local', 'operation': 'model.invoke', 'purpose': 'uc004.invoke'},
    {'audience': 'assistance.local', 'operation': 'answer.create', 'purpose': 'uc004.answer'}]


def bootstrap(directory, model=MODEL, endpoint=ENDPOINT, profile=None):
    if profile is None:
        profile = {'routeId': ROUTE, 'model': model, 'endpoint': endpoint}
        available = adapter.ollama(profile, '/api/tags')
        matches = [m for m in available['models'] if m['name'] == model and m.get('details', {}).get('format') == 'gguf']
        if len(matches) != 1:
            raise ValueError('The explicitly selected local model must already be installed; no automatic download or fallback.')
        profile.update(modelDigest=matches[0]['digest'])
    directory = core.bootstrap(directory, SERVICES)
    (directory / 'source/report.txt').write_bytes(previous.REPORT)
    for identity in [*SERVICES, 'owner', 'reader', 'denied', 'unknown']:
        path = directory / (identity + '.json')
        config = json.loads(path.read_text())
        config.update(environmentId='environment.uc004-local', bootstrapProfile='uc004.bootstrap', compositionRevision=1)
        for name in ('model.local', 'assistance.local'):
            config['endpoints'][name]['timeoutSeconds'] = 55
        if identity == 'wallet.local':
            config.update(readSubjects=['owner', 'reader', 'denied', 'processing.local'],
                          permissionScopes=SCOPES, implementationVersion='0.3.0')
        if identity == 'model.local':
            config.update(modelProfile=profile, approvedProfileDigest=digest(profile))
        path.write_text(json.dumps(config, indent=2))
    return directory


def fixture(directory):
    resource = core.call(directory, 'resource.register', {'path': 'report.txt'})
    grants, _ = previous.permissions(directory, resource)
    previous.call(directory, 'job.run', grants, refs=core.refs(resource), key='job.' + resource['resourceId'])
    def grant(subject, target, op, purpose):
        return previous.scoped(directory, resource, subject, target, op, purpose)['grantId']
    payload = {'question': 'Which crop is recorded?', 'routeId': ROUTE,
               'knowledgeGrant': grant('assistance.local', 'knowledge.local', 'evidence.query', 'uc002.query'),
               'modelEvidenceGrant': grant('model.local', 'knowledge.local', 'evidence.query', 'uc002.query'),
               'modelGrant': grant('assistance.local', 'model.local', 'model.invoke', 'uc004.invoke')}
    permission = grant('reader', 'assistance.local', 'answer.create', 'uc004.answer')
    return resource, payload, permission


def answer(directory, resource, payload, permission, identity='reader', key='key.answer'):
    config = core.config(directory, identity)
    body = request(config, 'assistance.local', 'answer.create', payload, refs=core.refs(resource), grant=permission, key=key)
    body['deadline'] = utc(55)
    return exchange(config, 'assistance.local', body)


def demo(directory):
    with core.Processes(directory, SERVICES) as processes:
        resource, payload, permission = fixture(directory)
        result = answer(directory, resource, payload, permission)
        assert result['text'] == 'The recorded crop is wheat.'
        assert result['citation']['source'] == core.refs(resource)[0]
        print('PASS selected local model answered with validated exact-source citation')
        print(json.dumps(result, indent=2))
        for service in ('assistance.local', 'model.local'):
            processes.stop(service)
            processes.start(service)
        assert answer(directory, resource, payload, permission) == result
        print('PASS restart/replay returns the same answer without another model invocation')
        core.expect_fault('denied', lambda: answer(directory, resource, payload, permission, identity='denied'))
        core.expect_fault('denied', lambda: answer(directory, resource, dict(payload, routeId='route.unapproved'), permission, key='key.egress'))
        print('PASS unauthorised reader and unapproved model route rejected')
        previous.call(directory, 'access.revoke', {'grantId': payload['modelGrant']}, revision=1)
        core.expect_fault('denied', lambda: answer(directory, resource, payload, permission))
        processes.stop('wallet.local')
        core.expect_fault('unavailable', lambda: answer(directory, resource, payload, permission))
        print('PASS revoked model grant and unavailable authority fail closed even on replay')
    print('Demo complete. All seven Farmy processes stopped; existing Ollama service retained.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['demo', 'bootstrap', 'serve', 'example'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--model', default=MODEL)
    parser.add_argument('--endpoint', default=ENDPOINT)
    parser.add_argument('--service', choices=list(SERVICES))
    args = parser.parse_args()
    if args.action == 'demo':
        if args.directory:
            parser.error('demo owns temporary state; omit --directory')
        with tempfile.TemporaryDirectory(prefix='farmy-uc004-') as directory:
            demo(bootstrap(directory, args.model, args.endpoint))
    elif args.directory is None:
        parser.error('--directory is required')
    elif args.action == 'bootstrap':
        print(bootstrap(args.directory, args.model, args.endpoint))
    elif args.action == 'serve':
        if args.service is None:
            parser.error('--service is required')
        os.execve(sys.executable, core.command(args.directory, args.service, SERVICES), core.environment())
    else:
        resource, payload, permission = fixture(args.directory)
        print(json.dumps(answer(args.directory, resource, payload, permission), indent=2))


if __name__ == '__main__':
    main()
