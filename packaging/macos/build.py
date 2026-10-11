"""Build an installable local release plus a Homebrew formula; no publication."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[2]
VERSION='0.3.0'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--wheels',type=Path,help='Reuse previously downloaded pinned wheels offline')
    args=parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64' or sys.version_info[:2] != (3,14):
        parser.error('This release builder currently supports macOS arm64 / Python 3.14 only.')
    out=args.output.absolute();out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='farmy-release-') as temporary:
        bundle=Path(temporary)/'farmy';app=bundle/'app';app.mkdir(parents=True)
        for name in ('modules','sdk','contracts','solutions','runtime/local','dashboard/workbench'):
            shutil.copytree(ROOT/name,app/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copy2(ROOT/'LICENSE',bundle/'LICENSE')
        shutil.copy2(ROOT/'packaging/macos/install.py',bundle/'install.py')
        shutil.copy2(ROOT/'conformance/foundation/requirements.txt',bundle/'requirements.txt')
        wheels=bundle/'wheels'
        if args.wheels:shutil.copytree(args.wheels,wheels)
        else:
            wheels.mkdir()
            subprocess.run([sys.executable,'-m','pip','download','--only-binary=:all:','--dest',str(wheels),'-r',str(bundle/'requirements.txt')],check=True)
        files={str(p.relative_to(bundle)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.rglob('*')) if p.is_file()}
        build=VERSION+'-'+hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()[:12]
        revision=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        manifest=dict(sourceRevision=revision,stateSchema=1,version=VERSION,build=build,system=platform.system(),machine=platform.machine(),python=list(sys.version_info[:2]),files=files)
        (bundle/'release.json').write_text(json.dumps(manifest,indent=2)+'\n')
        archive=out/f'farmy-{build}-{platform.system().lower()}-{platform.machine()}.tar.gz'
        with tarfile.open(archive,'w:gz') as tar:tar.add(bundle,arcname='farmy')
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        (out/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n')
        formula='''class Farmy < Formula
  desc "Local modular information workspace"
  homepage "https://github.com/cgrbxl/farmy"
  url %s
  version "%s"
  sha256 "%s"
  license "Apache-2.0"
  depends_on :macos
  depends_on arch: :arm64
  depends_on "python@3.14"
  depends_on "openssl@3"

  def install
    libexec.install "app", "wheels", "requirements.txt", "release.json"
    system Formula["python@3.14"].opt_bin/"python3.14", "-m", "venv", libexec/"venv"
    system libexec/"venv/bin/python", "-m", "pip", "install", "--no-index", "--find-links", libexec/"wheels", "-r", libexec/"requirements.txt"
    (bin/"farmy").write <<~SH
      #!/bin/sh
      export FARMY_LAUNCHER="#{opt_bin}/farmy"
      export PATH="#{Formula["openssl@3"].opt_bin}:$PATH"
      exec "#{libexec}/venv/bin/python" "#{libexec}/app/runtime/local/farmy.py" "$@"
    SH
  end

  service do
    run [opt_bin/"farmy", "serve"]
    keep_alive false
    working_dir Dir.home
    log_path var/"log/farmy.log"
    error_log_path var/"log/farmy.log"
  end

  test do
    assert_match "%s", shell_output("#{bin}/farmy --version")
  end
end
''' % (json.dumps(archive.as_uri()),VERSION,digest,VERSION)
        (out/'farmy.rb').write_text(formula)
        print('Release:',archive)
        print('SHA-256:',digest)
        print('Local formula:',out/'farmy.rb')


if __name__=='__main__':main()
