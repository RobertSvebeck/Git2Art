"""Artwork catalogue and web-sized images for the 3D museum."""

import json
import os

from PIL import Image

from scene.repodata import build_repo_data, repo_data_path, write_repo_data
from utils.db import get_db_cursor

MUSEUM_SUBDIR = 'museum'
REPO_DATA_SUBDIR = 'repodata'
MUSEUM_MAX_SIDE = 1024
MUSEUM_QUALITY = 82

_size_cache = {}


def museum_image_path(images_dir, image_filename):
    stem = os.path.splitext(image_filename)[0]
    return os.path.join(images_dir, MUSEUM_SUBDIR, f'{stem}.webp')


def make_museum_image(images_dir, image_filename, overwrite=False):
    """Write a downscaled WebP next to the original; returns its path or None."""
    source = os.path.join(images_dir, image_filename)
    target = museum_image_path(images_dir, image_filename)
    if not os.path.exists(source):
        return None
    if os.path.exists(target) and not overwrite:
        return target
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with Image.open(source) as image:
        image = image.convert('RGB')
        image.thumbnail((MUSEUM_MAX_SIDE, MUSEUM_MAX_SIDE), Image.LANCZOS)
        image.save(target, 'WEBP', quality=MUSEUM_QUALITY, method=6)
    return target


def save_repo_data(repo_path, repo_url, repo_name, data_dir):
    """Write the repo's sculpture data; never fails the caller."""
    try:
        return write_repo_data(data_dir, build_repo_data(repo_path, repo_url, repo_name))
    except Exception as e:
        print(f"Warning: Failed to save repo data for {repo_url}: {e}")
        return None


_commit_cache = {}


def _commit_count(data_file):
    if not os.path.exists(data_file):
        return 0
    mtime = os.path.getmtime(data_file)
    cached = _commit_cache.get(data_file)
    if cached and cached[0] == mtime:
        return cached[1]
    with open(data_file, encoding='utf-8') as handle:
        count = json.load(handle).get('commits', 0)
    _commit_cache[data_file] = (mtime, count)
    return count


def _image_size(path):
    mtime = os.path.getmtime(path)
    cached = _size_cache.get(path)
    if cached and cached[0] == mtime:
        return cached[1]
    with Image.open(path) as image:
        size = image.size
    _size_cache[path] = (mtime, size)
    return size


def get_museum_artworks(images_dir):
    """Latest artwork per (repository, style), skipping images missing on disk."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT a.id, a.repo_name, a.repo_url, a.art_style, a.image_filename, a.like_count, a.created_at
            FROM artworks a
            INNER JOIN (
                SELECT repo_url, art_style, MAX(created_at) AS max_created_at
                FROM artworks
                GROUP BY repo_url, art_style
            ) latest
            ON a.repo_url = latest.repo_url
            AND a.art_style = latest.art_style
            AND a.created_at = latest.max_created_at
            WHERE a.art_style IN (SELECT style_id FROM art_styles WHERE is_active = 1)
            ORDER BY a.id
        """)
        rows = cursor.fetchall()

    artworks = []
    for row in rows:
        original = os.path.join(images_dir, row['image_filename'])
        if not os.path.exists(original):
            continue
        museum = museum_image_path(images_dir, row['image_filename'])
        if os.path.exists(museum):
            url = f'/static/generated/{MUSEUM_SUBDIR}/{os.path.basename(museum)}'
        else:
            url = f'/static/generated/{row["image_filename"]}'
        width, height = _image_size(original)
        data_file = repo_data_path(os.path.join(images_dir, REPO_DATA_SUBDIR), row['repo_url'])
        artworks.append({
            'id': row['id'],
            'title': row['repo_name'],
            'repo_url': row['repo_url'],
            'style': row['art_style'],
            'likes': row['like_count'],
            'added': row['created_at'].isoformat() if row['created_at'] else '',
            'image': url,
            'aspect': round(width / height, 4),
            'data': f'/static/generated/{REPO_DATA_SUBDIR}/{os.path.basename(data_file)}'
                    if os.path.exists(data_file) else None,
            'commits': _commit_count(data_file),
        })
    return artworks
