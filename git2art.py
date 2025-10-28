#!/usr/bin/env python3
"""
Git2Art: Repository-Driven Generative Art
Creates harmonious, organic art with color palettes derived from repository characteristics
Inspired by "Painting with Code" - IDEO

This is the CLI interface that uses the modular generator system.
"""

from generators import get_generator, list_available_styles, is_valid_style
import git
from pathlib import Path


def main():
    """Main function"""
    import argparse
    import re
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description='Generate harmonious generative art from a git repository'
    )
    parser.add_argument('--repo', default='.', help='Path to git repository')
    parser.add_argument('--output', default=None, help='Output image path (auto-generated if not specified)')
    parser.add_argument('--size', type=int, default=1600, help='Canvas width in pixels')
    parser.add_argument('--aspect', default='auto',
                       choices=['auto', 'square', '16:10', '16:9', '3:2', '4:3', '5:4', 'portrait_3:4', 'portrait_2:3'],
                       help='Canvas aspect ratio (default: auto - detects based on repo type)')
    parser.add_argument('--contrast', default='high',
                       choices=['low', 'medium', 'high'],
                       help='Color contrast level: low (subtle), medium (balanced), high (dramatic). Default: high')
    parser.add_argument('--style', default='default',
                       help='Art style to use (default, minimalist, etc.). Use --list-styles to see all available')
    parser.add_argument('--list-styles', action='store_true',
                       help='List all available art styles and exit')

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
            aspect_ratio=args.aspect,
            contrast=args.contrast
        )
        width = generator_temp.width
        height = generator_temp.height

        # Build filename with timestamp and style for uniqueness
        # Format: RepoName_WIDTHxHEIGHT_STYLE_TIMESTAMP_commithash.png
        args.output = f"{sanitized_name}_{width}x{height}_{args.style}_{timestamp}_{commit_hash}.png"
        print(f"📝 Auto-generated filename: {args.output}")

    # Create generator with selected style
    generator = get_generator(
        style=args.style,
        repo_path=args.repo,
        width=args.size,
        aspect_ratio=args.aspect,
        contrast=args.contrast
    )

    # Generate artwork
    generator.generate_art(args.output)


if __name__ == '__main__':
    exit(main() or 0)
