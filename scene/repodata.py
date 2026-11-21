"""Compact per-repository data for browser-side art (sculptures, 2D drawings).

Works on a blobless clone: only trees, commits and HEAD blobs are needed.
"""

import json
import os
import re
import subprocess
import time
from collections import defaultdict
from pathlib import PurePosixPath

from .history import FIELD_SEP, RECORD_SEP, is_tracked_path

FORMAT_VERSION = 1
MAX_FILES = 2000
MAX_TIMELINE = 300


def _git(repo_path, *args):
    return subprocess.run(['git', '-c', 'core.quotePath=false', *args], cwd=repo_path,
                          capture_output=True, text=True, errors='replace', check=True).stdout


def _head_files(repo_path):
    files = {}
    for entry in _git(repo_path, 'ls-tree', '-r', '-l', '-z', 'HEAD').split('\0'):
        if not entry:
            continue
        meta, path = entry.split('\t', 1)
        _, kind, _, size = meta.split()
        if kind == 'blob' and size != '-' and is_tracked_path(path):
            files[path] = int(size)
    return files


def _history(repo_path):
    log = _git(repo_path, 'log', '--first-parent', '--reverse', '--no-renames', '--name-status',
               f'--format={RECORD_SEP}%at{FIELD_SEP}%an')
    born, touches = {}, defaultdict(int)
    timeline, authors = [], set()
    for index, record in enumerate(log.split(RECORD_SEP)[1:]):
        lines = record.split('\n')
        timestamp, author = lines[0].split(FIELD_SEP, 1)
        authors.add(author)
        changed = 0
        for line in lines[1:]:
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            status, path = parts[0], parts[-1]
            changed += 1
            if status.startswith('D'):
                born.pop(path, None)
                continue
            born.setdefault(path, index)
            touches[path] += 1
        timeline.append((int(timestamp), changed))
    return born, touches, timeline, authors


def _downsample(timeline, buckets):
    if len(timeline) <= buckets:
        return [[t, c] for t, c in timeline]
    result = []
    for b in range(buckets):
        chunk = timeline[b * len(timeline) // buckets:(b + 1) * len(timeline) // buckets]
        result.append([chunk[-1][0], sum(c for _, c in chunk)])
    return result


def build_repo_data(repo_path, repo_url, repo_name):
    files = _head_files(repo_path)
    born, touches, timeline, authors = _history(repo_path)
    commit_count = len(timeline)

    kept = sorted(files, key=lambda p: -files[p])[:MAX_FILES]
    languages = defaultdict(int)
    for path, size in files.items():
        languages[PurePosixPath(path).suffix.lower() or 'none'] += size

    return {
        'version': FORMAT_VERSION,
        'repo_url': repo_url,
        'name': repo_name,
        'head': _git(repo_path, 'rev-parse', 'HEAD').strip(),
        'generated_at': int(time.time()),
        'commits': commit_count,
        'authors': len(authors),
        'first_commit': timeline[0][0] if timeline else None,
        'last_commit': timeline[-1][0] if timeline else None,
        'total_files': len(files),
        'total_bytes': sum(files.values()),
        'languages': dict(sorted(languages.items(), key=lambda kv: -kv[1])[:12]),
        'timeline': _downsample(timeline, MAX_TIMELINE),
        'files': [[p, files[p], born.get(p, 0), touches.get(p, 0)] for p in sorted(kept)],
    }


def repo_data_slug(repo_url):
    parts = repo_url.rstrip('/').removesuffix('.git').replace(':', '/').split('/')[-2:]
    return re.sub(r'[^A-Za-z0-9_.-]', '_', '__'.join(parts))


def repo_data_path(data_dir, repo_url):
    return os.path.join(data_dir, f'{repo_data_slug(repo_url)}.json')


def write_repo_data(data_dir, data):
    os.makedirs(data_dir, exist_ok=True)
    path = repo_data_path(data_dir, data['repo_url'])
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, separators=(',', ':'))
    return path
