#!/usr/bin/env python3
"""Local guided deployment; Scaleway CLI owns credentials. No credential inputs."""
import json
import os
from pathlib import Path
import re
import subprocess
import uuid


def cli(*args):
    try:
        result = subprocess.run(['scw', *args, '-o', 'json'], capture_output=True,
                                text=True, timeout=120, check=True)
        return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        # Provider output can contain credentials. Never echo it.
        raise RuntimeError('Scaleway command failed or timed out. Inspect the console; do not blindly retry creation.') from None


def plan(project, namespace, region, name, image):
    for value in (project, namespace):
        if str(uuid.UUID(value)) != value:
            raise ValueError('Use canonical project and namespace UUIDs.')
    if region not in ('fr-par', 'nl-ams', 'pl-waw'):
        raise ValueError('Unsupported region for this profile.')
    if not re.fullmatch(r'[a-z][a-z0-9-]{2,49}', name):
        raise ValueError('Name must be 3–50 lowercase letters, digits or hyphens.')
    if not re.fullmatch(r'ghcr\.io/[a-z0-9_-]+/[a-z0-9_/-]+@sha256:[0-9a-f]{64}', image):
        raise ValueError('Use the public GitHub image reference pinned by sha256 digest.')
    return dict(project=project, namespace=namespace, region=region, name=name, image=image,
                privacy='private', minScale=0, maxScale=1, memoryMB=256, cpu=250, timeoutSeconds=10)


def preflight(p, run=cli):
    ns = run('container', 'namespace', 'get', p['namespace'], 'region='+p['region'])
    if ns.get('project_id') != p['project'] or ns.get('region') != p['region']:
        raise ValueError('Namespace does not belong to the selected project and region.')
    if ns.get('environment_variables') or ns.get('secret_environment_variables'):
        raise ValueError('Use a dedicated empty namespace: inherited variables/secrets are not allowed.')
    items = run('container', 'container', 'list', 'namespace-id='+p['namespace'], 'region='+p['region'])
    if not isinstance(items, list) or items:
        raise ValueError('Use a dedicated namespace with no containers. Inspect partial deployments in the console.')


def create_args(p):
    return ['container', 'container', 'create', 'namespace-id='+p['namespace'],
            'region='+p['region'], 'name='+p['name'], 'image='+p['image'],
            'privacy=private', 'https-connections-only=true', 'min-scale=0', 'max-scale=1',
            'memory-limit-bytes=268435456', 'mvcpu-limit=250', 'timeout=10s', 'port=8080',
            'protocol=http1', 'liveness-probe.http.path=/health']


def check_cli():
    result = subprocess.run(['scw', 'container', 'container', 'create', '--help'],
                            capture_output=True, text=True, timeout=10, check=True)
    required = ('memory-limit-bytes', 'mvcpu-limit', 'https-connections-only', 'liveness-probe.http.path')
    if not all(name in result.stdout for name in required):
        raise ValueError('Unsupported Scaleway CLI interface. Use CLI 2.60.0 or a compatible release.')


def main():
    print('Farmy optional processor · Scaleway\nNo secrets are requested. Authenticate locally with scw init first.\n'
          'Create/select a separate Farmy project and an empty Serverless Containers namespace in the console.\n'
          'Namespace creation may also create registry resources. Review pricing and set billing alerts there.\n'
          'This installer creates one container. It uploads no wallet, files or keys.')
    check_cli()
    p = plan(input('Farmy project UUID: ').strip(), input('Empty namespace UUID: ').strip(),
             input('Region (fr-par / nl-ams / pl-waw): ').strip(),
             input('Container name [farmy-text]: ').strip() or 'farmy-text',
             input('Public GitHub image @sha256 digest: ').strip())
    preflight(p)
    print(json.dumps(p, indent=2))
    print('Scale limits are NOT a spending cap. Provider logs/network/registry can incur costs.\n'
          'Deployment is experimental; use synthetic text only until remote grants are implemented.')
    if input('Type the project UUID to authorise this deployment, or Enter to stop: ').strip() != p['project']:
        print('No resources created.'); return
    # Exclusive private receipt acts as an uncertainty latch, before the mutating call.
    folder = Path('.farmy/deployments'); folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    receipt = folder / (p['namespace']+'.json')
    fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as out:
        json.dump({'plan': p, 'status': 'creation_pending_inspect_console_before_retry'}, out)
        out.flush(); os.fsync(out.fileno())
    result = cli(*create_args(p))
    container_id = str(uuid.UUID(result['id']))
    with receipt.open('w') as out:
        json.dump({'plan': p, 'id': container_id, 'status': 'submitted_not_verified'}, out, indent=2)
    print('Deployment submitted. Container ID: '+container_id)
    print('Check readiness and private access in the console. Receipt: '+str(receipt))
    print('To remove only this container: scw container container delete '+container_id+' region='+p['region'])

if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, EOFError, subprocess.SubprocessError) as exc:
        print('Stopped: '+str(exc)); raise SystemExit(1)
