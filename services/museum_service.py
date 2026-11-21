"""Artwork catalogue and web-sized images for the 3D museum."""

import os

from PIL import Image

from utils.db import get_db_cursor

MUSEUM_SUBDIR = 'museum'
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
            SELECT a.id, a.repo_name, a.repo_url, a.art_style, a.image_filename, a.like_count
            FROM artworks a
            INNER JOIN (
                SELECT repo_url, art_style, MAX(created_at) AS max_created_at
                FROM artworks
                GROUP BY repo_url, art_style
            ) latest
            ON a.repo_url = latest.repo_url
            AND a.art_style = latest.art_style
            AND a.created_at = latest.max_created_at
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
        artworks.append({
            'id': row['id'],
            'title': row['repo_name'],
            'repo_url': row['repo_url'],
            'style': row['art_style'],
            'likes': row['like_count'],
            'image': url,
            'aspect': round(width / height, 4),
        })
    return artworks
