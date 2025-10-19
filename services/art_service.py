"""Art generation service integrating with git2art.py."""

import os
import json
import subprocess
import glob
from datetime import datetime
from services.git_service import clone_or_update_repo, extract_repo_name
from utils.watermark import add_watermark
from models.artwork import Artwork


def get_cache_info_path(images_dir, repo_name):
    """Get path to cache info JSON file."""
    return os.path.join(images_dir, f'.{repo_name}_cache.json')


def get_cached_art_info(images_dir, repo_name, commit_hash):
    """
    Check if artwork exists for this repo/commit combination.

    Returns:
        dict or None: Cache info if exists and matches commit hash
    """
    cache_path = get_cache_info_path(images_dir, repo_name)

    if not os.path.exists(cache_path):
        return None

    try:
        with open(cache_path, 'r') as f:
            cache_info = json.load(f)

        if cache_info.get('commit_hash') == commit_hash:
            # Verify image file still exists
            image_path = os.path.join(images_dir, cache_info['filename'])
            if os.path.exists(image_path):
                return cache_info

    except (json.JSONDecodeError, KeyError):
        pass

    return None


def save_cache_info(images_dir, repo_name, commit_hash, filename):
    """Save cache information for generated artwork."""
    cache_path = get_cache_info_path(images_dir, repo_name)

    cache_info = {
        'commit_hash': commit_hash,
        'filename': filename,
        'repo_name': repo_name
    }

    with open(cache_path, 'w') as f:
        json.dump(cache_info, f, indent=2)


def generate_art_from_github(github_url, temp_dir, images_dir):
    """
    Generate artwork from a GitHub repository.

    Returns:
        dict: Result with image_url, repo_name, artwork_id, and cached flag
    """
    # Clone or update repository
    repo_path, commit_hash, _ = clone_or_update_repo(github_url, temp_dir)
    repo_name = extract_repo_name(github_url)

    # Check database first for cached art
    try:
        db_artwork = Artwork.get_by_repo_and_commit(github_url, commit_hash)
        if db_artwork:
            image_path = os.path.join(images_dir, db_artwork['image_filename'])
            if os.path.exists(image_path):
                return {
                    'image_url': f'/static/generated/{db_artwork["image_filename"]}',
                    'repo_name': repo_name,
                    'artwork_id': db_artwork['id'],
                    'like_count': db_artwork['like_count'],
                    'cached': True
                }
    except Exception:
        pass

    # Fallback: Check filesystem cache
    cache_info = get_cached_art_info(images_dir, repo_name, commit_hash)
    if cache_info:
        return {
            'image_url': f'/static/generated/{cache_info["filename"]}',
            'repo_name': repo_name,
            'artwork_id': None,
            'like_count': 0,
            'cached': True
        }

    # Generate new artwork
    output_filename = f'{repo_name}_{commit_hash[:8]}.png'
    output_path = os.path.join(images_dir, output_filename)

    # Get absolute path to git2art.py (should be in parent directory of services)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git2art_script = os.path.join(current_dir, 'git2art.py')

    # Run git2art.py on the cloned repository
    try:
        subprocess.run(
            [
                'python3', git2art_script,
                '--repo', repo_path,
                '--output', output_path,
                '--size', '1600',
                '--aspect', 'auto'
            ],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to generate artwork: {e.stderr}")

    # Add watermark
    add_watermark(output_path, github_url)

    # Save to database
    artwork_id = None
    try:
        relative_path = f'/static/generated/{output_filename}'
        artwork_id = Artwork.create(github_url, repo_name, commit_hash, relative_path, output_filename)
    except Exception as e:
        print(f"Warning: Failed to save to database: {e}")

    # Save filesystem cache as backup
    save_cache_info(images_dir, repo_name, commit_hash, output_filename)

    return {
        'image_url': f'/static/generated/{output_filename}',
        'repo_name': repo_name,
        'artwork_id': artwork_id,
        'like_count': 0,
        'cached': False
    }


def get_all_gallery_artworks(images_dir):
    """
    Load all generated artworks from database (with filesystem fallback).

    Returns:
        list: List of artwork dicts with id, repo_name, image_url, commit_hash, created_at, like_count
    """
    artworks = []

    # Try to fetch from database first
    try:
        db_artworks = Artwork.get_all(order_by='created_at', order_dir='DESC')
        for artwork in db_artworks:
            artworks.append({
                'id': artwork['id'],
                'repo_name': artwork['repo_name'],
                'image_url': artwork['image_path'],
                'commit_hash': artwork['commit_hash'],
                'created_at': artwork['created_at'],
                'created_at_formatted': artwork['created_at'].strftime('%b %d, %Y at %I:%M %p'),
                'like_count': artwork['like_count']
            })
        return artworks
    except Exception as e:
        print(f"Warning: Database fetch failed, falling back to filesystem: {e}")

    # Fallback: filesystem-based gallery
    if not os.path.exists(images_dir):
        return artworks

    cache_files = glob.glob(os.path.join(images_dir, '.*_cache.json'))

    for cache_path in cache_files:
        try:
            with open(cache_path, 'r') as f:
                cache_info = json.load(f)

            image_path = os.path.join(images_dir, cache_info['filename'])

            if os.path.exists(image_path):
                file_stat = os.stat(image_path)
                created_at = datetime.fromtimestamp(file_stat.st_mtime)

                artworks.append({
                    'id': None,
                    'repo_name': cache_info['repo_name'],
                    'image_url': f'/static/generated/{cache_info["filename"]}',
                    'commit_hash': cache_info['commit_hash'],
                    'created_at': created_at,
                    'created_at_formatted': created_at.strftime('%b %d, %Y at %I:%M %p'),
                    'like_count': 0
                })

        except (json.JSONDecodeError, KeyError, OSError):
            continue

    artworks.sort(key=lambda x: x['created_at'], reverse=True)

    return artworks
