"""Small flock-compatible exclusive locks for Windows and POSIX."""
import errno
import os
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
