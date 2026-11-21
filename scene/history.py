"""Read a repository's first-parent history as per-commit file changes."""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import PurePosixPath

RECORD_SEP = '\x1e'
FIELD_SEP = '\x1f'
LOG_FORMAT = f'{RECORD_SEP}%H{FIELD_SEP}%at{FIELD_SEP}%an{FIELD_SEP}%s'

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.bmp', '.pdf',
    '.zip', '.tar', '.gz', '.bin', '.exe', '.dll', '.so', '.dylib', '.woff',
    '.woff2', '.ttf', '.otf', '.eot', '.mp3', '.mp4', '.mov', '.lock', '.map',
}
SKIP_NAMES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock',
              'Cargo.lock', 'composer.lock', 'Gemfile.lock', '.DS_Store'}
SKIP_DIRS = {'node_modules', 'vendor', 'dist', 'build', '.venv', 'venv', '__pycache__'}

BRACE_RENAME = re.compile(r'^(.*)\{(.*) => (.*)\}(.*)$')


@dataclass
class FileChange:
    path: str
    added: int
    deleted: int
    old_path: str = None


@dataclass
class Commit:
    sha: str
    timestamp: int
    author: str
    subject: str
    changes: list = field(default_factory=list)
    deleted_paths: list = field(default_factory=list)


def is_tracked_path(path):
    p = PurePosixPath(path)
    if p.name in SKIP_NAMES or p.suffix.lower() in SKIP_EXTENSIONS:
        return False
    if p.name.endswith('.min.js') or p.name.endswith('.min.css'):
        return False
    return not any(part in SKIP_DIRS for part in p.parts[:-1])


def _join_parts(*parts):
    return re.sub(r'/+', '/', ''.join(parts)).strip('/')


def parse_rename(path_field):
    """Return (old_path, new_path); old_path is None when not a rename."""
    match = BRACE_RENAME.match(path_field)
    if match:
        prefix, old, new, suffix = match.groups()
        return _join_parts(prefix, old, suffix), _join_parts(prefix, new, suffix)
    if ' => ' in path_field:
        old, new = path_field.split(' => ', 1)
        return old, new
    return None, path_field


def _parse_record(record):
    lines = record.split('\n')
    sha, timestamp, author, subject = lines[0].split(FIELD_SEP, 3)
    commit = Commit(sha=sha, timestamp=int(timestamp), author=author, subject=subject)
    for line in lines[1:]:
        if line.startswith(' delete mode '):
            path = line.split(' ', 4)[4]
            if is_tracked_path(path):
                commit.deleted_paths.append(path)
            continue
        parts = line.split('\t', 2)
        if len(parts) != 3 or parts[0] == '-':
            continue
        old_path, new_path = parse_rename(parts[2])
        if not is_tracked_path(new_path):
            continue
        commit.changes.append(FileChange(new_path, int(parts[0]), int(parts[1]), old_path))
    return commit


def read_history(repo_path):
    """Return the first-parent history, oldest commit first."""
    result = subprocess.run(
        ['git', '-c', 'core.quotePath=false', 'log', '--first-parent', '--reverse',
         '-M', '--numstat', '--summary', f'--format={LOG_FORMAT}'],
        cwd=repo_path, capture_output=True, text=True, errors='replace', check=True,
    )
    records = result.stdout.split(RECORD_SEP)[1:]
    return [_parse_record(record) for record in records]
