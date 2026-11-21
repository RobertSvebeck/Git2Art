"""Free disk space taken by artworks nobody can see any more.

Categories (orphans always; the others only when asked for):
  orphans       image files in static/generated (and museum/ copies) with no
                artworks row; files only, the database is not touched
  --superseded  older commits of the same repository and style, unless liked
  --retired     artworks of styles that are inactive in art_styles

Previews by default; pass --yes to delete. Run it on the server: the files
live there, and the database rows it deletes are shared by every machine.

Usage: python scripts/cleanup_artworks.py [--superseded] [--retired] [--yes]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

from services.museum_service import MUSEUM_SUBDIR, museum_image_path  # noqa: E402
from utils.db import get_db_cursor  # noqa: E402

IMAGES_DIR = os.path.join(ROOT, 'static', 'generated')
IMAGE_EXTENSIONS = ('.png', '.webp', '.jpg', '.jpeg')


def size_of(paths):
    return sum(os.path.getsize(p) for p in paths if os.path.exists(p))


def files_for(rows):
    paths = []
    for row in rows:
        paths.append(os.path.join(IMAGES_DIR, row['image_filename']))
        paths.append(museum_image_path(IMAGES_DIR, row['image_filename']))
    return [p for p in paths if os.path.exists(p)]


def find_orphans(referenced):
    stems = {os.path.splitext(name)[0] for name in referenced}
    orphans = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR)
               if f.lower().endswith(IMAGE_EXTENSIONS) and f not in referenced]
    museum_dir = os.path.join(IMAGES_DIR, MUSEUM_SUBDIR)
    if os.path.isdir(museum_dir):
        orphans += [os.path.join(museum_dir, f) for f in os.listdir(museum_dir)
                    if f.lower().endswith('.webp') and os.path.splitext(f)[0] not in stems]
    return orphans


def superseded_rows():
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT a.id, a.image_filename, a.repo_url, a.art_style FROM artworks a
            JOIN (SELECT repo_url, art_style, MAX(created_at) AS latest FROM artworks GROUP BY repo_url, art_style) l
              ON a.repo_url = l.repo_url AND a.art_style = l.art_style AND a.created_at < l.latest
            WHERE a.like_count = 0
        """)
        return cursor.fetchall()


def retired_rows():
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT id, image_filename, repo_url, art_style FROM artworks
            WHERE art_style IN (SELECT style_id FROM art_styles WHERE is_active = 0)
        """)
        return cursor.fetchall()


def delete_rows(rows):
    ids = [row['id'] for row in rows]
    for start in range(0, len(ids), 200):
        chunk = ids[start:start + 200]
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(f"DELETE FROM artworks WHERE id IN ({', '.join(['%s'] * len(chunk))})", chunk)


def main():
    confirm = '--yes' in sys.argv
    print(f"Database: {os.environ.get('DB_HOST', '?')}/{os.environ.get('DB_NAME', '?')}   Images: {IMAGES_DIR}\n")
    with get_db_cursor(commit=False) as cursor:
        cursor.execute('SELECT image_filename FROM artworks')
        referenced = {row['image_filename'] for row in cursor.fetchall()}

    plan = []
    orphans = find_orphans(referenced)
    plan.append(('orphan files', [], orphans))
    if '--superseded' in sys.argv:
        rows = superseded_rows()
        plan.append(('superseded versions', rows, files_for(rows)))
    if '--retired' in sys.argv:
        rows = retired_rows()
        plan.append(('retired-style artworks', rows, files_for(rows)))

    seen = set()
    for label, rows, paths in plan:
        unique = [p for p in paths if p not in seen]
        seen.update(unique)
        rows_text = f'{len(rows)} rows, ' if rows else ''
        print(f'{label:24} {rows_text}{len(unique)} files, {size_of(unique) / 1e6:.1f} MB')
    if not confirm:
        print('\nPreview only. Run again with --yes to delete.')
        return 0

    for label, rows, paths in plan:
        if rows:
            delete_rows(rows)
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
        print(f'removed {label}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
