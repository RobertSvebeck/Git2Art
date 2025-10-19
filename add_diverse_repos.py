#!/usr/bin/env python3
"""Add 20 diverse repositories to showcase different languages and patterns"""

import requests
import time

# Diverse selection of repos across languages and types
REPOS = [
    # Python - backend (square)
    "https://github.com/pallets/flask",
    "https://github.com/psf/requests",
    "https://github.com/scrapy/scrapy",

    # JavaScript/Web - frontend (landscape)
    "https://github.com/expressjs/express",
    "https://github.com/vuejs/vue",
    "https://github.com/sveltejs/svelte",
    "https://github.com/jquery/jquery",

    # PHP - backend (square)
    "https://github.com/symfony/symfony",
    "https://github.com/laravel/framework",

    # Ruby - backend (square)
    "https://github.com/jekyll/jekyll",
    "https://github.com/sinatra/sinatra",

    # Go - systems (square)
    "https://github.com/gohugoio/hugo",
    "https://github.com/gin-gonic/gin",

    # Rust - systems (square)
    "https://github.com/actix/actix-web",

    # Java - enterprise (square)
    "https://github.com/spring-projects/spring-boot",

    # TypeScript/Web (landscape)
    "https://github.com/microsoft/TypeScript",
    "https://github.com/angular/angular",

    # Mobile - (portrait)
    "https://github.com/flutter/flutter",
    "https://github.com/ionic-team/ionic-framework",

    # Data Science - (square with data palette)
    "https://github.com/jupyter/notebook",
]

def add_repos():
    print(f"Adding {len(REPOS)} diverse repositories...\n")

    success_count = 0
    failed_repos = []

    for i, repo_url in enumerate(REPOS, 1):
        repo_name = repo_url.split('/')[-1]
        print(f"[{i}/{len(REPOS)}] Adding {repo_name}...")
        print(f"    URL: {repo_url}")

        try:
            response = requests.post(
                'http://localhost:5000/generate',
                json={'github_url': repo_url},
                timeout=180  # 3 minute timeout
            )

            if response.status_code == 200:
                result = response.json()
                print(f"    ✓ Success! {result.get('message', 'Generated')}")
                success_count += 1
            else:
                print(f"    ✗ Error: {response.status_code}")
                print(f"    {response.text[:200]}")
                failed_repos.append(repo_name)

        except requests.exceptions.Timeout:
            print(f"    ✗ Timeout (repo too large or slow)")
            failed_repos.append(f"{repo_name} (timeout)")
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            failed_repos.append(f"{repo_name} (error)")

        print()

        # Small delay between requests
        if i < len(REPOS):
            time.sleep(2)

    print(f"\n✅ Complete!")
    print(f"   Success: {success_count}/{len(REPOS)}")

    if failed_repos:
        print(f"\n⚠️  Failed repos:")
        for repo in failed_repos:
            print(f"   - {repo}")

if __name__ == '__main__':
    add_repos()
