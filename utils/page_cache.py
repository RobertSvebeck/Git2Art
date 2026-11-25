"""Text cached on disk, shared by all worker processes.

LiteSpeed starts and stops a process per concurrent request, so a cache in
process memory is usually cold. One worker rebuilds an expired entry while
the others keep serving the old copy.
"""

import os
import tempfile
import time

from utils.file_lock import file_lock


def _age(path):
    try:
        return time.time() - os.path.getmtime(path)
    except OSError:
        return None


def _read(path):
    with open(path, encoding='utf-8') as handle:
        return handle.read()


def _write(path, text):
    handle, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix='.tmp')
    with os.fdopen(handle, 'w', encoding='utf-8') as out:
        out.write(text)
    os.replace(tmp, path)


def cached_text(path, max_age, build):
    """Text from path, rebuilt with build() when older than max_age seconds.

    build() may return None or raise: nothing is cached then, and the old copy
    is served if there is one.
    """
    age = _age(path)
    if age is not None and age < max_age:
        return _read(path)
    has_old_copy = age is not None
    with file_lock(f'{path}.lock', wait=not has_old_copy) as held:
        if not held:
            return _read(path)
        age = _age(path)
        if age is not None and age < max_age:
            return _read(path)
        try:
            text = build()
        except Exception as e:
            if not has_old_copy:
                raise
            print(f'Warning: could not rebuild {os.path.basename(path)}: {e}')
            text = None
        if text is not None:
            _write(path, text)
            return text
    return _read(path) if has_old_copy else None
