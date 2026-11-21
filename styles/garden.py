"""Garden: the repository as a botanical plate.

Each top-level folder grows as a plant whose branches follow its subfolders.
Files are leaves (sized by bytes); the most-edited files flower in their
language colour; documentation blooms as daisies and data files as berries.
Old code is woody, recent code is green. Butterflies are contributors.
Every angle and position comes from hashing paths, so plants change gently.
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .common import DOC_EXTENSIONS, districts, extension, language_rgb, unit_hash

SUPERSAMPLE = 2
MAX_LEAVES = 1600
PAPER = (243, 236, 220)
BARK = np.array([107, 74, 47], dtype=np.float32)
SHOOT = np.array([92, 143, 60], dtype=np.float32)
LEAF_DARK = (58, 104, 52)
LEAF_LIGHT = (126, 176, 84)
SOIL = (122, 92, 64)
DATA_EXTENSIONS = {'.json', '.csv', '.yml', '.yaml', '.toml', '.xml', '.sql'}


class Branch:
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.files = []
        self.weight = 0
        self.born = 1.0

    def add(self, parts, record, born):
        self.weight += record[1]
        self.born = min(self.born, born)
        if len(parts) == 1:
            self.files.append(record)
            return
        self.children.setdefault(parts[0], Branch(parts[0])).add(parts[1:], record, born)


def mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


class Garden:
    def __init__(self, data, width, height):
        self.data = data
        self.w, self.h = width * SUPERSAMPLE, height * SUPERSAMPLE
        self.unit = min(self.w, self.h)
        self.image = Image.new('RGB', (self.w, self.h), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.commits = max(1, data.get('commits', 1))
        files = sorted(data.get('files', []), key=lambda f: -f[1])[:MAX_LEAVES]
        self.files = files
        self.max_bytes = max((f[1] for f in files), default=1)
        touches = sorted((f[3] for f in files), reverse=True)
        self.bloom_cut = touches[max(0, len(touches) // 10)] if touches else 0
        self.ground = int(self.h * 0.9)
        self.scale = min(3.0, max(1.0, (60 / max(1, len(files))) ** 0.4))
        self.flowers = []
        self.leaves = []

    # Background: aged paper with a soft wash and a soil bed.
    def paint_background(self):
        rng = np.random.default_rng(int(unit_hash(self.data.get('name', ''), 'paper') * 2 ** 32))
        pixels = np.asarray(self.image, dtype=np.float32)
        low = rng.normal(0, 1, (self.h // 80 + 2, self.w // 80 + 2)).astype(np.float32)
        low = np.asarray(Image.fromarray(low).resize((self.w, self.h), Image.BICUBIC))[..., None]
        ys = np.linspace(0, 1, self.h, dtype=np.float32)[:, None, None]
        vignette = (np.abs(np.linspace(-1, 1, self.w, dtype=np.float32))[None, :, None] ** 2) * 10 + ys * 6
        pixels = pixels + low * 4 - vignette + rng.normal(0, 2.0, pixels.shape)
        self.image = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), 'RGB')
        self.draw = ImageDraw.Draw(self.image)
        for y in range(self.ground, self.h):
            t = (y - self.ground) / max(1, self.h - self.ground)
            self.draw.line((0, y, self.w, y), fill=mix((96, 72, 50), SOIL, min(1.0, t * 2.5)))
        for k in range(int(self.w / 6)):
            x = unit_hash(self.data.get('name', ''), f'soil{k}') * self.w
            y = self.ground + unit_hash(self.data.get('name', ''), f'soily{k}') * (self.h - self.ground)
            self.draw.ellipse((x - 3, y - 2, x + 3, y + 2), fill=mix(SOIL, (70, 50, 34), 0.6))
        grass = mix(LEAF_DARK, LEAF_LIGHT, 0.4)
        for k in range(int(self.w / 9)):
            x = unit_hash(self.data.get('name', ''), f'grass{k}') * self.w
            tall = self.unit * (0.008 + 0.018 * unit_hash(self.data.get('name', ''), f'gt{k}'))
            lean = (unit_hash(self.data.get('name', ''), f'gl{k}') - 0.5) * tall
            self.draw.line((x, self.ground + 4, x + lean, self.ground - tall), fill=grass, width=max(2, SUPERSAMPLE))

    # One plant per district, spaced by weight.
    def layout(self):
        groups = districts(self.files, minimum=2, maximum=9)
        plants = []
        for name, files in groups:
            root = Branch(name)
            depth = 0 if name in ('', '(other)') else name.count('/') + 1
            for record in files:
                parts = record[0].split('/')[depth:] or [record[0]]
                root.add(parts, record, record[2] / self.commits)
            plants.append(root)
        plants.sort(key=lambda p: unit_hash(p.name, 'bed'))
        total = sum(math.sqrt(p.weight) for p in plants) or 1
        heaviest = max(p.weight for p in plants)
        x = self.w * 0.08
        span = self.w * 0.84
        for plant in plants:
            share = math.sqrt(plant.weight) / total
            centre = x + span * share / 2
            x += span * share
            height = self.h * (0.36 + 0.4 * (plant.weight / heaviest) ** 0.35)
            yield plant, centre, height

    def stem_colour(self, born):
        t = min(1.0, max(0.0, born) * 1.4)
        return tuple(int(c) for c in BARK + (SHOOT - BARK) * t)

    def grow(self, branch, x, y, angle, length, width, depth, key):
        steps = 10
        bend = (unit_hash(key, 'bend') - 0.5) * 0.5
        colour = self.stem_colour(branch.born)
        points = [(x, y)]
        px, py, a = x, y, angle
        for s in range(steps):
            a += bend / steps + math.sin(s * 0.9 + unit_hash(key, 'wave') * 6) * 0.015
            px += math.cos(a) * length / steps
            py -= math.sin(a) * length / steps
            points.append((px, py))
        for s in range(steps):
            w = max(1.5, width * (1 - 0.55 * s / steps))
            self.draw.line((points[s], points[s + 1]), fill=colour, width=int(w))
            self.draw.ellipse((points[s + 1][0] - w / 2, points[s + 1][1] - w / 2,
                               points[s + 1][0] + w / 2, points[s + 1][1] + w / 2), fill=colour)

        def along(t):
            i = min(steps - 1, int(t * steps))
            f = t * steps - i
            (x0, y0), (x1, y1) = points[i], points[i + 1]
            return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, math.atan2(-(y1 - y0), x1 - x0)

        children = sorted(branch.children.values(), key=lambda c: -c.weight)
        for index, child in enumerate(children[:9]):
            ckey = f'{key}/{child.name}'
            t = 0.3 + 0.62 * unit_hash(ckey, 'at')
            bx, by, ba = along(t)
            side = 1 if (index + int(unit_hash(ckey, 'side') * 2)) % 2 else -1
            spread = math.radians(22 + 30 * unit_hash(ckey, 'spread'))
            share = math.sqrt(child.weight / max(branch.weight, 1))
            self.grow(child, bx, by, ba + side * spread, length * (0.4 + 0.3 * share),
                      max(1.5, width * (0.35 + 0.5 * share)), depth + 1, ckey)

        for record in branch.files:
            path, size, born, touches = record
            t = 0.15 + 0.85 * unit_hash(path, 'leafat')
            lx, ly, la = along(t)
            side = 1 if unit_hash(path, 'leafside') < 0.5 else -1
            ext = extension(path)
            if touches >= self.bloom_cut and touches > 1 or ext in DOC_EXTENSIONS or ext in DATA_EXTENSIONS:
                stalk = self.unit * 0.012
                fa = la + side * math.radians(35)
                fx, fy = lx + math.cos(fa) * stalk, ly - math.sin(fa) * stalk
                self.draw.line((lx, ly, fx, fy), fill=colour, width=max(2, int(width * 0.25)))
                self.flowers.append((fx, fy, record))
            else:
                self.leaves.append((lx, ly, la + side * math.radians(40 + 25 * unit_hash(path, 'la')), record))

    def paint_leaf(self, x, y, angle, record):
        path, size, born, _ = record
        length = self.unit * (0.012 + 0.04 * math.sqrt(size / self.max_bytes)) * self.scale
        width = length * 0.42
        ca, sa = math.cos(angle), -math.sin(angle)
        outline = []
        for k in range(13):
            t = k / 12
            r = math.sin(t * math.pi) * width / 2
            outline.append((t * length, r))
        for k in range(12, -1, -1):
            t = k / 12
            outline.append((t * length, -math.sin(t * math.pi) * width / 2 * 0.85))
        poly = [(x + u * ca - v * sa, y + u * sa + v * ca) for u, v in outline]
        shade = mix(LEAF_DARK, LEAF_LIGHT, min(1.0, born / self.commits * 1.2 + 0.25 * unit_hash(path, 'ls')))
        self.draw.polygon(poly, fill=shade)
        tip = (x + length * ca, y + length * sa)
        self.draw.line(((x, y), tip), fill=mix(shade, (30, 60, 30), 0.35), width=max(1, SUPERSAMPLE))

    def paint_flower(self, x, y, record):
        path, size, _, touches = record
        ext = extension(path)
        r = self.unit * (0.008 + 0.016 * math.sqrt(size / self.max_bytes)) * self.scale
        if ext in DATA_EXTENSIONS:
            berry = mix((150, 30, 50), language_rgb(path), 0.25)
            for k in range(3):
                a = k * 2.1 + unit_hash(path, 'berry') * 6
                bx, by = x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7
                self.draw.ellipse((bx - r * 0.55, by - r * 0.55, bx + r * 0.55, by + r * 0.55), fill=berry)
                self.draw.ellipse((bx - r * 0.25, by - r * 0.35, bx - r * 0.05, by - r * 0.15), fill=(240, 210, 210))
            return
        petal = (247, 246, 240) if ext in DOC_EXTENSIONS else language_rgb(path)
        centre = (233, 182, 44) if ext in DOC_EXTENSIONS else mix(petal, (60, 30, 20), 0.55)
        count = 5 + int(unit_hash(path, 'petals') * 4)
        spin = unit_hash(path, 'spin') * math.pi
        for k in range(count):
            a = spin + k * 2 * math.pi / count
            px, py = x + math.cos(a) * r * 0.85, y + math.sin(a) * r * 0.85
            self.draw.ellipse((px - r * 0.55, py - r * 0.55, px + r * 0.55, py + r * 0.55),
                              fill=petal, outline=mix(petal, (0, 0, 0), 0.25))
        self.draw.ellipse((x - r * 0.42, y - r * 0.42, x + r * 0.42, y + r * 0.42), fill=centre)

    def paint_butterflies(self):
        authors = min(9, self.data.get('authors', 0))
        name = self.data.get('name', '')
        wing_colours = [language_rgb(f'x{ext}') for ext in self.data.get('languages', {})] or [(230, 150, 60)]
        for k in range(authors):
            x = self.w * (0.1 + 0.8 * unit_hash(name, f'b{k}x'))
            y = self.h * (0.08 + 0.4 * unit_hash(name, f'b{k}y'))
            s = self.unit * (0.016 + 0.012 * unit_hash(name, f'b{k}s'))
            colour = wing_colours[k % len(wing_colours)]
            tilt = (unit_hash(name, f'b{k}t') - 0.5) * 0.8
            for side in (-1, 1):
                for wing, scale in ((0.9, 1.0), (1.6, 0.7)):
                    a = tilt + side * wing
                    wx, wy = x + math.cos(a) * s * 0.6 * side, y - math.sin(wing) * s * 0.3 * (1 if scale == 1 else -1)
                    self.draw.ellipse((wx - s * scale * 0.6, wy - s * scale * 0.45, wx + s * scale * 0.6, wy + s * scale * 0.45),
                                      fill=colour, outline=mix(colour, (0, 0, 0), 0.4))
            self.draw.line((x, y - s * 0.5, x, y + s * 0.5), fill=(40, 30, 25), width=max(2, SUPERSAMPLE))

    def render(self):
        self.paint_background()
        for plant, centre, height in self.layout():
            width = self.unit * (0.006 + 0.016 * min(1.0, math.sqrt(plant.weight / max(1, self.max_bytes * 6))))
            lean = (unit_hash(plant.name, 'lean') - 0.5) * 0.25
            self.grow(plant, centre, self.ground, math.pi / 2 + lean, height * 0.58, width * self.scale ** 0.5, 0, plant.name or 'root')
        for x, y, angle, record in self.leaves:
            self.paint_leaf(x, y, angle, record)
        for x, y, record in self.flowers:
            self.paint_flower(x, y, record)
        self.paint_butterflies()
        return self.image


def render(data, width=1600, height=1600):
    image = Garden(data, width, height).render()
    image = image.filter(ImageFilter.GaussianBlur(0.6))
    return image.resize((width, height), Image.LANCZOS)
