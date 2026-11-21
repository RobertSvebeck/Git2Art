"""Clone every repository in the artworks table and write its sculpture data.

Reads the database only; writes JSON files to static/generated/repodata/.
Usage: python scripts/make_repo_data.py [--overwrite]
"""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

from scene.repodata import repo_data_path  # noqa: E402
from services.git_service import cleanup_repo, clone_repo, extract_repo_name  # noqa: E402
from services.museum_service import REPO_DATA_SUBDIR, save_repo_data  # noqa: E402
from utils.db import get_db_cursor  # noqa: E402

DATA_DIR = os.path.join(ROOT, 'static', 'generated', REPO_DATA_SUBDIR)


def main():
    overwrite = '--overwrite' in sys.argv
    with get_db_cursor(commit=False) as cursor:
        cursor.execute('SELECT DISTINCT repo_url FROM artworks ORDER BY repo_url')
        urls = [row['repo_url'] for row in cursor.fetchall()]
    temp_dir = tempfile.mkdtemp(prefix='git2art_repodata_')
    done = failed = skipped = 0
    for index, url in enumerate(urls, 1):
        if not overwrite and os.path.exists(repo_data_path(DATA_DIR, url)):
            skipped += 1
            continue
        try:
            repo_path, _ = clone_repo(url, temp_dir)
        except Exception as e:
            print(f'[{index}/{len(urls)}] FAILED {url}: {e}')
            failed += 1
            continue
        try:
            if save_repo_data(repo_path, url, extract_repo_name(url), DATA_DIR):
                done += 1
                print(f'[{index}/{len(urls)}] {url}')
            else:
                failed += 1
        finally:
            cleanup_repo(repo_path)
    print(f'written {done}, skipped {skipped}, failed {failed}')


if __name__ == '__main__':
    main()
