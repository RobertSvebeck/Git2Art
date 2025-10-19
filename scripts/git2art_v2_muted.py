#!/usr/bin/env python3
"""
Git2Art v2: Art Theory Enhanced
Incorporates principles of abstract art composition, color theory, and visual harmony
"""

import git
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import colorsys
from pathlib import Path
from collections import defaultdict
import math


class ColorTheory:
    """Color theory utilities for creating harmonious palettes"""

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convert HSV to RGB (0-255)"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def create_analogous_palette(base_hue, count=5):
        """Create analogous color scheme (colors next to each other on color wheel)"""
        colors = []
        spread = 30  # degrees on color wheel
        for i in range(count):
            offset = (i - count//2) * spread / 360
            h = (base_hue + offset) % 1.0
            s = 0.6 + (i % 2) * 0.2  # Vary saturation
            v = 0.7 + (i % 3) * 0.1  # Vary value
            colors.append(ColorTheory.hsv_to_rgb(h, s, v))
        return colors

    @staticmethod
    def create_complementary_palette(base_hue):
        """Create complementary color scheme (opposite colors)"""
        colors = []
        # Base color
        colors.append(ColorTheory.hsv_to_rgb(base_hue, 0.7, 0.8))
        # Complement (180 degrees opposite)
        colors.append(ColorTheory.hsv_to_rgb((base_hue + 0.5) % 1.0, 0.7, 0.8))
        # Add tints and shades for variation
        colors.append(ColorTheory.hsv_to_rgb(base_hue, 0.4, 0.9))
        colors.append(ColorTheory.hsv_to_rgb((base_hue + 0.5) % 1.0, 0.4, 0.9))
        return colors

    @staticmethod
    def create_triadic_palette(base_hue):
        """Create triadic color scheme (3 colors evenly spaced)"""
        colors = []
        for i in range(3):
            h = (base_hue + i * (1/3)) % 1.0
            s = 0.65 + (i * 0.1)
            v = 0.75 + (i * 0.1)
            colors.append(ColorTheory.hsv_to_rgb(h, s, v))
        return colors


class Composition:
    """Composition and layout utilities"""

    GOLDEN_RATIO = 1.618033988749895

    @staticmethod
    def golden_points(width, height):
        """Calculate golden ratio points for focal areas"""
        return [
            (int(width / Composition.GOLDEN_RATIO), int(height / Composition.GOLDEN_RATIO)),
            (int(width - width / Composition.GOLDEN_RATIO), int(height / Composition.GOLDEN_RATIO)),
            (int(width / Composition.GOLDEN_RATIO), int(height - height / Composition.GOLDEN_RATIO)),
            (int(width - width / Composition.GOLDEN_RATIO), int(height - height / Composition.GOLDEN_RATIO)),
        ]

    @staticmethod
    def rule_of_thirds_points(width, height):
        """Calculate rule of thirds intersection points"""
        return [
            (int(width * 1/3), int(height * 1/3)),
            (int(width * 2/3), int(height * 1/3)),
            (int(width * 1/3), int(height * 2/3)),
            (int(width * 2/3), int(height * 2/3)),
        ]

    @staticmethod
    def fibonacci_spiral_points(width, height, steps=50):
        """Generate points along a fibonacci spiral"""
        points = []
        phi = Composition.GOLDEN_RATIO
        cx, cy = width / 2, height / 2

        for i in range(steps):
            angle = i * 2.4  # Golden angle in radians ≈ 137.5 degrees
            radius = phi * math.sqrt(i) * min(width, height) / 20
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((int(x), int(y)))

        return points


class GitArtGenerator:
    def __init__(self, repo_path='.', width=1200, height=1200):
        """Initialize the art generator with a git repository"""
        self.repo = git.Repo(repo_path)
        self.width = width
        self.height = height
        self.repo_path = Path(repo_path)

    def get_repo_fingerprint(self):
        """Generate a deterministic fingerprint of the current repo state"""
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
            pass

        # Analyze all tracked files
        try:
            for item in self.repo.tree().traverse():
                if item.type == 'blob':
                    file_path = item.path

                    if self._should_skip_file(file_path):
                        continue

                    try:
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        lines = content.split('\n')
                        line_count = len(lines)

                        ext = Path(file_path).suffix or 'no_ext'
                        fingerprint_data['file_types'][ext] += line_count

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
        """Generate abstract art based on repository fingerprint using art theory"""
        fingerprint = self.get_repo_fingerprint()

        # Determine color scheme based on repo characteristics
        base_hue = (fingerprint['total_lines'] % 360) / 360.0

        # Choose color palette based on file count
        num_files = len(fingerprint['files'])
        if num_files <= 3:
            palette = ColorTheory.create_complementary_palette(base_hue)
        elif num_files <= 10:
            palette = ColorTheory.create_triadic_palette(base_hue)
        else:
            palette = ColorTheory.create_analogous_palette(base_hue, count=7)

        # Create base image with harmonious gradient
        img = self._create_artistic_background(fingerprint, palette)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Apply composition techniques
        self._draw_with_composition(draw, fingerprint, palette)

        # Add subtle texture and depth
        img = self._add_texture_and_depth(img)

        # Save the art
        img.save(output_path, quality=95)
        print(f"Art generated: {output_path}")
        print(f"Based on: {len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines of code, "
              f"{fingerprint['commit_count']} commits")
        print(f"Color scheme: {self._get_palette_name(num_files)}")

        return output_path

    def _get_palette_name(self, num_files):
        """Get the name of the color palette used"""
        if num_files <= 3:
            return "Complementary"
        elif num_files <= 10:
            return "Triadic"
        else:
            return "Analogous"

    def _create_artistic_background(self, fingerprint, palette):
        """Create sophisticated gradient background with color theory"""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        # Use multiple gradient centers for visual interest
        centers = Composition.golden_points(self.width, self.height)

        for y in range(self.height):
            for x in range(self.width):
                # Calculate influence from each center
                influences = []
                for cx, cy in centers:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    max_dist = math.sqrt(self.width**2 + self.height**2)
                    influence = 1 - (dist / max_dist)
                    influences.append(influence)

                # Blend colors based on position
                total_influence = sum(influences)
                r, g, b = 0, 0, 0

                for i, influence in enumerate(influences):
                    weight = influence / total_influence if total_influence > 0 else 0
                    color_idx = i % len(palette)
                    pr, pg, pb = palette[color_idx]
                    r += pr * weight
                    g += pg * weight
                    b += pb * weight

                pixels[x, y] = (int(r), int(g), int(b))

        return img

    def _draw_with_composition(self, draw, fingerprint, palette):
        """Draw elements using composition rules and visual hierarchy"""
        files = fingerprint['files']

        if not files:
            return

        # Sort files by importance (line count)
        sorted_files = sorted(files.items(), key=lambda x: x[1]['lines'], reverse=True)

        # Use golden ratio points for most important files
        golden_pts = Composition.golden_points(self.width, self.height)
        thirds_pts = Composition.rule_of_thirds_points(self.width, self.height)
        fib_pts = Composition.fibonacci_spiral_points(self.width, self.height, len(sorted_files))

        # Combine focal points
        focal_points = golden_pts + thirds_pts

        for idx, (file_path, file_data) in enumerate(sorted_files):
            # Place important files at focal points, others follow fibonacci spiral
            if idx < len(focal_points):
                x, y = focal_points[idx]
            else:
                spiral_idx = idx - len(focal_points)
                if spiral_idx < len(fib_pts):
                    x, y = fib_pts[spiral_idx]
                else:
                    # Fallback to grid
                    grid_size = int(np.sqrt(len(files))) + 1
                    cell_w = self.width // grid_size
                    cell_h = self.height // grid_size
                    x = (idx % grid_size) * cell_w + cell_w // 2
                    y = (idx // grid_size) * cell_h + cell_h // 2

            # Size based on importance (line count) with visual hierarchy
            max_lines = max(f['lines'] for f in files.values())
            min_lines = min(f['lines'] for f in files.values())

            if max_lines > min_lines:
                normalized_size = (file_data['lines'] - min_lines) / (max_lines - min_lines)
            else:
                normalized_size = 0.5

            # Apply contrast: make sizes more dramatic
            size = 30 + normalized_size * 200

            # Color from harmonious palette based on file hash
            hash_val = int(file_data['hash'][:8], 16)
            color_idx = hash_val % len(palette)
            base_color = palette[color_idx]

            # Add variation to opacity based on file importance
            opacity = int(150 + normalized_size * 80)

            # Draw with artistic shapes
            self._draw_artistic_element(draw, x, y, size, base_color, opacity, file_data)

        # Add connecting flow lines for visual unity
        self._add_flow_lines(draw, sorted_files, focal_points, fib_pts, palette)

    def _draw_artistic_element(self, draw, x, y, size, color, opacity, file_data):
        """Draw individual elements with artistic variation"""
        # Determine shape based on file type
        ext = file_data['extension']
        hash_val = int(file_data['hash'][:8], 16)

        # Different shapes for different file types
        if ext == '.py':
            # Organic circles for Python
            self._draw_organic_circle(draw, x, y, size, color, opacity)
        elif ext == '.md':
            # Soft rectangles for markdown
            self._draw_rounded_rect(draw, x, y, size, color, opacity)
        elif ext == '.txt':
            # Triangles for text files
            self._draw_triangle(draw, x, y, size, color, opacity)
        else:
            # Hexagons for other files
            self._draw_hexagon(draw, x, y, size, color, opacity)

        # Add subtle outline for depth
        outline_color = tuple(max(0, c - 40) for c in color)
        draw.ellipse([x - size/2 - 2, y - size/2 - 2, x + size/2 + 2, y + size/2 + 2],
                    outline=outline_color + (opacity//2,), width=2)

    def _draw_organic_circle(self, draw, x, y, size, color, opacity):
        """Draw organic-looking circle with slight imperfections"""
        points = []
        segments = 32
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            # Add slight variation to radius for organic feel
            variation = 1 + 0.05 * math.sin(angle * 5)
            radius = (size / 2) * variation
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        draw.polygon(points, fill=color + (opacity,))

    def _draw_rounded_rect(self, draw, x, y, size, color, opacity):
        """Draw rectangle with rounded corners"""
        corner_radius = size * 0.2
        draw.rounded_rectangle(
            [x - size/2, y - size/2, x + size/2, y + size/2],
            radius=corner_radius,
            fill=color + (opacity,)
        )

    def _draw_triangle(self, draw, x, y, size, color, opacity):
        """Draw equilateral triangle"""
        h = size * 0.866  # height of equilateral triangle
        points = [
            (x, y - h/2),
            (x - size/2, y + h/2),
            (x + size/2, y + h/2)
        ]
        draw.polygon(points, fill=color + (opacity,))

    def _draw_hexagon(self, draw, x, y, size, color, opacity):
        """Draw regular hexagon"""
        points = []
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            px = x + (size/2) * math.cos(angle)
            py = y + (size/2) * math.sin(angle)
            points.append((px, py))
        draw.polygon(points, fill=color + (opacity,))

    def _add_flow_lines(self, draw, sorted_files, focal_points, fib_pts, palette):
        """Add subtle connecting lines for visual flow and unity"""
        if len(sorted_files) < 2:
            return

        # Connect some elements with subtle curves
        all_points = focal_points + fib_pts[:max(0, len(sorted_files) - len(focal_points))]

        for i in range(min(len(all_points) - 1, 10)):  # Limit connections
            x1, y1 = all_points[i]
            x2, y2 = all_points[i + 1]

            # Draw bezier curve
            control_x = (x1 + x2) / 2 + (y2 - y1) * 0.2
            control_y = (y1 + y2) / 2 - (x2 - x1) * 0.2

            # Use palette colors with low opacity
            color = palette[i % len(palette)]

            # Draw curve as series of small lines
            steps = 20
            for t in range(steps - 1):
                t1 = t / steps
                t2 = (t + 1) / steps

                # Quadratic bezier
                p1x = (1-t1)**2 * x1 + 2*(1-t1)*t1 * control_x + t1**2 * x2
                p1y = (1-t1)**2 * y1 + 2*(1-t1)*t1 * control_y + t1**2 * y2
                p2x = (1-t2)**2 * x1 + 2*(1-t2)*t2 * control_x + t2**2 * x2
                p2y = (1-t2)**2 * y1 + 2*(1-t2)*t2 * control_y + t2**2 * y2

                draw.line([(p1x, p1y), (p2x, p2y)], fill=color + (30,), width=2)

    def _add_texture_and_depth(self, img):
        """Add subtle texture and depth to the final image"""
        # Apply slight blur to background
        blurred = img.filter(ImageFilter.GaussianBlur(radius=1))

        # Blend original and blurred for subtle effect
        img = Image.blend(img, blurred, alpha=0.3)

        return img


def main():
    """Main function to generate art from current repository"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate beautiful abstract art from a git repository using art theory principles'
    )
    parser.add_argument('--repo', default='.', help='Path to git repository (default: current directory)')
    parser.add_argument('--output', default='repo_art.png', help='Output image path')
    parser.add_argument('--size', type=int, default=1200, help='Image size (square)')

    args = parser.parse_args()

    generator = GitArtGenerator(args.repo, width=args.size, height=args.size)
    generator.generate_art(args.output)


if __name__ == '__main__':
    main()
