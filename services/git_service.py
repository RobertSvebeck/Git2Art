"""Git repository operations and validation."""

import subprocess
import os
import re


def validate_github_url(url):
    """
    Validate GitHub URL format.

    Returns:
        tuple: (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    # Support both HTTPS and git@ formats
    patterns = [
        r'^https://github\.com/[\w-]+/[\w.-]+/?$',
        r'^git@github\.com:[\w-]+/[\w.-]+\.git$'
    ]

    if not any(re.match(pattern, url.strip()) for pattern in patterns):
        return False, "Invalid GitHub URL format. Expected: https://github.com/owner/repo"

    return True, None


def extract_repo_name(url):
    """Extract repository name from GitHub URL."""
    # Remove trailing slash and .git
    url = url.rstrip('/').replace('.git', '')

    # Extract repo name (last part of URL)
    return url.split('/')[-1]


def get_repo_commit_hash(repo_path):
    """Get the current commit hash of a repository."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def clone_or_update_repo(github_url, temp_dir):
    """
    Clone a repository or update it if it already exists.

    Returns:
        tuple: (repo_path, commit_hash, was_cached)
    """
    repo_name = extract_repo_name(github_url)
    repo_path = os.path.join(temp_dir, repo_name)

    if os.path.exists(repo_path):
        # Repository exists, try to update it
        try:
            subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ['git', 'reset', '--hard', 'origin/HEAD'],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
            commit_hash = get_repo_commit_hash(repo_path)
            return repo_path, commit_hash, True
        except subprocess.CalledProcessError:
            # If update fails, remove and re-clone
            import shutil
            shutil.rmtree(repo_path)

    # Clone fresh repository
    try:
        subprocess.run(
            ['git', 'clone', '--depth', '1', github_url, repo_path],
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = get_repo_commit_hash(repo_path)
        return repo_path, commit_hash, False
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository: {e.stderr}")


def cleanup_repo(repo_path):
    """Remove temporary repository directory."""
    import shutil
    if os.path.exists(repo_path):
        try:
            shutil.rmtree(repo_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup repository at {repo_path}: {e}")
