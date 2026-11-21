"""Render a data style for a fixed sample of repositories into one contact sheet.

Usage: python scripts/style_lab.py pixel_city [output.png] [--size 800]
"""

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw  # noqa: E402

from styles import DATA_STYLES  # noqa: E402

DATA_DIR = os.path.join(ROOT, 'static', 'generated', 'repodata')
SAMPLE = [
    'hugoocoto__flag.h', 'fc-io__pp1', 'public-apis__public-apis', 'RobertSvebeck__Git2Art',
    'pallets__flask', 'FacundoPiriz17__Obligatorio_BDII', 'athatheo__bobe', 'sveltejs__svelte',
]


def main():
    style = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else f'{style}_lab.png'
    size = int(sys.argv[sys.argv.index('--size') + 1]) if '--size' in sys.argv else 800
    render = DATA_STYLES[style]
    tiles = []
    for slug in SAMPLE:
        with open(os.path.join(DATA_DIR, f'{slug}.json'), encoding='utf-8') as handle:
            data = json.load(handle)
        started = time.time()
        image = render(data, size, size)
        print(f'{slug}: {time.time() - started:.2f}s, {data["total_files"]} files')
        tiles.append((slug.split('__')[1], image))
    cols = 4
    sheet = Image.new('RGB', (cols * size, (len(tiles) + cols - 1) // cols * (size + 28)), 'white')
    draw = ImageDraw.Draw(sheet)
    for k, (label, image) in enumerate(tiles):
        x, y = (k % cols) * size, (k // cols) * (size + 28)
        sheet.paste(image, (x, y + 28))
        draw.text((x + 8, y + 7), label, fill='black')
    sheet.save(output)
    print(f'saved {output}')


if __name__ == '__main__':
    main()
