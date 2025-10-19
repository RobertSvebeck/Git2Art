"""Art generation service integrating with git2art.py."""

import os
import json
import subprocess
from services.git_service import clone_or_update_repo, extract_repo_name
from utils.watermark import add_watermark


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
        dict: Result with image_url, repo_name, and cached flag
    """
    # Clone or update repository
    repo_path, commit_hash, _ = clone_or_update_repo(github_url, temp_dir)
    repo_name = extract_repo_name(github_url)

    # Check if we have cached art for this commit
    cache_info = get_cached_art_info(images_dir, repo_name, commit_hash)

    if cache_info:
        return {
            'image_url': f'/static/generated/{cache_info["filename"]}',
            'repo_name': repo_name,
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
                '--aspect', '4:3'
            ],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to generate artwork: {e.stderr}")

    # Add watermark
    add_watermark(output_path, github_url)

    # Save cache info
    save_cache_info(images_dir, repo_name, commit_hash, output_filename)

    return {
        'image_url': f'/static/generated/{output_filename}',
        'repo_name': repo_name,
        'cached': False
    }
