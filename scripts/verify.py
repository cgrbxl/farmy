"""Run the local synthetic development checks using this Python environment."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--with-local-model', action='store_true', help='Also run UC-004 against installed qwen2.5:3b through local Ollama')
args = parser.parse_args()
steps = [
    ['-m', 'unittest', 'discover', '-s', 'conformance/foundation', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc001', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc002', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc003', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc004', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc005', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc006', '-v'],
    ['conformance/foundation/check.py'],
    ['scripts/check_docs.py'],
    ['solutions/core/uc001/run.py', 'demo'],
    ['solutions/document-path/uc002/run.py', 'demo'],
    ['solutions/sensor-path/uc003/run.py', 'demo'],
    ['solutions/operations/uc005/run.py', 'demo'],
    ['solutions/disclosure/uc006/run.py', 'demo'],
]
if args.with_local_model:
    steps.append(['solutions/assisted-answer/uc004/run.py', 'demo'])
for step in steps:
    subprocess.run([sys.executable, *step], cwd=ROOT, check=True)
print('All local synthetic checks and ' + ('six' if args.with_local_model else 'five (UC-004 real-model demo not requested)') + ' demos passed.')
