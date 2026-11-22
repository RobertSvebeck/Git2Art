"""Give re-rendered artworks back the date their repository was first added.

render_data_style.py inserted its rows with today's date, so the newest
artworks were simply the last style rendered (Tapestry). This sets
created_at for every row made on or after the rework (REWORK_START) to the
repository's first-added date from scripts/artwork_dates.csv. Rows older
than that keep their own date, so running it twice changes nothing.

Each style is a few seconds apart, in an order that rotates per repository,
so "newest first" lists mix the styles instead of repeating one.

Where the dates come from (column `source` in the CSV):
  database             earliest row that survived the cleanup (exact)
  local copy           an older image file synced before that row (exact enough)
  git commit           commit date of the oldest painted commit, found from old
                       image filenames; never before the launch on 2025-10-19
  git head (estimate)  nothing survived; the current head commit's date,
                       kept between 2025-10-30 and 2026-11-18

Usage: python scripts/restore_artwork_dates.py [--yes]
"""

import csv
import datetime
import os
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

from utils.db import get_db_cursor  # noqa: E402

REWORK_START = datetime.datetime(2026, 11, 21, 12, 0)
DATES_CSV = os.path.join(ROOT, 'scripts', 'artwork_dates.csv')


def main():
    confirm = '--yes' in sys.argv
    with open(DATES_CSV, newline='', encoding='utf-8') as handle:
        dates = {row['repo_url']: row for row in csv.DictReader(handle)}

    with get_db_cursor(commit=False) as cursor:
        cursor.execute('SELECT id, repo_url, repo_name, art_style FROM artworks WHERE created_at >= %s ORDER BY id',
                       (REWORK_START,))
        rows = cursor.fetchall()

    by_repo = {}
    for row in rows:
        by_repo.setdefault(row['repo_url'], []).append(row)
    updates, unknown = [], []
    for repo_url, repo_rows in sorted(by_repo.items()):
        entry = dates.get(repo_url)
        if not entry:
            unknown.append(repo_rows[0]['repo_name'])
            continue
        added = datetime.datetime.strptime(entry['added_at'], '%Y-%m-%d %H:%M:%S')
        styles = sorted({r['art_style'] for r in repo_rows})
        shift = zlib.crc32(repo_url.encode()) % len(styles)
        order = styles[shift:] + styles[:shift]
        for row in repo_rows:
            updates.append((added + datetime.timedelta(seconds=order.index(row['art_style'])), row['id']))
        print(f"{repo_rows[0]['repo_name'][:32]:32} {len(repo_rows)} rows -> {added:%Y-%m-%d %H:%M}  ({entry['source']})")

    print(f'\n{len(updates)} rows in {len(by_repo) - len(unknown)} repositories')
    if unknown:
        print('not in the CSV, left as they are: ' + ', '.join(unknown))
    if not confirm:
        print('\nPreview only. Run again with --yes to apply.')
        return 0
    with get_db_cursor(commit=True) as cursor:
        cursor.executemany('UPDATE artworks SET created_at = %s WHERE id = %s', updates)
    print('dates restored')
    return 0


if __name__ == '__main__':
    sys.exit(main())
