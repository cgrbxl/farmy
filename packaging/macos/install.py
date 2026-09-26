"""Install an unpacked, platform-specific Farmy release without a source checkout."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import venv


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix',type=Path,default=Path.home()/'.local/share/farmy')
    parser.add_argument('--home',type=Path,default=Path(os.environ.get('FARMY_HOME',str(Path.home()/'Library/Application Support/Farmy'))))
    args=parser.parse_args();bundle=Path(__file__).resolve().parent
    manifest=json.loads((bundle/'release.json').read_text())
    if manifest['system'] != platform.system() or manifest['machine'] != platform.machine() or manifest['python'] != list(sys.version_info[:2]):
        parser.error('Release platform/Python mismatch; build the appropriate artifact.')
    for relative,digest in manifest['files'].items():
        if hashlib.sha256((bundle/relative).read_bytes()).hexdigest()!=digest:
            parser.error('Artifact checksum mismatch: '+relative)
    prefix=args.prefix.absolute();prefix.mkdir(parents=True,exist_ok=True)
    lock=None
    if (args.home/'installation.json').exists():
        if json.loads((args.home/'installation.json').read_text()).get('schema') != 1:
            parser.error('Workspace schema is not supported by this release.')
        lock=(args.home/'runtime.lock').open('a')
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:parser.error('Stop Farmy before switching installed releases.')
    target=prefix/'releases'/manifest['build']
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        try:
            shutil.copytree(bundle/'app',target/'app')
            shutil.copy2(bundle/'release.json',target/'release.json')
            venv.EnvBuilder(with_pip=True).create(target/'venv')
            python=target/'venv/bin/python'
            subprocess.run([str(python),'-m','pip','install','--no-index','--find-links',str(bundle/'wheels'),'-r',str(bundle/'requirements.txt')],check=True)
            subprocess.run([str(python),str(target/'app/runtime/local/farmy.py'),'--version'],check=True)
        except BaseException:
            shutil.rmtree(target,ignore_errors=True);raise
    current=prefix/'current';temporary=prefix/('.current-'+str(os.getpid()))
    temporary.symlink_to(target);os.replace(temporary,current)
    binaries=prefix/'bin';binaries.mkdir(exist_ok=True)
    launcher=binaries/'farmy'
    launcher.write_text('#!/bin/sh\nexport FARMY_LAUNCHER='+shlex.quote(str(launcher))+'\nexec '+shlex.quote(str(current/'venv/bin/python'))+' '+shlex.quote(str(current/'app/runtime/local/farmy.py'))+' "$@"\n')
    launcher.chmod(0o755)
    print('Installed:',launcher)
    print('Workspace data is separate and unchanged. Add this bin directory to PATH if desired.')
    if lock:lock.close()


if __name__=='__main__':main()
