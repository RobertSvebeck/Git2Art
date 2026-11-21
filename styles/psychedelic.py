"""Psychedelic: a 1960s-poster / op-art field computed per pixel.

Every folder is the centre of a logarithmic spiral (strength from its size,
twist direction from its path); the spirals interfere, are domain-warped and
cut into neon bands with dark outlines. The largest folders bloom into
mandalas whose petal counts come from their contents; the most-edited files
glow as small concentric eyes. Positions come from the path-stable layout.
"""

import colorsys
import math

import numpy as np
from PIL import Image

from scene.layout import dir_position, file_position, parent_dir
from .common import language_rgb, unit_hash

BANDS = 7.0
COLOURS = 6  # spiral arms are multiples of this, so the angle seam is invisible


def palette_phases(data):
    hues = []
    for ext in list(data.get('languages', {}))[:3]:
        r, g, b = (c / 255 for c in language_rgb(f'x{ext}'))
        hues.append(colorsys.rgb_to_hsv(r, g, b)[0])
    while len(hues) < 3:
        hues.append((hues[-1] + 0.33) % 1.0 if hues else 0.8)
    return np.array(hues, dtype=np.float32)


def render(data, width=1600, height=1600):
    files = sorted(data.get('files', []), key=lambda f: -f[1])[:800]
    ys, xs = np.mgrid[0:height, 0:width].astype(np.float32)
    aspect = width / height
    u = (xs / width - 0.5) * aspect
    v = ys / height - 0.5

    folders = {}
    for f in files:
        d = parent_dir(f[0])
        entry = folders.setdefault(d, [0, 0])
        entry[0] += f[1]
        entry[1] += 1
    if not folders:
        folders[''] = [1, 1]
    stretch = aspect ** 0.5
    raw = {d: dir_position(d) for d in folders}
    px = [p[0] * stretch for p in raw.values()]
    py = [p[1] for p in raw.values()]
    cx, cy = (min(px) + max(px)) / 2, (min(py) + max(py)) / 2
    span = max(max(px) - min(px), max(py) - min(py), 0.4)
    scale = 0.8 / span

    def to_uv(x, y):
        return (x * stretch - cx) * scale, (y - cy) * scale

    total = sum(w for w, _ in folders.values()) or 1
    ranked = sorted(folders.items(), key=lambda kv: -kv[1][0])[:14]
    t = np.zeros_like(u)
    warp_u = u + 0.035 * np.sin(v * 11 + unit_hash(data.get('name', ''), 'w1') * 6)
    warp_v = v + 0.035 * np.sin(u * 9 + unit_hash(data.get('name', ''), 'w2') * 6)
    for rank, (d, (weight, count)) in enumerate(ranked):
        fx, fy = to_uv(*raw[d])
        dx, dy = warp_u - fx, warp_v - fy
        dist = np.sqrt(dx * dx + dy * dy) + 0.02
        angle = np.arctan2(dy, dx)
        strength = math.sqrt(weight / total)
        twist = 1 if unit_hash(d, 'twist') < 0.5 else -1
        arms = COLOURS * (2 if strength > 0.45 else 1)
        t += strength * np.log(dist) * 2.2 * BANDS + twist * arms * angle / (2 * math.pi)
        if rank < 3:
            petals = int(min(16, max(5, count)))
            reach = 0.12 + 0.25 * strength
            bloom = np.exp(-(dist / reach) ** 2)
            t += bloom * 0.35 * BANDS * np.cos(petals * angle + np.log(dist) * 6)

    band = t - np.floor(t)
    level = np.mod(np.floor(t), COLOURS) / COLOURS
    phases = palette_phases(data)
    colour = 0.5 + 0.5 * np.cos(2 * math.pi * (level[..., None] + phases[None, None, :]))
    colour = np.clip(colour * 1.15 + 0.05, 0, 1)
    edge = np.minimum(band, 1 - band)
    outline = np.clip(edge / 0.06, 0, 1) ** 0.6
    colour *= (0.12 + 0.88 * outline)[..., None]
    shading = 0.82 + 0.18 * np.cos(band * 2 * math.pi)
    colour *= shading[..., None]

    touches = sorted((f[3] for f in files), reverse=True)
    hot = touches[max(0, len(touches) // 15)] if touches else 0
    for f in files:
        if f[3] < max(hot, 2):
            continue
        fx, fy = to_uv(*file_position(f[0]))
        dist = np.sqrt((u - fx) ** 2 + (v - fy) ** 2)
        radius = 0.025
        mask = dist < radius
        if not mask.any():
            continue
        rings = 0.5 + 0.5 * np.cos(dist[mask] / radius * 18)
        glow = np.array(language_rgb(f[0]), dtype=np.float32) / 255
        colour[mask] = colour[mask] * 0.25 + (rings[:, None] * glow[None, :] * 0.95 + 0.05)

    image = Image.fromarray((np.clip(colour, 0, 1) * 255).astype(np.uint8), 'RGB')
    return image
