"""Remove repositories from the collection: artworks rows (likes cascade), images,
museum WebP copies and repo data.

Previews by default; pass --yes to delete.
Usage: python scripts/remove_repo.py https://github.com/owner/repo [...] [--yes]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

from scene.repodata import repo_data_path  # noqa: E402
from services.museum_service import REPO_DATA_SUBDIR, museum_image_path  # noqa: E402
from utils.db import get_db_cursor  # noqa: E402

IMAGES_DIR = os.path.join(ROOT, 'static', 'generated')


def normalise(url):
    url = url.strip().rstrip('/')
    return url[:-4] if url.endswith('.git') else url


def main():
    confirm = '--yes' in sys.argv
    urls = [normalise(a) for a in sys.argv[1:] if not a.startswith('--')]
    if not urls:
        print(__doc__)
        return 1
    for url in urls:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute('SELECT id, art_style, image_filename, like_count FROM artworks WHERE repo_url IN (%s, %s)',
                           (url, f'{url}.git'))
            rows = cursor.fetchall()
        files = []
        for row in rows:
            files += [os.path.join(IMAGES_DIR, row['image_filename']), museum_image_path(IMAGES_DIR, row['image_filename'])]
        files.append(repo_data_path(os.path.join(IMAGES_DIR, REPO_DATA_SUBDIR), url))
        files = [f for f in files if os.path.exists(f)]
        likes = sum(row['like_count'] for row in rows)
        print(f'{url}: {len(rows)} artwork{"" if len(rows) == 1 else "s"} '
              f'({likes} like{"" if likes == 1 else "s"}), {len(files)} files')
        for row in rows:
            print(f'  artwork {row["id"]} {row["art_style"]} {row["image_filename"]}')
        if not confirm:
            continue
        with get_db_cursor(commit=True) as cursor:
            cursor.execute('DELETE FROM artworks WHERE repo_url IN (%s, %s)', (url, f'{url}.git'))
        for path in files:
            os.remove(path)
        print('  removed')
    if not confirm:
        print('\nPreview only. Run again with --yes to delete.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
