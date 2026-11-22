"""Refresh GitHub star counts for the museum, stalest first.

Reads the database only; writes static/generated/repodata/github.json.
Without GITHUB_TOKEN in .env GitHub allows 60 requests an hour, so the
default is 40 per run: run it from cron every hour or two to keep all
counts fresh, or once with a token and --limit 1000.

Usage: python scripts/refresh_github_info.py [--limit 40]
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

from services.github_info import load_info, update_stars  # noqa: E402
from services.museum_service import REPO_DATA_SUBDIR  # noqa: E402
from utils.db import get_db_cursor  # noqa: E402

DATA_DIR = os.path.join(ROOT, 'static', 'generated', REPO_DATA_SUBDIR)


def main():
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 40
    with get_db_cursor(commit=False) as cursor:
        cursor.execute('SELECT DISTINCT repo_url FROM artworks')
        urls = [row['repo_url'] for row in cursor.fetchall()]
    info = load_info(DATA_DIR)
    urls.sort(key=lambda url: info.get(url, {}).get('fetched', 0))
    done = failed = 0
    for url in urls[:limit]:
        stars = update_stars(DATA_DIR, url)
        if stars is None:
            failed += 1
            print(f'no answer   {url}')
            if failed >= 3 and done == 0:
                print('GitHub is not answering (rate limit?); try again later')
                break
        else:
            done += 1
            print(f'{stars:>8}    {url}')
        time.sleep(0.5)
    print(f'\n{done} updated, {failed} failed, {len(urls)} repositories in all')
    return 0


if __name__ == '__main__':
    sys.exit(main())
