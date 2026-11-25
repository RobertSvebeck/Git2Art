"""Locks shared by all worker processes; the system frees them if a worker dies."""

import fcntl
import os
from contextlib import ExitStack, contextmanager


@contextmanager
def file_lock(path, wait=True):
    """Yield True while holding the lock, or False if it is taken and wait is False."""
    with open(path, 'a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX if wait else fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


@contextmanager
def lock_slot(directory, name, slots):
    """Yield True while holding one of a few slots, or False if all are taken."""
    with ExitStack() as stack:
        yield any(stack.enter_context(file_lock(os.path.join(directory, f'{name}-{slot}.lock'), wait=False))
                  for slot in range(slots))
