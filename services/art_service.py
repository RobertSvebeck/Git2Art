"""Art generation service integrating with git2art.py."""

import os
import subprocess
import sys
from datetime import datetime
from services.git_service import clone_or_update_repo, extract_repo_name, cleanup_repo
from utils.watermark import add_watermark
from models.artwork import Artwork


def generate_art_from_github(github_url, temp_dir, images_dir, force=False, art_style='default'):
    """
    Generate artwork from a GitHub repository.

    Args:
        github_url: GitHub repository URL
        temp_dir: Temporary directory for cloning repos
        images_dir: Directory for generated images
        force: If True, bypass cache and force regeneration
        art_style: Art style to use ('default', 'minimalist', etc.)

    Returns:
        dict: Result with image_url, repo_name, artwork_id, and cached flag
    """
    # Clone or update repository
    repo_path, commit_hash, _ = clone_or_update_repo(github_url, temp_dir)
    repo_name = extract_repo_name(github_url)

    try:
        # Skip cache checks if force regeneration requested
        if not force:
            # Check database for cached art
            db_artwork = Artwork.get_by_repo_and_commit(github_url, commit_hash, art_style)
            if db_artwork:
                image_path = os.path.join(images_dir, db_artwork['image_filename'])
                if os.path.exists(image_path):
                    return {
                        'image_url': f'/static/generated/{db_artwork["image_filename"]}',
                        'repo_name': repo_name,
                        'artwork_id': db_artwork['id'],
                        'like_count': db_artwork['like_count'],
                        'art_style': art_style,
                        'cached': True
                    }

        # Generate new artwork
        output_filename = f'{repo_name}_{commit_hash[:8]}_{art_style}.png'
        output_path = os.path.join(images_dir, output_filename)

        # Get absolute path to git2art.py (should be in parent directory of services)
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        git2art_script = os.path.join(current_dir, 'git2art.py')

        # Run git2art.py on the cloned repository
        try:
            result = subprocess.run(
                [
                    sys.executable, git2art_script,
                    '--repo', repo_path,
                    '--output', output_path,
                    '--size', '1600',
                    '--aspect', 'auto',
                    '--style', art_style
                ],
                capture_output=True,
                text=True,
                check=True
            )
            # Log the output for debugging aspect ratio detection
            debug_log = os.path.join(images_dir, 'debug.log')
            with open(debug_log, 'a') as f:
                f.write(f"\n=== Generation for {repo_name} at {datetime.now()} ===\n")
                f.write(f"Command: python3 git2art.py --repo {repo_path} --output {output_path} --size 1600 --aspect auto\n")
                f.write("=== STDOUT ===\n")
                f.write(result.stdout)
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)
                f.write("\n")
        except subprocess.CalledProcessError as e:
            debug_log = os.path.join(images_dir, 'debug.log')
            with open(debug_log, 'a') as f:
                f.write(f"\n=== ERROR for {repo_name} at {datetime.now()} ===\n")
                f.write(f"stderr: {e.stderr}\n")
                f.write(f"stdout: {e.stdout}\n")
            raise Exception(f"Failed to generate artwork: {e.stderr}")

        # Add watermark
        add_watermark(output_path, github_url)

        # Save to database
        artwork_id = None
        try:
            relative_path = f'/static/generated/{output_filename}'
            artwork_id = Artwork.create(github_url, repo_name, commit_hash, relative_path, output_filename, art_style)
        except Exception as e:
            print(f"Warning: Failed to save to database: {e}")
            raise Exception(f"Database save failed: {e}")

        return {
            'image_url': f'/static/generated/{output_filename}',
            'repo_name': repo_name,
            'artwork_id': artwork_id,
            'like_count': 0,
            'art_style': art_style,
            'cached': False
        }
    finally:
        # Always cleanup the temporary repository
        cleanup_repo(repo_path)


def get_all_gallery_artworks(images_dir):
    """
    Load all generated artworks from database grouped by repository.

    Returns:
        list: List of artwork dicts with id, repo_name, image_url, commit_hash, created_at,
              like_count, scale, and versions list
    """
    artworks = []

    try:
        unique_repos = Artwork.get_unique_repos()
        for repo_info in unique_repos:
            repo_url = repo_info['repo_url']
            repo_name = repo_info['repo_name']
            version_count = repo_info['version_count']

            # Get the latest version for display
            latest = Artwork.get_latest_by_repo(repo_url)
            if not latest:
                continue

            # Get all versions for this repo
            versions = Artwork.get_versions_by_repo(repo_url)
            version_list = [
                {
                    'id': v['id'],
                    'commit_hash': v['commit_hash'],
                    'image_url': v['image_path'],
                    'image_filename': v['image_filename'],
                    'created_at': v['created_at'],
                    'created_at_formatted': v['created_at'].strftime('%b %d, %Y at %I:%M %p'),
                    'like_count': v['like_count']
                }
                for v in versions
            ]

            # Get art style display name
            art_style = latest.get('art_style', 'default')
            art_style_name = art_style.replace('_', ' ').title()

            scale = 1.0
            artworks.append({
                'id': latest['id'],
                'repo_name': repo_name,
                'repo_url': repo_url,
                'image_url': latest['image_path'],
                'image_filename': latest['image_filename'],
                'commit_hash': latest['commit_hash'],
                'art_style': art_style,
                'art_style_name': art_style_name,
                'created_at': latest['created_at'],
                'created_at_formatted': latest['created_at'].strftime('%b %d, %Y at %I:%M %p'),
                'like_count': latest['like_count'],
                'scale': scale,
                'version_count': version_count,
                'versions': version_list
            })

        return artworks
    except Exception as e:
        print(f"Error: Failed to fetch gallery artworks from database: {e}")
        return []
