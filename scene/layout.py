"""Path-stable layout and language colours for the scene model.

Every position is a pure function of a path, so adding, editing or deleting
one file never moves any other file.
"""

import colorsys
import hashlib
import math
from functools import lru_cache
from pathlib import PurePosixPath

LANGUAGE_COLOURS = {
    '.py': '#4f8fe0', '.pyx': '#4f8fe0', '.ipynb': '#f08a4b',
    '.js': '#f2d64b', '.mjs': '#f2d64b', '.cjs': '#f2d64b', '.jsx': '#f2d64b',
    '.ts': '#5aa2ff', '.tsx': '#5aa2ff',
    '.html': '#f06a3c', '.htm': '#f06a3c', '.css': '#a77bf3', '.scss': '#e06aa8',
    '.sass': '#e06aa8', '.less': '#8f7ff0', '.vue': '#4fd39a', '.svelte': '#ff6a3d',
    '.java': '#e3a24a', '.kt': '#b18cff', '.kts': '#b18cff', '.scala': '#e5505f',
    '.go': '#3fd0e8', '.rs': '#f0b58a', '.c': '#9fb4c8', '.h': '#9fb4c8',
    '.cpp': '#f26a96', '.cc': '#f26a96', '.hpp': '#f26a96', '.cs': '#4cc26a',
    '.swift': '#ff7a52', '.m': '#6fa8ff', '.dart': '#3fd3c4', '.rb': '#e8475a',
    '.php': '#8e9cf0', '.lua': '#6a7cf5', '.r': '#4aa8f5', '.jl': '#b77be0',
    '.ex': '#9b6fd0', '.exs': '#9b6fd0', '.erl': '#d04f8a', '.hs': '#9a86d8',
    '.sh': '#9be36a', '.bash': '#9be36a', '.zsh': '#9be36a', '.ps1': '#5f9ff0',
    '.sql': '#f0a23a', '.json': '#e8c27a', '.yml': '#e9746a', '.yaml': '#e9746a',
    '.toml': '#d9a27a', '.xml': '#7ac0a8', '.ini': '#b8a890', '.cfg': '#b8a890',
    '.md': '#bfb398', '.rst': '#bfb398', '.txt': '#a39d8c',
}
NEUTRAL_SATURATION = 0.35

ROOT_FILE_SPREAD = 0.30
DIR_DISTANCE = 0.58
DEPTH_DECAY = 0.58
FILE_SPREAD_DECAY = 0.66
COVERAGE = 0.20
MAX_RADIUS = 0.17


def unit_hash(text, salt=''):
    digest = hashlib.md5(f'{salt}:{text}'.encode()).digest()
    return int.from_bytes(digest[:8], 'big') / 2 ** 64


def _hex_to_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


@lru_cache(maxsize=None)
def extension_colour(extension):
    if extension in LANGUAGE_COLOURS:
        return _hex_to_rgb(LANGUAGE_COLOURS[extension])
    r, g, b = colorsys.hsv_to_rgb(unit_hash(extension, 'hue'), NEUTRAL_SATURATION, 0.85)
    return int(r * 255), int(g * 255), int(b * 255)


@lru_cache(maxsize=None)
def file_colour(path):
    base = extension_colour(PurePosixPath(path).suffix.lower())
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in base))
    l = min(0.92, max(0.35, l + (unit_hash(path, 'light') - 0.5) * 0.16))
    h = (h + (unit_hash(path, 'hue') - 0.5) * 0.03) % 1.0
    return tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, l, s))


def parent_dir(path):
    parent = str(PurePosixPath(path).parent)
    return '' if parent == '.' else parent


def depth_of(dir_path):
    return 0 if dir_path == '' else dir_path.count('/') + 1


@lru_cache(maxsize=None)
def dir_position(dir_path):
    if dir_path == '':
        return 0.0, 0.0
    px, py = dir_position(parent_dir(dir_path))
    depth = depth_of(dir_path)
    angle = 2 * math.pi * unit_hash(dir_path, 'angle')
    distance = DIR_DISTANCE * DEPTH_DECAY ** (depth - 1) * (0.7 + 0.3 * unit_hash(dir_path, 'dist'))
    return px + distance * math.cos(angle), py + distance * math.sin(angle)


@lru_cache(maxsize=None)
def file_position(path):
    directory = parent_dir(path)
    cx, cy = dir_position(directory)
    spread = ROOT_FILE_SPREAD * FILE_SPREAD_DECAY ** depth_of(directory)
    distance = spread * (0.25 + 0.75 * math.sqrt(unit_hash(path, 'radius')))
    angle = 2 * math.pi * unit_hash(path, 'angle')
    return cx + distance * math.cos(angle), cy + distance * math.sin(angle)


def size_scale(total_lines):
    """Factor k so that radius = k * sqrt(lines) covers a fixed share of the canvas."""
    return math.sqrt(COVERAGE / max(total_lines, 1))


def file_radius(lines, scale):
    return min(MAX_RADIUS, scale * math.sqrt(max(lines, 0)))


def ancestor_dirs(path):
    directory = parent_dir(path)
    while True:
        yield directory
        if directory == '':
            return
        directory = parent_dir(directory)
