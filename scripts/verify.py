"""Run the local synthetic development checks using this Python environment."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
steps = [
    ['-m', 'unittest', 'discover', '-s', 'conformance/foundation', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc001', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc002', '-v'],
    ['-m', 'unittest', 'discover', '-s', 'conformance/uc003', '-v'],
    ['conformance/foundation/check.py'],
    ['scripts/check_docs.py'],
    ['solutions/core/uc001/run.py', 'demo'],
    ['solutions/document-path/uc002/run.py', 'demo'],
    ['solutions/sensor-path/uc003/run.py', 'demo'],
]
for step in steps:
    subprocess.run([sys.executable, *step], cwd=ROOT, check=True)
print('All local synthetic checks and all three demos passed.')
