"""Art generation service integrating with git2art.py."""

import os
import subprocess
import sys
from datetime import datetime
from services.git_service import clone_or_update_repo, extract_repo_name, cleanup_repo
from utils.watermark import add_watermark
from models.artwork import Artwork


def generate_art_from_github(github_url, temp_dir, images_dir, force=False, art_style='expressionist'):
    """
    Generate artwork from a GitHub repository.

    Args:
        github_url: GitHub repository URL
        temp_dir: Temporary directory for cloning repos
        images_dir: Directory for generated images
        force: If True, bypass cache and force regeneration
        art_style: Art style to use ('expressionist', 'minimalist', etc.)

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


def get_all_gallery_artworks(images_dir, page=1, per_page=30, art_style=None, search_query=None):
    """
    Load gallery artworks with pagination, optional style filtering, and search.

    Args:
        images_dir: Directory for generated images
        page: Page number (1-indexed)
        per_page: Number of artworks per page
        art_style: Optional filter by art style
        search_query: Optional search by repo name or commit hash

    Returns:
        dict: {
            'artworks': list of artwork dicts,
            'total': total count matching filters,
            'page': current page,
            'per_page': artworks per page,
            'total_pages': total number of pages
        }
    """
    artworks = []

    try:
        offset = (page - 1) * per_page

        # Get paginated artworks with optional filters
        from utils.db import get_db_cursor

        # Build WHERE clause for filters
        where_clauses = []
        params = []

        if art_style:
            where_clauses.append("a.art_style = %s")
            params.append(art_style)

        if search_query:
            where_clauses.append("(a.repo_name LIKE %s OR a.commit_hash LIKE %s)")
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term])

        where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Get total count matching filters
        with get_db_cursor(commit=False) as cursor:
            count_query = f"""
                SELECT COUNT(DISTINCT a.repo_url, a.art_style) as total
                FROM artworks a
                INNER JOIN (
                    SELECT repo_url, art_style, MAX(created_at) as max_created_at
                    FROM artworks
                    {where_clause}
                    GROUP BY repo_url, art_style
                ) latest
                ON a.repo_url = latest.repo_url
                AND a.art_style = latest.art_style
                AND a.created_at = latest.max_created_at
            """
            cursor.execute(count_query, params)
            result = cursor.fetchone()
            total_count = result['total'] if result else 0

        # Get paginated artworks
        with get_db_cursor(commit=False) as cursor:
            query = f"""
                SELECT
                    a.*,
                    (SELECT COUNT(*) FROM artworks WHERE repo_url = a.repo_url AND art_style = a.art_style) as version_count
                FROM artworks a
                INNER JOIN (
                    SELECT repo_url, art_style, MAX(created_at) as max_created_at
                    FROM artworks
                    {where_clause}
                    GROUP BY repo_url, art_style
                ) latest
                ON a.repo_url = latest.repo_url
                AND a.art_style = latest.art_style
                AND a.created_at = latest.max_created_at
                ORDER BY a.created_at DESC
                LIMIT {int(per_page)}
                OFFSET {int(offset)}
            """
            cursor.execute(query, params)
            paginated_artworks = cursor.fetchall()

        for artwork in paginated_artworks:
            repo_url = artwork['repo_url']
            repo_name = artwork['repo_name']
            art_style_val = artwork.get('art_style', 'expressionist')
            version_count = artwork.get('version_count', 1)

            # Get art style display name
            art_style_name = art_style_val.replace('_', ' ').title()

            scale = 1.0
            artworks.append({
                'id': artwork['id'],
                'repo_name': repo_name,
                'repo_url': repo_url,
                'image_url': artwork['image_path'],
                'image_filename': artwork['image_filename'],
                'commit_hash': artwork['commit_hash'],
                'art_style': art_style_val,
                'art_style_name': art_style_name,
                'created_at': artwork['created_at'],
                'created_at_formatted': artwork['created_at'].strftime('%b %d, %Y at %I:%M %p'),
                'like_count': artwork['like_count'],
                'scale': scale,
                'version_count': version_count,
                'versions': []
            })

        total_pages = (total_count + per_page - 1) // per_page

        return {
            'artworks': artworks,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
    except Exception as e:
        print(f"Error: Failed to fetch gallery artworks from database: {e}")
        import traceback
        traceback.print_exc()
        return {
            'artworks': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0
        }
