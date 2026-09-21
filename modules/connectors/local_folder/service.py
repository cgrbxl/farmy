"""Versioned local snapshots behind a mutually authenticated loopback API."""
import argparse
import json
import os
from pathlib import Path
import stat

from farmy_transport.http import Fault, MAX_BYTES, serve
from farmy_transport.snapshots import SnapshotConnector


def safe_read(root_fd, relative):
    parts = relative.split('/')
    if relative.startswith('/') or '\\' in relative or any(p in ('', '.', '..') for p in parts):
        raise Fault('denied')
    directory = os.dup(root_fd)
    file_fd = None
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise Fault('denied')
        def read_all():
            chunks = []
            size = 0
            while True:
                block = os.read(file_fd, min(65536, MAX_BYTES + 1 - size))
                if not block:
                    break
                chunks.append(block)
                size += len(block)
                if size > MAX_BYTES:
                    raise Fault('conflict')
            return b''.join(chunks)
        first = read_all()
        middle = os.fstat(file_fd)
        os.lseek(file_fd, 0, os.SEEK_SET)
        second = read_all()
        after = os.fstat(file_fd)
        def signature(s):
            return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns
        if signature(before) != signature(middle) or signature(before) != signature(after) or first != second:
            raise Fault('conflict')
        return first
    except OSError as exc:
        raise Fault('denied') from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(directory)


class Connector(SnapshotConnector):
    def __init__(self, config):
        super().__init__(config)
        self.root_fd = os.open(config['sourceRoot'], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)

    def read_source(self, path):
        return safe_read(self.root_fd, path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    serve(Connector(json.loads(Path(args.config).read_text())))
