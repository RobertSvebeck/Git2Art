"""Watercolour: layered transparent glazes on cold-press paper.

Folders are broad pale washes, files are smaller saturated glazes, placed by
the path-stable layout (scene/layout.py) and tied together by a light ink
sketch of the folder tree. Each glaze is ~20 nearly transparent layers of a
deformed polygon; the layers accumulate at the edges like pooled pigment.
Colours combine multiplicatively, as pigments absorb light.
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from scene.layout import dir_position, file_position, parent_dir
from .common import districts, language_rgb, unit_hash

LAYERS = 18
MAX_GLAZES = 140
PAPER = np.array([246, 241, 230], dtype=np.float32)


class Rng:
    def __init__(self, key):
        self.rng = np.random.default_rng(int(unit_hash(key, 'wc') * 2 ** 32))

    def gauss(self, sigma):
        return float(self.rng.normal(0, sigma))

    def uniform(self, a, b):
        return float(self.rng.uniform(a, b))


def deform(points, rounds, variance, rng):
    for _ in range(rounds):
        new = []
        for i, (x0, y0, v0) in enumerate(points):
            x1, y1, v1 = points[(i + 1) % len(points)]
            length = math.hypot(x1 - x0, y1 - y0)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            spread = length * v0 * variance
            new.append((x0, y0, v0))
            new.append((mx + rng.gauss(spread), my + rng.gauss(spread), (v0 + v1) / 2 * rng.uniform(0.75, 1.25)))
        points = new
    return points


def base_shape(radius, rng, sides=10):
    return [(math.cos(a) * radius * rng.uniform(0.85, 1.15), math.sin(a) * radius * rng.uniform(0.85, 1.15),
             rng.uniform(0.4, 1.4)) for a in np.linspace(0, 2 * math.pi, sides, endpoint=False)]


def watercolour_tone(rgb, wash):
    """Watercolour pigments: lighter and a touch desaturated; wash = 0 pale .. 1 rich."""
    grey = sum(rgb) / 3
    return tuple(c * (0.75 + 0.25 * wash) + grey * (0.25 - 0.25 * wash) for c in rgb)


class Painting:
    def __init__(self, data, width, height):
        self.data = data
        self.w, self.h = width, height
        self.unit = min(width, height)
        self.absorb = np.zeros((height, width, 3), dtype=np.float32)
        self.paper_grain = self.make_grain()

    def make_grain(self):
        rng = np.random.default_rng(int(unit_hash(self.data.get('name', ''), 'paper') * 2 ** 32))
        fine = rng.normal(0, 1, (self.h, self.w)).astype(np.float32)
        coarse = rng.normal(0, 1, (self.h // 6 + 2, self.w // 6 + 2)).astype(np.float32)
        coarse = np.asarray(Image.fromarray(coarse).resize((self.w, self.h), Image.BICUBIC))
        grain = 0.5 + 0.12 * fine + 0.25 * coarse
        return np.clip(grain, 0, 1)

    def glaze(self, cx, cy, radius, rgb, strength, key):
        rng = Rng(key)
        shape = deform(base_shape(radius, rng), 3, 0.32, rng)
        reach = max(math.hypot(x, y) for x, y, _ in shape)
        pad = int(reach * 1.6) + 6
        x0, y0 = max(0, int(cx - pad)), max(0, int(cy - pad))
        x1, y1 = min(self.w, int(cx + pad)), min(self.h, int(cy + pad))
        if x1 <= x0 or y1 <= y0:
            return
        mask = np.zeros((y1 - y0, x1 - x0), dtype=np.float32)
        for layer in range(LAYERS):
            pts = deform(shape, 2, 0.28, rng)
            img = Image.new('L', (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(img).polygon([(cx + x - x0, cy + y - y0) for x, y, _ in pts], fill=255)
            mask += np.asarray(img, dtype=np.float32) / 255
        mask /= LAYERS
        mask8 = Image.fromarray((mask * 255).astype(np.uint8), 'L')
        blurred = np.asarray(mask8.filter(ImageFilter.GaussianBlur(radius * 0.06 + 1)), dtype=np.float32) / 255
        edge = mask - blurred
        density = (mask * 0.75 + np.clip(edge, 0, 1) * 1.6) * strength
        grain = self.paper_grain[y0:y1, x0:x1]
        density *= 0.75 + 0.5 * grain
        pigment = 1 - np.array(rgb, dtype=np.float32) / 255
        self.absorb[y0:y1, x0:x1] += density[..., None] * pigment[None, None, :]

    def ink(self, segments):
        img = Image.new('L', (self.w, self.h), 0)
        draw = ImageDraw.Draw(img)
        for (xa, ya), (xb, yb), weight in segments:
            steps = 14
            pts = []
            for s in range(steps + 1):
                t = s / steps
                wobble = math.sin(t * math.pi * 3 + xa * 0.01) * self.unit * 0.002
                pts.append((xa + (xb - xa) * t + wobble, ya + (yb - ya) * t - wobble))
            draw.line(pts, fill=int(110 + 90 * weight), width=max(1, int(self.unit * 0.0014 * (1 + weight))))
        ink = np.asarray(img.filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255
        sepia = 1 - np.array([92, 70, 52], dtype=np.float32) / 255
        self.absorb += ink[..., None] * sepia[None, None, :] * 0.9

    def finish(self):
        compressed = self.absorb / (1 + 0.45 * self.absorb)
        pixels = PAPER[None, None, :] * np.exp(-compressed * 1.3)
        pixels *= (0.94 + 0.06 * self.paper_grain)[..., None]
        return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), 'RGB')


def render(data, width=1600, height=1600):
    files = sorted(data.get('files', []), key=lambda f: -f[1])
    painting = Painting(data, width, height)
    if not files:
        return painting.finish()

    stretch = (width / height) ** 0.5
    raw = {f[0]: file_position(f[0]) for f in files[:MAX_GLAZES * 4]}
    xs = [p[0] * stretch for p in raw.values()]
    ys = [p[1] for p in raw.values()]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    span = max(max(xs) - min(xs), (max(ys) - min(ys)) * width / height, 0.3)
    scale = width * 0.78 / span

    def to_px(x, y):
        return width / 2 + (x * stretch - cx) * scale, height / 2 + (y - cy) * scale

    total = sum(f[1] for f in files) or 1
    groups = districts(files, minimum=2, maximum=10)
    for name, group in groups:
        weight = sum(f[1] for f in group)
        points = [to_px(*raw[f[0]]) for f in group if f[0] in raw]
        if not points:
            continue
        gx = sum(p[0] for p in points) / len(points)
        gy = sum(p[1] for p in points) / len(points)
        dominant = max(group, key=lambda f: f[1])[0]
        radius = painting.unit * (0.1 + 0.26 * math.sqrt(weight / total))
        painting.glaze(gx, gy, radius, watercolour_tone(language_rgb(dominant), 0.2), 0.4, f'wash:{name}')

    segments = []
    for f in files[:MAX_GLAZES * 2]:
        parent = parent_dir(f[0])
        if f[0] in raw:
            segments.append((to_px(*dir_position(parent)), to_px(*raw[f[0]]), 0.2))
    painting.ink(segments[:400])

    max_bytes = files[0][1] or 1
    count = min(len(files), MAX_GLAZES)
    density = min(1.0, (30 / count) ** 0.5) if count else 1.0
    for f in files[:MAX_GLAZES]:
        x, y = to_px(*raw[f[0]])
        radius = painting.unit * (0.012 + 0.07 * math.sqrt(f[1] / max_bytes))
        heat = min(1.0, math.log1p(f[3]) / 4)
        painting.glaze(x, y, radius, watercolour_tone(language_rgb(f[0]), 0.6 + 0.4 * heat), 0.6 * density + 0.15, f'glaze:{f[0]}')

    return painting.finish()
