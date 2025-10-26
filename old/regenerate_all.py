#!/usr/bin/env python3
"""Regenerate all artworks in database with new aspect ratio detection"""

from models.artwork import Artwork
import requests
import time

def regenerate_all():
    artworks = Artwork.get_all()
    print(f"Found {len(artworks)} artworks in database\n")

    # Filter out test repos
    real_repos = [art for art in artworks if 'test/repo' not in art['repo_url']]

    print(f"Regenerating {len(real_repos)} real repositories:\n")

    for i, art in enumerate(real_repos, 1):
        repo_url = art['repo_url']
        repo_name = art['repo_name']

        print(f"[{i}/{len(real_repos)}] Regenerating {repo_name}...")
        print(f"    URL: {repo_url}")

        try:
            response = requests.post(
                'http://localhost:5000/generate',
                json={'github_url': repo_url},
                timeout=300  # 5 minute timeout for large repos
            )

            if response.status_code == 200:
                result = response.json()
                print(f"    Success! {result.get('message', 'Generated')}")
                if 'aspect_ratio' in result:
                    print(f"    Aspect ratio: {result['aspect_ratio']}")
            else:
                print(f"    Error: {response.status_code}")
                print(f"    {response.text[:200]}")

        except requests.exceptions.Timeout:
            print(f"    Timeout (repo too large or slow)")
        except Exception as e:
            print(f"    Error: {str(e)}")

        print()

        # Small delay between requests
        if i < len(real_repos):
            time.sleep(2)

    print("\nRegeneration complete!")

if __name__ == '__main__':
    regenerate_all()
