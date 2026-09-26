"""Stop an owned module if its supervisor exits, including an abrupt exit."""
import fcntl
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time

stopping = False

def stop(*_):
    global stopping
    stopping = True

for number in (signal.SIGTERM, signal.SIGINT): signal.signal(number, stop)
os.umask(0o077)
with Path(sys.argv[1]).open('a') as lock:
    deadline = time.monotonic() + 8
    while True:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if stopping or time.monotonic() >= deadline: sys.exit(1)
            time.sleep(.05)
    child = subprocess.Popen(sys.argv[2:], stdin=subprocess.DEVNULL)
    try:
        while not stopping and child.poll() is None:
            readable, _, _ = select.select([sys.stdin.buffer], [], [], .2)
            if readable and not os.read(sys.stdin.fileno(), 1): break
    finally:
        if child.poll() is None:
            child.terminate()
            try: child.wait(timeout=4)
            except subprocess.TimeoutExpired: child.kill();child.wait()
    sys.exit(child.returncode or 0)
