"""De Stijl: the repository as a Mondrian-style composition.

The canvas is divided by the folder tree: every division gives a folder (or a
large file) an area proportional to its bytes. Lines get thinner with depth.
Most fields stay white; the heaviest and the most-edited parts are painted in
primary colours chosen by language rank, and small config files become black.
"""

import math

import numpy as np
from PIL import Image, ImageDraw

from .common import DOC_EXTENSIONS, extension, unit_hash

SUPERSAMPLE = 2
MAX_DEPTH = 3
MIN_SHARE = 0.018
WHITE = (241, 238, 228)
OFF_WHITE = (232, 228, 216)
RED = (204, 32, 39)
BLUE = (22, 76, 156)
YELLOW = (244, 205, 58)
BLACK = (22, 21, 20)
GREY = (160, 158, 152)
PRIMARIES = [RED, BLUE, YELLOW]
CONFIG_EXTENSIONS = {'.json', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.lock', '.xml', ''}


class Node:
    def __init__(self, name, weight=0, path=None):
        self.name = name
        self.weight = weight
        self.path = path
        self.children = {}
        self.files = []

    def add(self, parts, size, touches, path):
        self.weight += size
        if len(parts) == 1:
            self.files.append((path, size, touches))
            return
        child = self.children.setdefault(parts[0], Node(parts[0]))
        child.add(parts[1:], size, touches, path)


def build_tree(files):
    root = Node('')
    for path, size, _born, touches in files:
        root.add(path.split('/'), max(size, 1), touches, path)
    return root


def leaf_items(node, total, depth, prefix):
    """Children of a node as (key, weight, payload) where payload is a Node or a file group."""
    items = []
    for name, child in node.children.items():
        key = f'{prefix}{name}/'
        if depth >= MAX_DEPTH or child.weight / total < MIN_SHARE * 3:
            items.append((key, child.weight, ('leaf', collect(child))))
        else:
            items.append((key, child.weight, ('node', child)))
    big = [f for f in node.files if f[1] / total >= MIN_SHARE * 2]
    small = [f for f in node.files if f[1] / total < MIN_SHARE * 2]
    for f in big:
        items.append((f[0], f[1], ('leaf', [f])))
    if small:
        items.append((f'{prefix}*', sum(f[1] for f in small), ('leaf', small)))
    return [item for item in items if item[1] > 0]


def collect(node):
    files = list(node.files)
    for child in node.children.values():
        files.extend(collect(child))
    return files


def split(rect, items, depth, leaves, lines):
    """Binary slice layout. rect = (x0, y0, x1, y1) in 0..1 canvas units."""
    x0, y0, x1, y1 = rect
    if len(items) == 1:
        key, weight, (kind, payload) = items[0]
        if kind == 'node':
            subdivide(rect, payload, depth + 1, key, leaves, lines)
        else:
            leaves.append((rect, key, payload, depth))
        return
    total = sum(w for _, w, _ in items)
    running, cut = 0, 1
    for i, (_, w, _) in enumerate(items[:-1]):
        running += w
        cut = i + 1
        if running >= total / 2:
            break
    share = sum(w for _, w, _ in items[:cut]) / total
    if (x1 - x0) >= (y1 - y0):
        xm = x0 + (x1 - x0) * share
        lines.append(((xm, y0, xm, y1), depth))
        split((x0, y0, xm, y1), items[:cut], depth, leaves, lines)
        split((xm, y0, x1, y1), items[cut:], depth, leaves, lines)
    else:
        ym = y0 + (y1 - y0) * share
        lines.append(((x0, ym, x1, ym), depth))
        split((x0, y0, x1, ym), items[:cut], depth, leaves, lines)
        split((x0, ym, x1, y1), items[cut:], depth, leaves, lines)


def subdivide(rect, node, depth, prefix, leaves, lines, total=None):
    total = total or subdivide.total
    items = leaf_items(node, total, depth, prefix)
    items.sort(key=lambda item: unit_hash(item[0], 'order'))
    if not items:
        return
    split(rect, items, depth, leaves, lines)


def language_ranks(data):
    order = [ext for ext in data.get('languages', {}) if ext not in DOC_EXTENSIONS and ext not in CONFIG_EXTENSIONS]
    return {ext: i for i, ext in enumerate(order[:3])}


def dominant_extension(files):
    weights = {}
    for path, size, _ in files:
        weights[extension(path)] = weights.get(extension(path), 0) + size
    return max(weights, key=weights.get) if weights else ''


def choose_colours(leaves, data):
    ranks = language_ranks(data)
    total = sum(sum(f[1] for f in payload) for _, _, payload, _ in leaves) or 1
    heat = []
    for rect, key, payload, _ in leaves:
        touches = sum(f[2] for f in payload)
        size = sum(f[1] for f in payload)
        heat.append(touches / max(1, math.sqrt(size)))
    hot_cut = sorted(heat, reverse=True)[max(0, len(heat) // 6)] if heat else 0
    by_weight = sorted(range(len(leaves)), key=lambda i: -sum(f[1] for f in leaves[i][2]))
    heaviest = set(by_weight[:3])
    colours = []
    for i, (rect, key, payload, _) in enumerate(leaves):
        ext = dominant_extension(payload)
        share = sum(f[1] for f in payload) / total
        area = (rect[2] - rect[0]) * (rect[3] - rect[1])
        if ext in DOC_EXTENSIONS:
            colour = OFF_WHITE if unit_hash(key, 'doc') < 0.5 else WHITE
        elif ext in CONFIG_EXTENSIONS and area < 0.01:
            colour = BLACK
        elif ext in ranks and (i in heaviest or heat[i] >= hot_cut) and area > 0.004:
            colour = PRIMARIES[ranks[ext]]
        elif share < 0.004 and unit_hash(key, 'grey') < 0.25:
            colour = GREY
        else:
            colour = WHITE
        colours.append(colour)
    used = set(colours)
    for primary_index, primary in enumerate(PRIMARIES):
        if primary in used:
            continue
        candidates = [i for i in by_weight if colours[i] == WHITE
                      and ranks.get(dominant_extension(leaves[i][2])) == primary_index]
        if candidates:
            colours[candidates[0]] = primary
    return colours


def paint_texture(image, seed):
    pixels = np.asarray(image, dtype=np.float32)
    h, w, _ = pixels.shape
    rng = np.random.default_rng(int(unit_hash(seed, 'grain') * 2 ** 32))
    grain = rng.normal(0, 2.4, (h, w, 1))
    low = rng.normal(0, 1, (h // 64 + 2, w // 64 + 2)).astype(np.float32)
    low = np.asarray(Image.fromarray(low).resize((w, h), Image.BICUBIC))[..., None] * 1.4
    return Image.fromarray(np.clip(pixels + grain + low, 0, 255).astype(np.uint8), 'RGB')


def render(data, width=1600, height=1600):
    files = data.get('files', [])
    w, h = width * SUPERSAMPLE, height * SUPERSAMPLE
    image = Image.new('RGB', (w, h), WHITE)
    draw = ImageDraw.Draw(image)
    if not files:
        return image.resize((width, height), Image.LANCZOS)

    root = build_tree(files)
    subdivide.total = root.weight
    leaves, lines = [], []
    subdivide((0, 0, 1, 1), root, 0, '', leaves, lines)
    colours = choose_colours(leaves, data)

    for ((x0, y0, x1, y1), _, _, _), colour in zip(leaves, colours):
        draw.rectangle((x0 * w, y0 * h, x1 * w, y1 * h), fill=colour)

    unit = min(w, h)
    for (x0, y0, x1, y1), depth in sorted(lines, key=lambda line: -line[1]):
        thickness = max(2, unit * (0.022 * 0.62 ** depth))
        if x0 == x1:
            draw.rectangle((x0 * w - thickness / 2, y0 * h, x0 * w + thickness / 2, y1 * h), fill=BLACK)
        else:
            draw.rectangle((x0 * w, y0 * h - thickness / 2, x1 * w, y0 * h + thickness / 2), fill=BLACK)

    image = paint_texture(image, data.get('name', ''))
    return image.resize((width, height), Image.LANCZOS)
