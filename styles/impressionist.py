"""Impressionist: broken brushstrokes swirling around the folders like a pond.

A soft underpainting takes each file's language colour around its position
(path-stable layout). Short strokes follow a flow field that circles each
folder, painted in passes from broad to fine, with broken colour and a few
complementary accents. The most-edited files catch the light as bright dabs.
"""

import colorsys
import math

import numpy as np
from PIL import Image, ImageDraw

from scene.layout import dir_position, file_position, parent_dir
from .common import language_rgb, unit_hash

SUPERSAMPLE = 2
FIELD = 96
MAX_FILES = 600
GROUND = np.array([226, 222, 200], dtype=np.float32)


def pastel(rgb, amount=0.28):
    return tuple(c + (255 - c) * amount for c in rgb)


def complement(rgb):
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    r, g, b = colorsys.hls_to_rgb((h + 0.5) % 1.0, min(0.85, l + 0.1), s * 0.8)
    return r * 255, g * 255, b * 255


def jitter(rgb, rng, amount):
    h, l, s = colorsys.rgb_to_hls(*(max(0, min(255, c)) / 255 for c in rgb))
    h = (h + rng.normal(0, 0.02)) % 1.0
    l = min(0.95, max(0.08, l + rng.normal(0, amount)))
    s = min(1.0, max(0.0, s + rng.normal(0, 0.06)))
    return tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, l, s))


class Canvas:
    def __init__(self, data, width, height):
        self.data = data
        self.w, self.h = width * SUPERSAMPLE, height * SUPERSAMPLE
        self.unit = min(self.w, self.h)
        self.rng = np.random.default_rng(int(unit_hash(data.get('name', ''), 'brush') * 2 ** 32))
        files = sorted(data.get('files', []), key=lambda f: -f[1])[:MAX_FILES]
        self.files = files
        stretch = (width / height) ** 0.5
        pos = {f[0]: file_position(f[0]) for f in files}
        xs = [p[0] * stretch for p in pos.values()] or [0]
        ys = [p[1] for p in pos.values()] or [0]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        span = max(max(xs) - min(xs), (max(ys) - min(ys)) * width / height, 0.3)
        scale = 0.82 / span

        def to_unit(x, y):
            return 0.5 + (x * stretch - cx) * scale, 0.5 + (y - cy) * scale * width / height

        self.points = [(*to_unit(*pos[f[0]]), f) for f in files]
        dirs = {}
        for f in files:
            d = parent_dir(f[0])
            dirs[d] = dirs.get(d, 0) + f[1]
        self.dirs = [(*to_unit(*dir_position(d)), weight) for d, weight in dirs.items()]
        self.colour_field = self.make_colour_field()

    def make_colour_field(self):
        ys, xs = np.mgrid[0:FIELD, 0:FIELD].astype(np.float32) / (FIELD - 1)
        total = np.full((FIELD, FIELD), 0.35, dtype=np.float32)
        colour = GROUND[None, None, :] * total[..., None]
        max_bytes = max((f[1] for f in self.files), default=1)
        reach = min(2.6, max(1.0, (40 / max(1, len(self.files))) ** 0.45))
        for x, y, f in self.points:
            influence = (0.03 + 0.12 * math.sqrt(f[1] / max_bytes)) * reach
            weight = np.exp(-((xs - x) ** 2 + (ys - y) ** 2) / (2 * influence ** 2)) * (0.4 + math.sqrt(f[1] / max_bytes))
            colour += weight[..., None] * np.array(pastel(language_rgb(f[0])), dtype=np.float32)[None, None, :]
            total += weight
        return colour / total[..., None]

    def colour_at(self, u, v):
        i = min(FIELD - 1, max(0, int(v * (FIELD - 1))))
        j = min(FIELD - 1, max(0, int(u * (FIELD - 1))))
        return tuple(self.colour_field[i, j])

    def flow_at(self, u, v):
        fx, fy = 0.0, 0.0
        for dx, dy, weight in self.dirs:
            rx, ry = u - dx, v - dy
            d2 = rx * rx + ry * ry + 0.004
            strength = math.sqrt(weight) / d2
            fx += -ry * strength
            fy += rx * strength
        fx += math.sin(v * 9.0) * 0.3 * (abs(fx) + abs(fy) + 1e-6)
        return math.atan2(fy, fx)

    def stroke(self, draw, u, v, length, width, colour):
        a = self.flow_at(u, v) + self.rng.normal(0, 0.18)
        x, y = u * self.w, v * self.h
        dx, dy = math.cos(a) * length / 2, math.sin(a) * length / 2
        draw.line((x - dx, y - dy, x + dx, y + dy), fill=colour, width=max(1, int(width)))
        r = width / 2
        draw.ellipse((x - dx - r, y - dy - r, x - dx + r, y - dy + r), fill=colour)
        draw.ellipse((x + dx - r, y + dy - r, x + dx + r, y + dy + r), fill=colour)

    def paint(self):
        base = Image.fromarray(self.colour_field.astype(np.uint8), 'RGB').resize((self.w, self.h), Image.BICUBIC)
        draw = ImageDraw.Draw(base)
        for count, length, width, light in ((2600, 0.05, 0.016, 0.06), (5200, 0.03, 0.009, 0.08), (7000, 0.018, 0.005, 0.1)):
            for _ in range(count):
                u, v = self.rng.random(), self.rng.random()
                colour = self.colour_at(u, v)
                if self.rng.random() < 0.035:
                    colour = complement(colour)
                self.stroke(draw, u, v, self.unit * length * self.rng.uniform(0.6, 1.3),
                            self.unit * width * self.rng.uniform(0.7, 1.3), jitter(colour, self.rng, light))
        touches = sorted((f[3] for _, _, f in self.points), reverse=True)
        cut = touches[max(0, len(touches) // 8)] if touches else 0
        for x, y, f in self.points:
            if f[3] < max(cut, 2):
                continue
            for _ in range(6):
                u, v = x + self.rng.normal(0, 0.012), y + self.rng.normal(0, 0.012)
                glint = jitter((255, 246, 214), self.rng, 0.03)
                self.stroke(draw, u, v, self.unit * 0.012, self.unit * 0.0045, glint)
        return base


def render(data, width=1600, height=1600):
    if not data.get('files'):
        return Image.new('RGB', (width, height), tuple(int(c) for c in GROUND))
    return Canvas(data, width, height).paint().resize((width, height), Image.LANCZOS)
