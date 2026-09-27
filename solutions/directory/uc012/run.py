"""Browse a selected read-only folder and admit exact managed copies."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('workbench', ROOT / 'solutions/interactive/uc010/server.py')
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
SERVICES = dict(server.managed.SERVICES, **{'connector.local': 'modules/connectors/directory/service.py'})


def bootstrap(directory, source, identity_keys=None, extra_services=None):
    source = Path(source).absolute()
    if source.is_symlink() or not source.is_dir():
        raise ValueError('Select an existing directory, not a symbolic link')
    directory = server.managed.bootstrap(directory, identity_keys=identity_keys, extra_services=extra_services)
    path = directory / 'connector.local.json'
    config = json.loads(path.read_text())
    config.update(sourceRoot=str(source), implementationId='farmy.reference.directory', implementationVersion='0.1.0')
    path.write_text(json.dumps(config, indent=2))
    return directory


class Workbench(server.Workbench):
    def catalogue(self):
        return self.call('folder.browse', server.managed.scope(self.session['source']), grant=self.session['sourceGrant'])['entries']

    def state(self, role):
        result = super().state(role)
        if role == 'owner':
            result.update(directory=True, catalogue=self.catalogue())
        return result

    def entry_title(self, entry):
        for item in self.catalogue():
            if item['entry'] == entry:
                return item['path']
        raise server.Fault('not_found')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['launch', 'demo'])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    if args.action == 'launch' and args.source is None:
        parser.error('launch requires --source PATH')
    with tempfile.TemporaryDirectory(prefix='farmy-uc012-') as temp:
        source = args.source
        if source is None:
            source = Path(temp) / 'example-source'
            (source / 'records').mkdir(parents=True)
            (source / 'records' / 'example.json').write_text('{"example":42}\n')
        directory = bootstrap(Path(temp) / 'runtime', source)
        with server.managed.core.Processes(directory, SERVICES):
            workbench = Workbench(directory)
            if args.action == 'demo':
                catalogue = workbench.catalogue()
                eligible = next(item for item in catalogue if not item['reason'])
                preview = workbench.preview(eligible['entry'])
                result = workbench.action('owner', 'admit', dict(entry=eligible['entry'], sha256=preview['sha256'], policy='restricted', key='directory-demo'))
                workbench.action('owner','grant',dict(id=result['id'],key='directory-grant'))
                assert workbench.action('consumer','read',{'id':result['id']})['text'] == preview['text']
                workbench.action('owner','revoke',dict(id=result['id'],key='directory-revoke'))
                server.managed.core.expect_fault('denied',lambda:workbench.action('consumer','read',{'id':result['id']}))
                print(f'PASS directory catalogue ({len(catalogue)} entries), admission, granted read and revocation')
                return
            with server.Server(workbench, args.port) as http:
                print(f'Open http://127.0.0.1:{http.server_port}/#access={workbench.session["owner"]}', flush=True)
                print('Read-only source. Temporary managed copies; one-hour development grants.', flush=True)
                try:
                    http.serve_forever()
                except KeyboardInterrupt:
                    pass


if __name__ == '__main__':
    main()
