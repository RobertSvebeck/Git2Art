"""Render a repository-data style for every repository with a repodata file.

No cloning: works from static/generated/repodata/*.json. Each image is
watermarked, gets a museum WebP copy and an artworks row. A new row takes the
date the repository was first added, so a re-render does not make every
artwork of this style look brand new. --dry-run renders
into a temporary folder instead and touches neither static/generated nor the DB.

Usage: python scripts/render_data_style.py pixel_city [--dry-run] [--size 1600]
"""

import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

from generators.base import BaseArtGenerator  # noqa: E402
from services.git_service import extract_repo_name  # noqa: E402
from services.museum_service import REPO_DATA_SUBDIR, make_museum_image  # noqa: E402
from styles import DATA_STYLES  # noqa: E402
from utils.image_io import save_artwork  # noqa: E402
from utils.watermark import add_watermark  # noqa: E402

IMAGES_DIR = os.path.join(ROOT, 'static', 'generated')


def canvas_size(data, width):
    fingerprint = {'file_types': data.get('languages', {}), 'total_lines': data.get('total_bytes', 0)}
    ratio_w, ratio_h = BaseArtGenerator.ASPECT_RATIOS[BaseArtGenerator.detect_aspect_ratio(fingerprint)]
    return width, int(width * ratio_h / ratio_w)


def main():
    style = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    size = int(sys.argv[sys.argv.index('--size') + 1]) if '--size' in sys.argv else 1600
    render = DATA_STYLES[style]
    out_dir = tempfile.mkdtemp(prefix=f'git2art_{style}_') if dry_run else IMAGES_DIR
    first_added = {}
    if not dry_run:
        from models.artwork import Artwork
        from utils.db import get_db_cursor
        with get_db_cursor(commit=False) as cursor:
            cursor.execute('SELECT repo_url, MIN(created_at) AS first FROM artworks GROUP BY repo_url')
            first_added = {row['repo_url']: row['first'] for row in cursor.fetchall()}

    data_dir = os.path.join(IMAGES_DIR, REPO_DATA_SUBDIR)
    names = sorted(f for f in os.listdir(data_dir) if f.endswith('.json'))
    for index, name in enumerate(names, 1):
        with open(os.path.join(data_dir, name), encoding='utf-8') as handle:
            data = json.load(handle)
        repo_url, head = data['repo_url'], data['head']
        repo_name = extract_repo_name(repo_url)
        filename = f'{repo_name}_{head[:8]}_{style}.webp'
        started = time.time()
        width, height = canvas_size(data, size)
        save_artwork(render(data, width, height), os.path.join(out_dir, filename))
        add_watermark(os.path.join(out_dir, filename), repo_url)
        if not dry_run:
            make_museum_image(IMAGES_DIR, filename, overwrite=True)
            Artwork.create(repo_url, repo_name, head, f'/static/generated/{filename}', filename, style)
            if first_added.get(repo_url):
                with get_db_cursor(commit=True) as cursor:
                    cursor.execute('UPDATE artworks SET created_at = %s WHERE repo_url = %s AND commit_hash = %s'
                                   ' AND art_style = %s AND created_at > %s',
                                   (first_added[repo_url], repo_url, head, style, first_added[repo_url]))
        print(f'[{index}/{len(names)}] {repo_name} {width}x{height} {time.time() - started:.1f}s'
              + (' (dry run)' if dry_run else ''))
    if dry_run:
        print(f'Dry run images in {out_dir}')


if __name__ == '__main__':
    main()
