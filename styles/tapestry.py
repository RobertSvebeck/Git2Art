"""Tapestry: the repository's history woven as textile.

Warp threads (vertical) are grouped into bands, one per top-level folder,
dyed a muted shade of its language. Weft rows (horizontal) are moments in
history, top to bottom from the first commit to now; row thickness follows
how busy that period was. Where a folder grew at that time, the weft carries
the folder's colour in a twill weave; quiet periods weave in neutral wool.
"""

import colorsys
import math

import numpy as np
from PIL import Image, ImageDraw

from .common import districts, language_rgb, unit_hash

SUPERSAMPLE = 2
WALL = (34, 30, 28)


def tone(rgb, light, sat):
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    r, g, b = colorsys.hls_to_rgb(h, light, min(1.0, s * sat))
    return int(r * 255), int(g * 255), int(b * 255)


def shade(rgb, k):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)


def render(data, width=1600, height=1600):
    w, h = width * SUPERSAMPLE, height * SUPERSAMPLE
    image = Image.new('RGB', (w, h), WALL)
    draw = ImageDraw.Draw(image)
    files = data.get('files', [])
    timeline = data.get('timeline', [])
    if not files or not timeline:
        return image.resize((width, height), Image.LANCZOS)

    left, right = int(w * 0.1), int(w * 0.9)
    top, bottom = int(h * 0.09), int(h * 0.88)
    thread = max(6, int((right - left) / 110))
    columns = (right - left) // thread
    border = 3

    groups = districts(files, minimum=3, maximum=10)
    total = sum(sum(f[1] for f in g) for _, g in groups) or 1
    inner = columns - 2 * border
    bands, used = [], 0
    for index, (name, group) in enumerate(groups):
        share = sum(f[1] for f in group) / total
        count = max(3, round(share * inner)) if index < len(groups) - 1 else max(3, inner - used)
        bands.append((name, group, count))
        used += count
    scale = inner / max(1, used)

    commits = max(1, data.get('commits', 1))
    rows = len(timeline)
    births = []
    max_touches = max((f[3] for f in files), default=1)
    rows_index = np.arange(rows, dtype=np.float32)
    for name, group, _ in bands:
        activity = np.zeros(rows, dtype=np.float32)
        for f in group:
            born = min(rows - 1, int(f[2] / commits * rows))
            care = math.log1p(f[3]) / math.log1p(max_touches or 1)
            linger = rows * (0.03 + 0.25 * care)
            after = rows_index - born
            activity += np.where(after >= 0, np.exp(-np.maximum(after, 0) / linger) * (0.4 + care), 0)
        births.append(activity / (activity.max() or 1))

    busy = np.array([math.sqrt(c) for _, c in timeline], dtype=np.float32)
    heights = 0.35 + busy / (busy.max() or 1)
    heights = heights / heights.sum() * (bottom - top)

    langs = list(data.get('languages', {}))
    main = language_rgb(f'x{langs[0]}') if langs else (180, 160, 120)
    wool = tone(main, 0.82, 0.12)
    border_colour = tone(main, 0.32, 0.9)

    column_owner = []
    for b, (_, _, count) in enumerate(bands):
        column_owner += [b] * max(1, round(count * scale))
    column_owner = ([-1] * border + column_owner[:inner] + [-2] * border)
    while len(column_owner) < columns:
        column_owner.insert(-border, len(bands) - 1)

    band_colours = []
    for name, group, _ in bands:
        dominant = max(group, key=lambda f: f[1])[0]
        rgb = language_rgb(dominant)
        band_colours.append((tone(rgb, 0.32, 0.55), tone(rgb, 0.55, 1.15)))

    shadow = 18 * SUPERSAMPLE
    draw.rectangle((left + shadow // 2, top + shadow, right + shadow // 2, bottom + shadow), fill=(18, 16, 15))
    y = float(top)
    for r in range(rows):
        row_h = heights[r]
        y0, y1 = int(y), int(y + row_h)
        y += row_h
        if y1 <= y0:
            continue
        for c, owner in enumerate(column_owner):
            x0 = left + c * thread
            x1 = x0 + thread
            if owner < 0:
                diamond = abs((r % 8) - 4) + abs((c % border) - 1) < 3
                colour = border_colour if diamond else shade(border_colour, 0.6)
                weft_on_top = (r + c) % 2 == 0
            else:
                warp, vivid_colour = band_colours[owner]
                activity = births[owner][r]
                weft_on_top = (r + c) % 4 < 2 if activity > 0.05 else (r + c) % 4 == 0
                if weft_on_top and activity > 0.05:
                    mix = min(1.0, 0.25 + activity * 0.85)
                    colour = tuple(int(wv + (vv - wv) * mix) for wv, vv in zip(wool, vivid_colour))
                elif weft_on_top:
                    colour = shade(wool, 0.92 + 0.08 * unit_hash(f'{r}', 'wool'))
                else:
                    colour = warp
            draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=colour)
            if weft_on_top:
                mid = (y0 + y1) / 2
                draw.line((x0, mid, x1 - 1, mid), fill=shade(colour, 1.07), width=max(1, int((y1 - y0) * 0.25)))
                draw.line((x0, y1 - 1, x1 - 1, y1 - 1), fill=shade(colour, 0.82))
            else:
                mid = (x0 + x1) / 2
                draw.line((mid, y0, mid, y1 - 1), fill=shade(colour, 1.07), width=max(1, int(thread * 0.25)))
                draw.line((x1 - 1, y0, x1 - 1, y1 - 1), fill=shade(colour, 0.82))

    rod_y = top - 6 * SUPERSAMPLE
    draw.rectangle((left - 30 * SUPERSAMPLE, rod_y - 7 * SUPERSAMPLE, right + 30 * SUPERSAMPLE, rod_y + 7 * SUPERSAMPLE), fill=(92, 64, 40))
    draw.line((left - 30 * SUPERSAMPLE, rod_y - 3 * SUPERSAMPLE, right + 30 * SUPERSAMPLE, rod_y - 3 * SUPERSAMPLE), fill=(140, 104, 70), width=2 * SUPERSAMPLE)
    for c, owner in enumerate(column_owner):
        if c % 2:
            continue
        x = left + c * thread + thread // 2
        colour = border_colour if owner < 0 else band_colours[owner][0]
        length = h * (0.03 + 0.02 * unit_hash(f'{c}', 'fringe'))
        sway = (unit_hash(f'{c}', 'sway') - 0.5) * thread * 2
        draw.line((x, bottom, x + sway, bottom + length), fill=shade(colour, 1.1), width=max(2, thread // 3))
    return image.resize((width, height), Image.LANCZOS)
