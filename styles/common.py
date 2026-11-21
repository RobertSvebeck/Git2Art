"""Shared helpers for styles rendered from repository data (see scene/repodata.py)."""

import hashlib
import math
from pathlib import PurePosixPath

LANGUAGE_HEX = {
    '.py': '#4f8fe0', '.ipynb': '#f08a4b', '.js': '#f2d64b', '.mjs': '#f2d64b', '.jsx': '#f2d64b',
    '.ts': '#5aa2ff', '.tsx': '#5aa2ff', '.html': '#f06a3c', '.css': '#a77bf3', '.scss': '#e06aa8',
    '.vue': '#4fd39a', '.svelte': '#ff6a3d', '.java': '#e3a24a', '.kt': '#b18cff', '.scala': '#e5505f',
    '.go': '#3fd0e8', '.rs': '#f0b58a', '.c': '#9fb4c8', '.h': '#9fb4c8', '.cpp': '#f26a96', '.cc': '#f26a96',
    '.hpp': '#f26a96', '.cs': '#4cc26a', '.swift': '#ff7a52', '.m': '#6fa8ff', '.dart': '#3fd3c4',
    '.rb': '#e8475a', '.php': '#8e9cf0', '.lua': '#6a7cf5', '.r': '#4aa8f5', '.sh': '#9be36a',
    '.sql': '#f0a23a', '.json': '#e8c27a', '.yml': '#e9746a', '.yaml': '#e9746a', '.toml': '#d9a27a',
    '.xml': '#7ac0a8', '.md': '#d8ccb0', '.rst': '#d8ccb0', '.txt': '#bdb6a4', '.csv': '#8fd18a',
}
DOC_EXTENSIONS = {'.md', '.rst', '.txt', '.adoc'}


def unit_hash(text, salt=''):
    digest = hashlib.md5(f'{salt}:{text}'.encode()).digest()
    return int.from_bytes(digest[:8], 'big') / 2 ** 64


def hex_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def extension(path):
    return PurePosixPath(path).suffix.lower()


def language_rgb(path):
    ext = extension(path)
    if ext in LANGUAGE_HEX:
        return hex_rgb(LANGUAGE_HEX[ext])
    h = unit_hash(ext or 'none', 'hue')
    return hsv_rgb(h, 0.3, 0.8)


def hsv_rgb(h, s, v):
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
    return int(r * 255), int(g * 255), int(b * 255)


def shade(rgb, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)


def nearest(rgb, palette):
    return min(palette, key=lambda p: (p[0] - rgb[0]) ** 2 * 0.3 + (p[1] - rgb[1]) ** 2 * 0.59 + (p[2] - rgb[2]) ** 2 * 0.11)


def days_idle(data):
    if not data.get('last_commit'):
        return 10_000
    return max(0.0, (data['generated_at'] - data['last_commit']) / 86400)


def districts(files, minimum=3, maximum=12):
    """Group file paths into districts by folder, going deeper while one folder dominates."""
    def key(path, depth):
        parts = path.split('/')[:-1]
        return '/'.join(parts[:depth]) if parts else ''

    depth = 1
    groups = {}
    while True:
        groups = {}
        for f in files:
            groups.setdefault(key(f[0], depth), []).append(f)
        largest = max(groups.values(), key=len)
        deeper = {key(f[0], depth + 1) for f in largest}
        if len(groups) >= minimum or len(deeper) <= 1 or depth >= 4:
            break
        depth += 1
    ordered = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    if len(ordered) > maximum:
        head, tail = ordered[:maximum - 1], ordered[maximum - 1:]
        ordered = head + [('(other)', [f for _, fs in tail for f in fs])]
    return ordered


def treemap(rect, weights, keys):
    """Binary slice treemap on an integer grid. rect = (x, y, w, h). Returns {key: rect}."""
    result = {}

    def split(rect, items):
        x, y, w, h = rect
        if not items:
            return
        if len(items) == 1 or w * h <= 1:
            result[items[0][0]] = rect
            return
        total = sum(weight for _, weight in items)
        running, cut = 0, 1
        for i, (_, weight) in enumerate(items[:-1]):
            running += weight
            cut = i + 1
            if running >= total / 2:
                break
        share = sum(weight for _, weight in items[:cut]) / total
        if w >= h:
            first = max(1, min(w - 1, round(w * share)))
            split((x, y, first, h), items[:cut])
            split((x + first, y, w - first, h), items[cut:])
        else:
            first = max(1, min(h - 1, round(h * share)))
            split((x, y, w, first), items[:cut])
            split((x, y + first, w, h - first), items[cut:])

    split(rect, sorted(zip(keys, weights), key=lambda kv: unit_hash(kv[0], 'order')))
    return result


def bayer4():
    return [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def clamp(value, low, high):
    return max(low, min(high, value))


def sqrt_scale(value, largest):
    return math.sqrt(value / largest) if largest > 0 else 0.0
