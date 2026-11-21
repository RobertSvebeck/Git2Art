#!/usr/bin/env python3
"""
Git2Art: Repository-Driven Generative Art
Creates harmonious, organic art with color palettes derived from repository characteristics
Inspired by "Painting with Code" - IDEO

This is the CLI interface that uses the modular generator system.
"""

from generators import get_generator, list_available_styles, is_valid_style
from generators.base import BaseArtGenerator
import git
import re
from pathlib import Path


def main():
    """Main function"""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description='Generate harmonious generative art from a git repository'
    )
    parser.add_argument('--repo', default='.', help='Path to git repository')
    parser.add_argument('--output', default=None, help='Output image path (auto-generated if not specified)')
    parser.add_argument('--size', type=int, default=None,
                       help='Canvas width in pixels (default: 1600 for images, 1920 for --animate)')
    parser.add_argument('--aspect', default='auto',
                       choices=['auto', 'square', '16:10', '16:9', '3:2', '4:3', '5:4', 'portrait_3:4', 'portrait_2:3'],
                       help='Canvas aspect ratio (default: auto - detects based on repo type)')
    parser.add_argument('--style', default='expressionist',
                       help='Art style to use (expressionist, minimalist, etc.). Use --list-styles to see all available')
    parser.add_argument('--list-styles', action='store_true',
                       help='List all available art styles and exit')
    parser.add_argument('--animate', action='store_true',
                       help='Render the repository history as a video (constellation style; .mp4 or .gif)')
    parser.add_argument('--duration', type=float, default=None,
                       help='Animation length in seconds, excluding the final hold (default: scales with commit count)')
    parser.add_argument('--fps', type=int, default=30, help='Animation frames per second (default: 30)')
    parser.add_argument('--pace', default='commits', choices=['commits', 'time'],
                       help='Advance the animation evenly per commit or per calendar time (default: commits)')
    parser.add_argument('--no-caption', action='store_true', help='Omit the date and statistics caption')

    args = parser.parse_args()

    # List styles if requested
    if args.list_styles:
        print("Available art styles:")
        print()
        for style in list_available_styles():
            print(f"  {style['id']}: {style['name']}")
            print(f"    {style['description']}")
            print()
        return

    if args.animate:
        return animate(args)

    if args.size is None:
        args.size = 1600

    # Validate style
    if not is_valid_style(args.style):
        available = ', '.join([s['id'] for s in list_available_styles()])
        print(f"Error: Unknown style '{args.style}'. Available styles: {available}")
        print("Use --list-styles for more details.")
        return 1

    # Smart filename generation
    if args.output is None:
        # Get repo name from path
        repo = git.Repo(args.repo)
        repo_name = Path(args.repo).resolve().name

        # Sanitize repo name for filename
        sanitized_name = re.sub(r'[^\w\-]', '_', repo_name)

        # Get commit hash (short)
        try:
            commit_hash = repo.head.commit.hexsha[:7]
        except:
            commit_hash = "nocommit"

        # Get timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Calculate actual dimensions using temporary generator
        generator_temp = get_generator(
            style=args.style,
            repo_path=args.repo,
            width=args.size,
            aspect_ratio=args.aspect
        )
        width = generator_temp.width
        height = generator_temp.height

        # Build filename with timestamp and style for uniqueness
        # Format: RepoName_WIDTHxHEIGHT_STYLE_TIMESTAMP_commithash.png
        args.output = f"{sanitized_name}_{width}x{height}_{args.style}_{timestamp}_{commit_hash}.png"
        print(f"Auto-generated filename: {args.output}")

    # Create generator with selected style
    generator = get_generator(
        style=args.style,
        repo_path=args.repo,
        width=args.size,
        aspect_ratio=args.aspect
    )

    # Generate artwork
    generator.generate_art(args.output)


def animate(args):
    import subprocess
    import time
    from scene.animate import HistoryAnimator, write_video
    from scene.history import read_history

    aspect = '16:9' if args.aspect == 'auto' else args.aspect
    ratio_w, ratio_h = BaseArtGenerator.ASPECT_RATIOS[aspect]
    width = (args.size or 1920) // 2 * 2
    height = int(width * ratio_h / ratio_w) // 2 * 2

    repo_name = Path(args.repo).resolve().name
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    safe_name = re.sub(r'[^\w\-]', '_', repo_name)
    output = args.output or f"{safe_name}_{width}x{height}_history.mp4"

    started = time.time()
    try:
        commits = read_history(args.repo)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Error: could not read git history from '{args.repo}': {getattr(error, 'stderr', '') or error}")
        return 1
    if not commits:
        print(f"Error: '{args.repo}' has no commits to animate")
        return 1
    animator = HistoryAnimator(commits, width, height, fps=args.fps, duration=args.duration,
                               pace=args.pace, repo_name=repo_name)
    print(f"Animating {len(commits)} commits of {repo_name}: {animator.frame_count} frames "
          f"at {width}x{height}, {args.fps} fps")
    write_video(animator.frames(caption=not args.no_caption), output, width, height,
                args.fps, animator.frame_count)
    print(f"Saved {output} in {time.time() - started:.1f}s")


if __name__ == '__main__':
    exit(main() or 0)
