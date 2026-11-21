"""Constellation renderer: draws a Scene, knows nothing about git."""

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SUPERSAMPLE = 2
GLOW_DOWNSCALE = 4
BACKGROUND_DARK = np.array([7, 9, 18], dtype=np.float32)
BACKGROUND_CENTRE = np.array([22, 26, 46], dtype=np.float32)
DUST_SEED = 7


@dataclass
class Star:
    x: float
    y: float
    radius: float
    colour: tuple
    alpha: float = 1.0
    flare: float = 0.0
    flash: float = 0.0


@dataclass
class Branch:
    x0: float
    y0: float
    x1: float
    y1: float
    weight: float
    colour: tuple
    bend: float
    alpha: float = 1.0


@dataclass
class Camera:
    cx: float
    cy: float
    scale: float


@dataclass
class Scene:
    stars: list
    branches: list
    tint: tuple
    caption: list = field(default_factory=list)


_background_cache = {}


def _background(width, height, tint):
    key = (width, height, tuple(int(c) // 8 for c in tint))
    if key in _background_cache:
        return _background_cache[key]
    ys, xs = np.mgrid[0:height, 0:width].astype(np.float32)
    nx = (xs - width / 2) / (width / 2)
    ny = (ys - height / 2) / (height / 2)
    falloff = np.clip(1.0 - np.sqrt(nx ** 2 * 0.7 + ny ** 2) / 1.35, 0, 1) ** 1.6
    centre = BACKGROUND_CENTRE * 0.8 + np.array(tint, dtype=np.float32) * 0.07
    pixels = BACKGROUND_DARK + (centre - BACKGROUND_DARK) * falloff[..., None]

    rng = np.random.default_rng(DUST_SEED)
    count = int(width * height / 900)
    dx = rng.integers(0, width, count)
    dy = rng.integers(0, height, count)
    brightness = rng.random(count) ** 3 * 70
    pixels[dy, dx] += brightness[:, None]

    image = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), 'RGB')
    if len(_background_cache) > 8:
        _background_cache.clear()
    _background_cache[key] = image
    return image


def _bezier(x0, y0, x1, y1, bend, segments=16):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    points = []
    for i in range(segments + 1):
        t = i / segments
        a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t ** 2
        points.append((a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1))
    return points


def _lighten(colour, amount):
    return tuple(int(c + (255 - c) * amount) for c in colour)


def _branch_polygon(points, start_width, end_width):
    left, right = [], []
    last = len(points) - 1
    for i, (x, y) in enumerate(points):
        ax, ay = points[max(i - 1, 0)]
        bx, by = points[min(i + 1, last)]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy) or 1.0
        half = (start_width + (end_width - start_width) * i / last) / 2
        nx, ny = -dy / length * half, dx / length * half
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return left + right[::-1]


def _draw_branches(draw, branches, to_px, unit_px):
    for branch in branches:
        width = branch.weight * unit_px
        alpha = int(255 * 0.30 * branch.alpha)
        if alpha <= 2 or width < 0.3:
            continue
        x0, y0 = to_px(branch.x0, branch.y0)
        x1, y1 = to_px(branch.x1, branch.y1)
        points = _bezier(x0, y0, x1, y1, branch.bend)
        if width < 1.5 * SUPERSAMPLE:
            draw.line(points, fill=branch.colour + (int(alpha * min(1.0, width)),), width=1)
        else:
            polygon = _branch_polygon(points, width, width * 0.55)
            draw.polygon(polygon, fill=branch.colour + (alpha,))


def _draw_stars(draw, stars, to_px, unit_px, min_radius):
    for star in sorted(stars, key=lambda s: -s.radius):
        if star.alpha <= 0.01:
            continue
        x, y = to_px(star.x, star.y)
        r = max(min_radius, star.radius * unit_px)
        a = star.alpha
        body = _lighten(star.colour, 0.35 * star.flash)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=body + (int(235 * a),))
        if r > 3 * SUPERSAMPLE:
            hr = r * 0.55
            hx, hy = x - r * 0.22, y - r * 0.22
            draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr),
                         fill=_lighten(star.colour, 0.45) + (int(110 * a),))
            cr = r * 0.18
            draw.ellipse((hx - cr, hy - cr, hx + cr, hy + cr), fill=(255, 255, 255, int(120 * a)))
        if star.flare > 0.02:
            ring = r + (3 + 10 * (1 - star.flare)) * SUPERSAMPLE
            draw.ellipse((x - ring, y - ring, x + ring, y + ring),
                         outline=_lighten(star.colour, 0.6) + (int(200 * star.flare * a),),
                         width=max(1, int(1.5 * SUPERSAMPLE)))


def _glow_layer(stars, width, height, to_px, unit_px):
    gw, gh = max(1, width // GLOW_DOWNSCALE), max(1, height // GLOW_DOWNSCALE)
    layer = Image.new('RGB', (gw, gh), (0, 0, 0))
    draw = ImageDraw.Draw(layer)
    factor = 1 / GLOW_DOWNSCALE
    for star in sorted(stars, key=lambda s: -s.radius):
        x, y = to_px(star.x, star.y)
        x, y = x * factor, y * factor
        body = max(1.0, star.radius * unit_px)
        r = (body * 1.35 + min(body, 40) * 0.5 + 6 * star.flare + 2) * factor
        strength = min(1.0, 0.45 * star.alpha + 0.6 * star.flare + 0.5 * star.flash)
        colour = tuple(int(c * strength) for c in _lighten(star.colour, 0.2))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=colour)
    blur = max(2, int(min(width, height) / 160))
    return layer.filter(ImageFilter.GaussianBlur(blur)).resize((width, height), Image.BILINEAR)


def _screen(base, layer):
    a = np.asarray(base, dtype=np.float32) / 255
    b = np.asarray(layer, dtype=np.float32) / 255
    return Image.fromarray(((1 - (1 - a) * (1 - b)) * 255).astype(np.uint8), 'RGB')


def _draw_caption(image, caption):
    if not caption:
        return
    draw = ImageDraw.Draw(image, 'RGBA')
    size = max(12, image.height // 34)
    font = ImageFont.load_default(size=size)
    small = ImageFont.load_default(size=int(size * 0.75))
    margin = int(size * 1.3)
    y = image.height - margin - int(size * 1.25) * (len(caption) - 1) - size
    for i, line in enumerate(caption):
        face = font if i == 0 else small
        colour = (235, 235, 245, 230) if i == 0 else (170, 175, 195, 210)
        draw.text((margin, y), line, font=face, fill=colour)
        y += int(size * 1.25)


def render(scene, camera, width, height):
    ss_w, ss_h = width * SUPERSAMPLE, height * SUPERSAMPLE

    def to_px_ss(x, y):
        return ((x - camera.cx) * camera.scale + width / 2) * SUPERSAMPLE, \
               ((y - camera.cy) * camera.scale + height / 2) * SUPERSAMPLE

    def to_px(x, y):
        return (x - camera.cx) * camera.scale + width / 2, (y - camera.cy) * camera.scale + height / 2

    canvas = _background(width, height, scene.tint).resize((ss_w, ss_h), Image.BILINEAR)
    draw = ImageDraw.Draw(canvas, 'RGBA')
    unit_ss = camera.scale * SUPERSAMPLE
    _draw_branches(draw, scene.branches, to_px_ss, unit_ss)
    _draw_stars(draw, scene.stars, to_px_ss, unit_ss, min_radius=1.1 * SUPERSAMPLE)
    image = canvas.resize((width, height), Image.LANCZOS)
    image = _screen(image, _glow_layer(scene.stars, width, height, to_px, camera.scale))
    _draw_caption(image, scene.caption)
    return image


def fit_camera(stars, width, height, margin=0.9, min_extent=0.75):
    """Frame the bounding box of the scene."""
    if not stars:
        return Camera(0.0, 0.0, min(width, height) / 2.5)
    xs = np.array([s.x for s in stars])
    ys = np.array([s.y for s in stars])
    radii = np.array([s.radius for s in stars])
    left, right = float(np.min(xs - radii)), float(np.max(xs + radii))
    top, bottom = float(np.min(ys - radii)), float(np.max(ys + radii))
    cx, cy = (left + right) / 2, (top + bottom) / 2
    ex = max((right - left) / 2 + 0.04, min_extent * width / max(width, height))
    ey = max((bottom - top) / 2 + 0.04, min_extent * height / max(width, height))
    scale = min(width * margin / (2 * ex), height * margin / (2 * ey))
    return Camera(cx, cy, scale)
