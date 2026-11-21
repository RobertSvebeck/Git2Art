"""Git repository operations and validation."""

import os
import re
import shutil
import subprocess
import tempfile

CLONE_TIMEOUT_SECONDS = 120


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
    name = url.strip().rstrip('/').split('/')[-1]
    return name[:-4] if name.endswith('.git') else name


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


def clone_repo(github_url, temp_dir):
    """
    Clone a repository into its own temporary folder.

    Blobless clone: full commit history (so commit and author counts are
    correct) but file contents are only downloaded for the checked-out HEAD.

    Returns:
        tuple: (repo_path, commit_hash)
    """
    repo_path = tempfile.mkdtemp(prefix=f'{extract_repo_name(github_url)}_', dir=temp_dir)
    try:
        subprocess.run(
            ['git', 'clone', '--filter=blob:none', '--single-branch', '--no-tags',
             github_url, repo_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=CLONE_TIMEOUT_SECONDS,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'},
        )
    except subprocess.TimeoutExpired:
        cleanup_repo(repo_path)
        raise Exception("Cloning took too long. The repository may be too large.")
    except subprocess.CalledProcessError as e:
        cleanup_repo(repo_path)
        error_msg = e.stderr

        if "could not read Username" in error_msg or "Authentication failed" in error_msg:
            raise Exception("This repository is private or requires authentication. Please use a public GitHub repository.")
        elif "not found" in error_msg.lower():
            raise Exception("Repository not found. Please check the URL and ensure the repository exists.")
        else:
            raise Exception(f"Failed to clone repository: {error_msg}")

    return repo_path, get_repo_commit_hash(repo_path)


def cleanup_repo(repo_path):
    """Remove temporary repository directory."""
    if os.path.exists(repo_path):
        try:
            shutil.rmtree(repo_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup repository at {repo_path}: {e}")
