"""Turn positioned files into a renderable Scene (stars plus directory branches)."""

import math
from collections import defaultdict

from .layout import ancestor_dirs, dir_position, parent_dir, unit_hash
from .render import Branch, Scene, Star

FILAMENT_WEIGHT = 0.12
TRUNK_WEIGHT = 0.42


def layout_stretch(width, height):
    """Widen the layout for landscape canvases (and narrow it for portrait)."""
    return (width / height) ** 0.5


def _mix(total, colour, weight):
    total[0] += colour[0] * weight
    total[1] += colour[1] * weight
    total[2] += colour[2] * weight
    total[3] += weight


def _average(total, darken=1.0):
    if total[3] <= 0:
        return (120, 130, 160)
    return tuple(int(total[i] / total[3] * darken) for i in range(3))


def build_scene(stars, stretch, caption=None):
    """Stars already carry unit-space positions; add branches and a tint."""
    subtree = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    filaments = []
    overall = [0.0, 0.0, 0.0, 0.0]
    for star, path in stars:
        weight = star.radius ** 2 * star.alpha
        _mix(overall, star.colour, weight + 1e-9)
        for directory in ancestor_dirs(path):
            _mix(subtree[directory], star.colour, weight)
        dx, dy = dir_position(parent_dir(path))
        filaments.append(Branch(
            dx * stretch, dy, star.x, star.y, FILAMENT_WEIGHT * star.radius,
            star.colour, (unit_hash(path, 'bend') - 0.5) * 0.5, star.alpha * 0.8,
        ))

    trunks = []
    for directory, total in subtree.items():
        if directory == '' or total[3] <= 0:
            continue
        x1, y1 = dir_position(directory)
        x0, y0 = dir_position(parent_dir(directory))
        trunks.append(Branch(
            x0 * stretch, y0, x1 * stretch, y1, TRUNK_WEIGHT * math.sqrt(total[3]) * 0.35,
            _average(total, 0.85), (unit_hash(directory, 'bend') - 0.5) * 0.6,
            min(1.0, 0.5 + 4 * math.sqrt(total[3])),
        ))

    return Scene(
        stars=[star for star, _ in stars],
        branches=trunks + filaments,
        tint=_average(overall),
        caption=caption or [],
    )
