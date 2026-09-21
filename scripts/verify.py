"""Run the local synthetic development checks using this Python environment."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--with-local-model', action='store_true', help='Also run UC-004 against installed qwen2.5:3b through local Ollama')
parser.add_argument('--with-s3-fixture', action='store_true', help='Also run pending UC-007 checks against a local S3 HTTP double; requires optional S3 dependencies')
args = parser.parse_args()
steps = [
    ['-m', 'unittest', 'discover', '-s', 'conformance/foundation', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc001', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc002', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc003', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc004', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc005', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc006', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc008', '-v'],
    ['conformance/foundation/check.py'],
    ['scripts/check_docs.py'],
    ['solutions/core/uc001/run.py', 'demo'],
    ['solutions/document-path/uc002/run.py', 'demo'],
    ['solutions/sensor-path/uc003/run.py', 'demo'],
    ['solutions/operations/uc005/run.py', 'demo'],
    ['solutions/disclosure/uc006/run.py', 'demo'],
    ['solutions/replacement/uc008/run.py', 'demo'],
]
if args.with_local_model:
    steps.append(['solutions/assisted-answer/uc004/run.py', 'demo'])
if args.with_s3_fixture:
    steps.extend([['-m', 'unittest', 'discover', '-s', 'conformance/uc007', '-v'],
                  ['solutions/s3-source/uc007/run.py', 'demo', '--fixture']])
for step in steps:
    subprocess.run([sys.executable, *step], cwd=ROOT, check=True)
print(f'All selected checks and {6 + int(args.with_local_model) + int(args.with_s3_fixture)} demos passed.'
      + (' UC-007 used a local HTTP double; real-provider validation remains separate.' if args.with_s3_fixture else ''))
