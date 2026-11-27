"""Small flock-compatible exclusive locks for Windows and POSIX."""
from contextlib import contextmanager
import errno
import os
import stat
import time

LOCK_EX, LOCK_NB, LOCK_UN = 2, 4, 8


def flock(stream, operation):
    if os.name != 'nt':
        import fcntl
        return fcntl.flock(stream, operation)
    import msvcrt
    if operation not in (LOCK_EX, LOCK_EX | LOCK_NB, LOCK_UN):
        raise ValueError('unsupported lock operation')
    fd = stream if isinstance(stream, int) else stream.fileno()
    position = os.lseek(fd, 0, os.SEEK_CUR)
    try:
        while True:
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_UNLCK if operation == LOCK_UN else msvcrt.LK_NBLCK, 1)
                return
            except OSError as exc:
                if operation == LOCK_UN or exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if operation & LOCK_NB:
                    raise BlockingIOError(errno.EAGAIN, 'lock already held') from exc
                time.sleep(.05)
    finally:
        os.lseek(fd, position, os.SEEK_SET)

@contextmanager
def try_owner_lock(path):
    from .project_docs import guard_write_path
    path = guard_write_path(path)
    if path.is_symlink():
        raise ValueError('owner lock must not be redirected')
    flags = os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags, 0o600)
    try:
        opened, named = os.fstat(fd), path.lstat()
        if (not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
                or getattr(named, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)):
            raise ValueError('owner lock must be a stable regular file')
        try:
            flock(fd, LOCK_EX | LOCK_NB)
        except BlockingIOError:
            yield False
        else:
            yield True
    finally:
        os.close(fd)
