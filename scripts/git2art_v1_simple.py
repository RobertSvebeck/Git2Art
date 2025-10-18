#!/usr/bin/env python3
"""
Git2Art: Turn your git repository into abstract art
Small changes = small visual changes, big changes = big visual changes
"""

import git
import hashlib
import numpy as np
from PIL import Image, ImageDraw
import os
from pathlib import Path
from collections import defaultdict


class GitArtGenerator:
    def __init__(self, repo_path='.', width=1200, height=1200):
        """Initialize the art generator with a git repository"""
        self.repo = git.Repo(repo_path)
        self.width = width
        self.height = height
        self.repo_path = Path(repo_path)

    def get_repo_fingerprint(self):
        """
        Generate a deterministic fingerprint of the current repo state.
        This ensures same code = same art, small changes = small art changes.
        """
        fingerprint_data = {
            'files': {},
            'total_lines': 0,
            'file_types': defaultdict(int),
            'commit_count': 0,
            'authors': set()
        }

        # Get current HEAD commit
        try:
            head_commit = self.repo.head.commit
            fingerprint_data['commit_count'] = len(list(self.repo.iter_commits()))
            fingerprint_data['authors'] = {c.author.name for c in self.repo.iter_commits()}
        except:
            # Empty repo or no commits yet
            pass

        # Analyze all tracked files
        try:
            for item in self.repo.tree().traverse():
                if item.type == 'blob':  # It's a file
                    file_path = item.path

                    # Skip binary files and common non-code files
                    if self._should_skip_file(file_path):
                        continue

                    # Get file content and analyze
                    try:
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        lines = content.split('\n')
                        line_count = len(lines)

                        # Get file extension
                        ext = Path(file_path).suffix or 'no_ext'
                        fingerprint_data['file_types'][ext] += line_count

                        # Create hash of file content
                        content_hash = hashlib.md5(content.encode()).hexdigest()

                        fingerprint_data['files'][file_path] = {
                            'lines': line_count,
                            'hash': content_hash,
                            'extension': ext
                        }
                        fingerprint_data['total_lines'] += line_count
                    except:
                        continue
        except:
            # No tracked files yet
            pass

        return fingerprint_data

    def _should_skip_file(self, file_path):
        """Determine if a file should be skipped"""
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
                          '.pdf', '.zip', '.tar', '.gz', '.bin', '.exe'}
        skip_names = {'package-lock.json', 'yarn.lock', '.gitattributes'}

        path = Path(file_path)
        return path.suffix in skip_extensions or path.name in skip_names

    def generate_art(self, output_path='repo_art.png'):
        """Generate abstract art based on repository fingerprint"""
        fingerprint = self.get_repo_fingerprint()

        # Create image
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)

        # Generate background gradient based on total lines and complexity
        img = self._create_background(fingerprint)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Draw elements based on files
        self._draw_file_elements(draw, fingerprint)

        # Draw commit history spiral
        self._draw_commit_spiral(draw, fingerprint)

        # Save the art
        img.save(output_path)
        print(f"Art generated: {output_path}")
        print(f"Based on: {len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines of code, "
              f"{fingerprint['commit_count']} commits")

        return output_path

    def _create_background(self, fingerprint):
        """Create a gradient background based on repo metrics"""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        # Use total lines to determine color scheme
        total_lines = fingerprint['total_lines']
        seed = total_lines % 360  # Hue rotation

        for y in range(self.height):
            for x in range(self.width):
                # Create gradient
                r = int((seed + x / self.width * 100) % 256)
                g = int((150 + y / self.height * 100) % 256)
                b = int((200 - (x + y) / (self.width + self.height) * 100) % 256)
                pixels[x, y] = (r, g, b)

        return img

    def _draw_file_elements(self, draw, fingerprint):
        """Draw geometric elements representing each file"""
        files = fingerprint['files']

        if not files:
            return

        # Create a deterministic layout
        num_files = len(files)
        grid_size = int(np.sqrt(num_files)) + 1
        cell_width = self.width // grid_size
        cell_height = self.height // grid_size

        for idx, (file_path, file_data) in enumerate(sorted(files.items())):
            # Position based on file name hash
            grid_x = idx % grid_size
            grid_y = idx // grid_size

            x = grid_x * cell_width + cell_width // 2
            y = grid_y * cell_height + cell_height // 2

            # Size based on line count
            size = min(cell_width, cell_height) * (file_data['lines'] / max(f['lines'] for f in files.values()))
            size = max(10, min(size, cell_width * 0.8))

            # Color based on file type and content hash
            color = self._hash_to_color(file_data['hash'])

            # Shape based on extension
            shape_type = hash(file_data['extension']) % 3

            if shape_type == 0:  # Circle
                draw.ellipse([x - size/2, y - size/2, x + size/2, y + size/2],
                           fill=color + (180,), outline=color)
            elif shape_type == 1:  # Rectangle
                draw.rectangle([x - size/2, y - size/2, x + size/2, y + size/2],
                             fill=color + (180,), outline=color)
            else:  # Triangle
                points = [
                    (x, y - size/2),
                    (x - size/2, y + size/2),
                    (x + size/2, y + size/2)
                ]
                draw.polygon(points, fill=color + (180,), outline=color)

    def _draw_commit_spiral(self, draw, fingerprint):
        """Draw a spiral pattern based on commit history"""
        commit_count = fingerprint['commit_count']

        if commit_count == 0:
            return

        # Draw spiral from center
        cx, cy = self.width // 2, self.height // 2
        angle = 0
        radius = 10

        for i in range(min(commit_count, 100)):  # Limit to 100 for performance
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)

            # Color changes with spiral
            color = self._hash_to_color(str(i))
            size = 5 + (i % 10)

            draw.ellipse([x - size, y - size, x + size, y + size],
                        fill=color + (150,))

            angle += 0.5
            radius += 2

    def _hash_to_color(self, text):
        """Convert a hash to a deterministic RGB color"""
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:6], 16)
        r = (hash_val >> 16) & 0xFF
        g = (hash_val >> 8) & 0xFF
        b = hash_val & 0xFF
        return (r, g, b)


def main():
    """Main function to generate art from current repository"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate abstract art from a git repository')
    parser.add_argument('--repo', default='.', help='Path to git repository (default: current directory)')
    parser.add_argument('--output', default='repo_art.png', help='Output image path')
    parser.add_argument('--size', type=int, default=1200, help='Image size (square)')

    args = parser.parse_args()

    generator = GitArtGenerator(args.repo, width=args.size, height=args.size)
    generator.generate_art(args.output)


if __name__ == '__main__':
    main()
