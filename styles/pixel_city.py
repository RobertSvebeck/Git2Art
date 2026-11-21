"""Pixel City: a repository as an isometric 8-bit city.

Folders become districts separated by roads, files become buildings (height
from size, colour from language), documentation becomes parks, data files
become low warehouses. Windows light up with how often a file changed. The
sky follows how recently the repository was active: day, sunset or night.
Every plot is chosen by hashing the file path, so small changes stay small.
"""

import math

from PIL import Image, ImageDraw

from .common import (DOC_EXTENSIONS, bayer4, clamp, days_idle, districts, extension, hex_rgb,
                     language_rgb, nearest, shade, sqrt_scale, treemap, unit_hash)

PIXEL = 4
MAX_BUILDINGS = 700
DATA_EXTENSIONS = {'.json', '.csv', '.yml', '.yaml', '.toml', '.xml', '.sql', '.lock'}

PALETTE = [hex_rgb(h) for h in (
    '#0b0d17', '#1c1f2e', '#2e3247', '#4a4f68', '#6d7391', '#9aa1bd', '#c9cfe3', '#f4f5fa',
    '#10244a', '#1d4f91', '#3b7dd8', '#6fb3f2', '#a9e0ff',
    '#14351f', '#2a6b3a', '#4ea04c', '#8fd16a',
    '#fff2a8', '#ffd23f', '#f59e2b', '#d2632a',
    '#7a1f2b', '#c23a3a', '#ff6b6b',
    '#2d1b4e', '#5b3c8f', '#9b6fd0',
    '#1f6f6b', '#3fd0c4',
    '#5a3a24', '#9c6b43', '#d9b38c',
)]

SKIES = {
    'day': {'bands': ['#1d4f91', '#3b7dd8', '#6fb3f2', '#a9e0ff'], 'light': 1.0, 'stars': False, 'clouds': '#f4f5fa',
            'water': ['#1d4f91', '#3b7dd8'], 'glint': '#a9e0ff'},
    'dusk': {'bands': ['#2d1b4e', '#5b3c8f', '#d2632a', '#f59e2b', '#ffd23f'], 'light': 0.8, 'stars': False, 'clouds': '#ff6b6b',
             'water': ['#2d1b4e', '#5b3c8f'], 'glint': '#f59e2b'},
    'night': {'bands': ['#0b0d17', '#10244a', '#1c1f2e', '#2e3247'], 'light': 0.42, 'stars': True, 'clouds': None,
              'water': ['#0b0d17', '#10244a'], 'glint': '#ffd23f'},
}


def sky_for(data):
    idle = days_idle(data)
    if idle < 30:
        return 'day'
    if idle < 365:
        return 'dusk'
    return 'night'


class City:
    def __init__(self, data, width, height):
        self.data = data
        self.lw, self.lh = width // PIXEL, height // PIXEL
        self.sky = SKIES[sky_for(data)]
        self.night = self.sky['light'] < 0.5
        files = sorted(data.get('files', []), key=lambda f: -f[1])[:MAX_BUILDINGS]
        self.files = files
        self.max_bytes = max((f[1] for f in files), default=1)
        self.max_touches = max((f[3] for f in files), default=1)
        n = max(1, len(files))
        fits = int(min(self.lw * 0.9 / 8, self.lh * 0.5 / 4))
        self.grid = int(clamp(math.ceil(math.sqrt(n * 2.4)) + 3, 7, fits))
        tile = int(min(self.lw * 0.9 / self.grid, self.lh * 1.0 / self.grid, 40)) // 2 * 2
        self.tw = max(8, tile)
        self.th = self.tw // 2
        self.ox = self.lw // 2
        self.oy = int(self.lh * 0.97) - self.grid * self.th
        self.img = Image.new('RGB', (self.lw, self.lh))
        self.draw = ImageDraw.Draw(self.img)

    def iso(self, i, j):
        return self.ox + (i - j) * self.tw // 2, self.oy + (i + j) * self.th // 2

    def colour(self, rgb, factor=1.0):
        return nearest(shade(rgb, factor * (0.55 + 0.45 * self.sky['light'])), PALETTE)

    # Sky, stars, clouds and a distant skyline.
    def paint_sky(self):
        bands = [hex_rgb(h) for h in self.sky['bands']]
        horizon = max(1, self.oy + self.th * 2)
        matrix = bayer4()
        pixels = self.img.load()
        for y in range(self.lh):
            t = clamp(y / horizon, 0, 0.999) * (len(bands) - 1)
            low, frac = int(t), t - int(t)
            for x in range(self.lw):
                pixels[x, y] = bands[low + 1] if frac * 16 > matrix[y % 4][x % 4] else bands[low]
        seed = self.data.get('name', '')
        if self.sky['stars']:
            for k in range(self.lw * self.lh // 90):
                x, y = int(unit_hash(seed, f's{k}x') * self.lw), int(unit_hash(seed, f's{k}y') * horizon * 0.9)
                pixels[x, y] = hex_rgb('#c9cfe3') if k % 7 else hex_rgb('#fff2a8')
            mx, my, r = int(self.lw * 0.8), int(self.lh * 0.14), max(4, self.lw // 40)
            self.draw.ellipse((mx - r, my - r, mx + r, my + r), fill=hex_rgb('#f4f5fa'))
            self.draw.ellipse((mx - r + r // 2, my - r - 1, mx + r + r // 2, my + r - 1), fill=bands[0])
        if self.sky['clouds']:
            cloud = hex_rgb(self.sky['clouds'])
            for k in range(5):
                cx = int(unit_hash(seed, f'c{k}x') * self.lw)
                cy = int((0.08 + unit_hash(seed, f'c{k}y') * 0.3) * horizon)
                w = int(self.lw * (0.06 + 0.1 * unit_hash(seed, f'c{k}w')))
                for b in range(3):
                    bx = cx + (b - 1) * w // 3
                    bh = max(2, w // (5 - (b == 1)))
                    self.draw.ellipse((bx - w // 3, cy - bh // 2, bx + w // 3, cy + bh // 2), fill=cloud)
        skyline = hex_rgb('#2e3247') if not self.night else hex_rgb('#1c1f2e')
        x = 0
        base = self.oy + self.grid * self.th // 2
        self.paint_water(base, seed)
        while x < self.lw:
            w = 3 + int(unit_hash(seed, f'k{x}') * 7)
            h = 4 + int(unit_hash(seed, f'kh{x}') * self.lh * 0.12)
            self.draw.rectangle((x, base - h, x + w, base), fill=skyline)
            if self.night and h > 6:
                for wy in range(base - h + 2, base, 3):
                    if unit_hash(seed, f'kw{x}{wy}') < 0.3:
                        self.draw.point((x + 1 + int(unit_hash(seed, f'kx{wy}') * max(1, w - 2)), wy), fill=hex_rgb('#d2632a'))
            x += w + 1

    def paint_water(self, horizon, seed):
        deep, shallow = (hex_rgb(h) for h in self.sky['water'])
        glint = hex_rgb(self.sky['glint'])
        matrix = bayer4()
        pixels = self.img.load()
        for y in range(horizon, self.lh):
            t = (y - horizon) / max(1, self.lh - horizon)
            for x in range(self.lw):
                pixels[x, y] = deep if t * 16 > matrix[y % 4][x % 4] else shallow
        for k in range(self.lw // 3):
            y = horizon + 2 + int(unit_hash(seed, f'g{k}y') * (self.lh - horizon - 3))
            x = int(unit_hash(seed, f'g{k}x') * self.lw)
            length = 2 + int(unit_hash(seed, f'g{k}l') * 6)
            self.draw.line((x, y, x + length, y), fill=glint)

    # Ground diamond, districts, roads and plots.
    def plan(self):
        groups = districts(self.files)
        names = [name for name, _ in groups]
        weights = [len(fs) + 2 for _, fs in groups]
        rects = treemap((0, 0, self.grid, self.grid), weights, names)
        plots, roads = {}, set()
        for name, fs in groups:
            x, y, w, h = rects[name]
            for i in range(x, x + w):
                for j in range(y, y + h):
                    if (i == x + w - 1 and w > 2) or (j == y + h - 1 and h > 2):
                        roads.add((i, j))
            free = [(i, j) for i in range(x, x + w) for j in range(y, y + h) if (i, j) not in roads]
            taken = set()
            for f in sorted(fs, key=lambda f: f[0]):
                if not free or len(taken) >= len(free):
                    break
                k = int(unit_hash(f[0], 'plot') * len(free))
                while free[k] in taken:
                    k = (k + 1) % len(free)
                taken.add(free[k])
                plots[free[k]] = f
            for tile in free:
                if tile not in taken:
                    plots.setdefault(tile, None)
        return plots, roads

    def tile_poly(self, i, j, inset=0.0):
        x, y = self.iso(i, j)
        cx, cy = x, y + self.th / 2
        corners = [(x, y), (x + self.tw / 2, y + self.th / 2), (x, y + self.th), (x - self.tw / 2, y + self.th / 2)]
        return [(cx + (px - cx) * (1 - inset), cy + (py - cy) * (1 - inset)) for px, py in corners]

    def paint_ground(self, plots, roads):
        grass = self.colour(hex_rgb('#2a6b3a'))
        grass2 = self.colour(hex_rgb('#4ea04c'))
        road = self.colour(hex_rgb('#2e3247'))
        paving = self.colour(hex_rgb('#6d7391'))
        for i in range(self.grid):
            for j in range(self.grid):
                if (i, j) in roads:
                    fill = road
                elif plots.get((i, j)) is not None:
                    fill = paving
                else:
                    fill = grass if (i + j) % 2 else grass2
                self.draw.polygon(self.tile_poly(i, j), fill=fill)
        edge = self.colour(hex_rgb('#14351f'))
        left, bottom, right = self.iso(0, self.grid), self.iso(self.grid, self.grid), self.iso(self.grid, 0)
        depth = max(2, self.th)
        self.draw.polygon([left, bottom, (bottom[0], bottom[1] + depth), (left[0], left[1] + depth)], fill=shade(edge, 0.8))
        self.draw.polygon([bottom, right, (right[0], right[1] + depth), (bottom[0], bottom[1] + depth)], fill=shade(edge, 0.6))
        if self.night:
            lamp = hex_rgb('#ffd23f')
            for (i, j) in roads:
                if unit_hash(f'{i},{j}', 'lamp') < 0.18:
                    x, y = self.iso(i, j)
                    self.draw.point((x, y + self.th // 2), fill=lamp)

    def paint_tree(self, i, j, key):
        x, y = self.iso(i, j)
        cy = y + self.th // 2
        r = max(2, self.tw // 4)
        trunk = self.colour(hex_rgb('#5a3a24'))
        leaf = self.colour(hex_rgb('#4ea04c' if unit_hash(key, 'leaf') < 0.6 else '#2a6b3a'))
        self.draw.line((x, cy, x, cy - r), fill=trunk)
        self.draw.ellipse((x - r, cy - r * 2 - 1, x + r, cy - 1), fill=leaf)
        self.draw.point((x - r // 2, cy - r * 2 + 1), fill=self.colour(hex_rgb('#8fd16a')))

    def paint_building(self, i, j, f):
        path, size, born, touches = f
        ext = extension(path)
        base = language_rgb(path)
        warehouse = ext in DATA_EXTENSIONS
        scale = 0.5 * sqrt_scale(size, self.max_bytes) + 0.5 * math.log1p(size) / math.log1p(self.max_bytes)
        height = max(2, int(self.th * 0.6 + (self.th * 1.5 if warehouse else self.tw * 4.2) * scale))
        inset = 0.12 if self.tw >= 12 else 0.08
        top, right, bottom, left = self.tile_poly(i, j, inset)
        up = lambda p: (p[0], p[1] - height)
        top_face = [up(top), up(right), up(bottom), up(left)]
        left_face = [left, bottom, up(bottom), up(left)]
        right_face = [bottom, right, up(right), up(bottom)]
        self.draw.polygon(left_face, fill=self.colour(base, 0.85))
        self.draw.polygon(right_face, fill=self.colour(base, 0.6))
        self.draw.polygon(top_face, fill=self.colour(base, 1.15))
        activity = math.log1p(touches) / math.log1p(self.max_touches or 1)
        self.paint_windows(path, left, bottom, height, base, activity, 0.85)
        self.paint_windows(path + '#r', bottom, right, height, base, activity, 0.6)
        if not warehouse and height > self.tw * 2.2:
            tip = up(bottom)[0], up(top)[1] + (up(bottom)[1] - up(top)[1]) // 2
            mast = max(2, height // 6)
            self.draw.line((tip[0], tip[1], tip[0], tip[1] - mast), fill=self.colour(hex_rgb('#9aa1bd')))
            if self.night:
                self.draw.point((tip[0], tip[1] - mast), fill=hex_rgb('#ff6b6b'))

    def paint_windows(self, key, a, b, height, base, activity, face_shade):
        dark = self.colour(base, face_shade * 0.55)
        lit = hex_rgb('#ffd23f') if self.night else hex_rgb('#fff2a8')
        glass = self.colour(hex_rgb('#a9e0ff'), 0.9) if not self.night else dark
        chance = 0.08 + 0.55 * activity if self.night else 0.04 + 0.2 * activity
        width = abs(b[0] - a[0])
        for col in range(2, int(width) - 1, 2):
            t = col / width
            x = a[0] + (b[0] - a[0]) * t
            y0 = a[1] + (b[1] - a[1]) * t
            for row, dy in enumerate(range(3, height - 2, 3)):
                k = unit_hash(key, f'{col}:{row}')
                fill = lit if k < chance else (glass if k < chance + 0.25 else dark)
                self.draw.point((round(x), round(y0 - dy)), fill=fill)

    def render(self):
        self.paint_sky()
        plots, roads = self.plan()
        self.paint_ground(plots, roads)
        for (i, j) in sorted(plots, key=lambda t: (t[0] + t[1], t[0])):
            f = plots[(i, j)]
            if f is None:
                if unit_hash(f'{i},{j}', 'tree') < 0.45:
                    self.paint_tree(i, j, f'{i},{j}')
            elif extension(f[0]) in DOC_EXTENSIONS:
                self.paint_tree(i, j, f[0])
            else:
                self.paint_building(i, j, f)
        return self.img


def render(data, width=1600, height=1600):
    small = City(data, width, height).render()
    palette_image = Image.new('P', (1, 1))
    flat = [c for rgb in PALETTE for c in rgb]
    palette_image.putpalette(flat + flat[:3] * (256 - len(PALETTE)))
    small = small.quantize(palette=palette_image, dither=Image.Dither.NONE).convert('RGB')
    return small.resize((small.width * PIXEL, small.height * PIXEL), Image.NEAREST)
