"""The people behind the repositories: owner, avatar and star counts.

Star counts come from the GitHub API and are cached in one small JSON file
(static/generated/repodata/github.json), so pages never wait on GitHub.
Without a token the API allows 60 requests an hour per IP, so counts are
refreshed one repository at a time: when it is painted, and by
scripts/refresh_github_info.py (stalest first, a few dozen per run).
Set GITHUB_TOKEN in .env to raise the limit to 5000 an hour.
"""

import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.request

INFO_FILENAME = 'github.json'
API_TIMEOUT_SECONDS = 5

_OWNER_REPO = re.compile(r'github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$')
_cache = {'path': None, 'mtime': None, 'data': {}}


def owner_and_repo(repo_url):
    match = _OWNER_REPO.search(repo_url or '')
    return (match.group(1), match.group(2)) if match else (None, None)


def repo_owner(repo_url):
    return owner_and_repo(repo_url)[0]


def avatar_url(owner, size=160):
    # avatars.githubusercontent.com sends CORS headers, so WebGL can use it
    return f'https://avatars.githubusercontent.com/{owner}?s={size}' if owner else None


def profile_url(owner):
    return f'https://github.com/{owner}' if owner else None


def info_path(data_dir):
    return os.path.join(data_dir, INFO_FILENAME)


def load_info(data_dir):
    """{repo_url: {'stars': int, 'fetched': unix time}}, cached by file mtime."""
    path = info_path(data_dir)
    if not os.path.exists(path):
        return {}
    mtime = os.path.getmtime(path)
    if _cache['path'] != path or _cache['mtime'] != mtime:
        try:
            with open(path, encoding='utf-8') as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            data = {}
        _cache.update(path=path, mtime=mtime, data=data)
    return _cache['data']


def _save_info(data_dir, data):
    os.makedirs(data_dir, exist_ok=True)
    handle, tmp = tempfile.mkstemp(dir=data_dir, suffix='.tmp')
    with os.fdopen(handle, 'w', encoding='utf-8') as out:
        json.dump(data, out, indent=0, sort_keys=True)
    os.replace(tmp, info_path(data_dir))


def fetch_stars(repo_url):
    """Star count from the GitHub API, or None if it cannot be had right now."""
    owner, repo = owner_and_repo(repo_url)
    if not owner:
        return None
    request = urllib.request.Request(
        f'https://api.github.com/repos/{owner}/{repo}',
        headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'git2art-museum'},
    )
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        request.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            return int(json.load(response).get('stargazers_count', 0))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def update_stars(data_dir, repo_url):
    """Fetch and store one repository's star count; never raises."""
    try:
        stars = fetch_stars(repo_url)
        if stars is None:
            return None
        data = dict(load_info(data_dir))
        data[repo_url] = {'stars': stars, 'fetched': int(time.time())}
        _save_info(data_dir, data)
        return stars
    except Exception as e:  # a missing star count must never break painting
        print(f'Warning: could not update stars for {repo_url}: {e}')
        return None


def stars_for(data_dir, repo_url):
    entry = load_info(data_dir).get(repo_url)
    return entry['stars'] if entry else None


def format_stars(stars):
    if not stars:
        return ''
    if stars >= 1000:
        return f'{stars / 1000:.1f}k'.replace('.0k', 'k')
    return str(stars)
