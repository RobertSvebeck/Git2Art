"""Expressionist: gestural bristle-brush painting structured by the code.

One sweeping gesture per top-level folder (width from its size, colour from
its main language), black calligraphic strokes along the main branches of the
folder tree, short slashing marks for files along their folder's gesture, and
splatter and drips from the most-edited files. Strokes are painted with a
simulated bristle brush: many hairs, uneven paint, tapering pressure, dry
breaks. Gestures are seeded by folder paths, so they stay put as code changes.
"""

import colorsys
import math

import numpy as np
from PIL import Image, ImageDraw

from .common import districts, extension, language_rgb, unit_hash

SUPERSAMPLE = 2
MAX_MARKS = 450


def vivid(rgb, boost=0.25):
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    r, g, b = colorsys.hls_to_rgb(h, min(0.6, max(0.3, l)), min(1.0, s + boost))
    return int(r * 255), int(g * 255), int(b * 255)


def bezier(points, steps):
    out = []
    n = len(points) - 1
    for k in range(steps + 1):
        t = k / steps
        x = y = 0.0
        for i, (px, py) in enumerate(points):
            c = math.comb(n, i) * (1 - t) ** (n - i) * t ** i
            x += c * px
            y += c * py
        out.append((x, y))
    return out


class Painting:
    def __init__(self, data, width, height):
        self.data = data
        self.w, self.h = width * SUPERSAMPLE, height * SUPERSAMPLE
        self.unit = min(self.w, self.h)
        self.rng = np.random.default_rng(int(unit_hash(data.get('name', ''), 'gesture') * 2 ** 32))
        self.image = self.ground()
        self.draw = ImageDraw.Draw(self.image, 'RGBA')

    def ground(self):
        langs = list(self.data.get('languages', {}))
        base = language_rgb(f'x{langs[0]}') if langs else (200, 190, 170)
        h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in base))
        r, g, b = colorsys.hls_to_rgb((h + 0.5) % 1.0, 0.9, 0.18)
        tone = np.array([r, g, b], dtype=np.float32) * 255
        noise = self.rng.normal(0, 1, (self.h // 40 + 2, self.w // 40 + 2)).astype(np.float32)
        noise = np.asarray(Image.fromarray(noise).resize((self.w, self.h), Image.BICUBIC))[..., None]
        pixels = tone[None, None, :] + noise * 6 + self.rng.normal(0, 3, (self.h, self.w, 1))
        return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), 'RGB')

    def gesture_path(self, key, cx, cy, reach):
        angle = unit_hash(key, 'angle') * 2 * math.pi
        dx, dy = math.cos(angle), math.sin(angle)
        px, py = -dy, dx
        points = [(cx - dx * reach, cy - dy * reach)]
        for i in (1, 2):
            along = (i / 3 - 0.5) * 2 * reach
            swing = (unit_hash(key, f'swing{i}') - 0.5) * 1.8 * reach
            points.append((cx + dx * along + px * swing, cy + dy * along + py * swing))
        points.append((cx + dx * reach * (0.6 + 0.6 * unit_hash(key, 'end')), cy + dy * reach * (0.6 + 0.6 * unit_hash(key, 'end'))))
        return points

    def brush(self, points, width, rgb, key, alpha=0.85, dry=0.6, steps=60):
        path = bezier(points, steps)
        left, right = [], []
        for k in range(len(path)):
            t = k / (len(path) - 1)
            if t > dry:
                break
            (x0, y0) = path[max(0, k - 1)]
            (x1, y1) = path[min(len(path) - 1, k + 1)]
            ddx, ddy = x1 - x0, y1 - y0
            length = math.hypot(ddx, ddy) or 1
            half = width / 2 * math.sin(math.pi * max(0.04, t)) ** 0.3 * (1 + self.rng.normal(0, 0.04))
            nx, ny = -ddy / length * half, ddx / length * half
            left.append((path[k][0] + nx, path[k][1] + ny))
            right.append((path[k][0] - nx, path[k][1] - ny))
        if len(left) > 2:
            self.draw.polygon(left + right[::-1], fill=tuple(rgb) + (int(255 * alpha),))

        bristles = max(4, int(width / (2.2 * SUPERSAMPLE)))
        for b in range(bristles):
            offset = (b / max(1, bristles - 1) - 0.5) * width * 0.95
            mixing = self.rng.normal(0, 0.18)
            target = (255, 255, 255) if mixing > 0 else (0, 0, 0)
            colour = tuple(int(c + (tc - c) * min(0.55, abs(mixing))) for c, tc in zip(rgb, target))
            load = self.rng.uniform(0.4, 1.0)
            hair = max(1, int(self.rng.uniform(0.8, 2.2) * SUPERSAMPLE))
            wobble = 0.0
            for k in range(len(path) - 1):
                t = k / (len(path) - 1)
                wobble += self.rng.normal(0, width * 0.006)
                (x0, y0), (x1, y1) = path[k], path[k + 1]
                ddx, ddy = x1 - x0, y1 - y0
                length = math.hypot(ddx, ddy) or 1
                o = (offset + wobble) * math.sin(math.pi * max(0.04, t)) ** 0.3
                nx, ny = -ddy / length * o, ddx / length * o
                if t > dry:
                    paint = load * (1 - (t - dry) / (1 - dry + 1e-6))
                    if self.rng.random() > paint * 1.3:
                        continue
                    a = int(255 * alpha * max(0.2, paint))
                    fill = tuple(rgb) + (a,)
                else:
                    a = int(255 * 0.32 * load)
                    fill = colour + (a,)
                self.draw.line((x0 + nx, y0 + ny, x1 + nx, y1 + ny), fill=fill, width=hair)
        return path

    def splatter(self, x, y, rgb, size, key):
        for k in range(int(8 + 20 * unit_hash(key, 'n'))):
            a = unit_hash(key, f'a{k}') * 2 * math.pi
            d = size * unit_hash(key, f'd{k}') ** 0.6 * 3
            r = size * 0.18 * (0.3 + unit_hash(key, f'r{k}'))
            px, py = x + math.cos(a) * d, y + math.sin(a) * d
            self.draw.ellipse((px - r, py - r, px + r, py + r), fill=rgb + (220,))
        if unit_hash(key, 'drip') < 0.6:
            length = size * (2 + 5 * unit_hash(key, 'dl'))
            self.draw.line((x, y, x + size * 0.1, y + length), fill=rgb + (210,), width=max(2, int(size * 0.18)))
            self.draw.ellipse((x - size * 0.16, y + length - size * 0.16, x + size * 0.2, y + length + size * 0.2), fill=rgb + (220,))


def render(data, width=1600, height=1600):
    painting = Painting(data, width, height)
    files = sorted(data.get('files', []), key=lambda f: -f[1])
    if not files:
        return painting.image.resize((width, height), Image.LANCZOS)
    total = sum(f[1] for f in files) or 1
    max_bytes = files[0][1] or 1
    groups = districts(files, minimum=3, maximum=10)
    w, h, unit = painting.w, painting.h, painting.unit

    gestures = []
    for name, group in groups:
        weight = sum(f[1] for f in group) / total
        dominant = max(group, key=lambda f: f[1])[0]
        colour = vivid(language_rgb(dominant))
        cx = w * (0.15 + 0.7 * unit_hash(name, 'x'))
        cy = h * (0.15 + 0.7 * unit_hash(name, 'y'))
        painting.brush(painting.gesture_path(f'under:{name}', cx, cy, unit * (0.3 + 0.3 * math.sqrt(weight))),
                       unit * (0.12 + 0.2 * math.sqrt(weight)), colour, f'under:{name}', alpha=0.3, dry=0.75, steps=40)

    for name, group in groups:
        weight = sum(f[1] for f in group) / total
        dominant = max(group, key=lambda f: f[1])[0]
        colour = vivid(language_rgb(dominant))
        cx = w * (0.15 + 0.7 * unit_hash(name, 'x'))
        cy = h * (0.15 + 0.7 * unit_hash(name, 'y'))
        count = 2 + min(4, int(math.log1p(len(group))))
        for g in range(count):
            key = f'{name}#{g}'
            ox = (unit_hash(key, 'ox') - 0.5) * unit * 0.25
            oy = (unit_hash(key, 'oy') - 0.5) * unit * 0.25
            reach = unit * (0.12 + 0.22 * math.sqrt(weight)) * (0.7 + 0.5 * unit_hash(key, 'reach'))
            width_px = unit * (0.02 + 0.09 * math.sqrt(weight)) * (0.6 + 0.6 * unit_hash(key, 'width'))
            path = painting.brush(painting.gesture_path(key, cx + ox, cy + oy, reach), width_px, colour, key)
            gestures.append((name, group, path, colour, width_px))

    for name, group, path, colour, width_px in sorted(gestures, key=lambda g: -g[4])[:2]:
        key = f'kline:{name}'
        anchor = path[len(path) // 2]
        painting.brush(painting.gesture_path(key, anchor[0], anchor[1], unit * (0.2 + 0.15 * unit_hash(key, 'r'))),
                       unit * 0.035, (24, 22, 20), key, alpha=0.85, dry=0.5, steps=50)

    marks = 0
    touches = sorted((f[3] for f in files), reverse=True)
    hot = touches[max(0, len(touches) // 12)] if touches else 0
    seen = set()
    for name, group, path, colour, width_px in gestures:
        if name in seen:
            continue
        seen.add(name)
        for f in group:
            if marks >= MAX_MARKS:
                break
            t = unit_hash(f[0], 't')
            px, py = path[int(t * (len(path) - 1))]
            spread = width_px * 1.4
            x = px + (unit_hash(f[0], 'ox') - 0.5) * spread
            y = py + (unit_hash(f[0], 'oy') - 0.5) * spread
            length = unit * (0.02 + 0.07 * math.sqrt(f[1] / max_bytes))
            a = unit_hash(f[0], 'a') * math.pi
            mark = [(x - math.cos(a) * length / 2, y - math.sin(a) * length / 2), (x, y + length * 0.08),
                    (x + math.cos(a) * length / 2, y + math.sin(a) * length / 2)]
            painting.brush(mark, unit * (0.004 + 0.012 * math.sqrt(f[1] / max_bytes)),
                           vivid(language_rgb(f[0]), 0.35), f[0], alpha=0.8, dry=0.6, steps=10)
            if f[3] >= max(hot, 2) and extension(f[0]):
                painting.splatter(x, y, vivid(language_rgb(f[0]), 0.4), unit * 0.012, f'spl:{f[0]}')
            marks += 1

    return painting.image.resize((width, height), Image.LANCZOS)
