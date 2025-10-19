#!/usr/bin/env python3
"""
Git2Art: Organic & Dynamic Edition
Vibrant colors, flowing lines, full of action and movement!
"""

import git
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import colorsys
from pathlib import Path
from collections import defaultdict
import math
import random


class OrganicColorTheory:
    """Vibrant, saturated color palettes with high contrast"""

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convert HSV to RGB (0-255)"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def create_vibrant_palette(seed, count=8):
        """Create highly saturated, contrasting color palette"""
        colors = []
        base_hue = (seed % 360) / 360.0

        for i in range(count):
            # Spread colors around the wheel with golden angle for natural distribution
            golden_angle = 137.508  # degrees
            h = (base_hue + (i * golden_angle / 360.0)) % 1.0

            # HIGH saturation (0.75-0.95) for vibrant colors
            s = 0.75 + (hash(str(seed + i)) % 20) / 100.0

            # HIGH value (0.7-1.0) for bright, energetic colors
            v = 0.7 + (hash(str(seed - i)) % 30) / 100.0

            colors.append(OrganicColorTheory.hsv_to_rgb(h, s, v))

        return colors

    @staticmethod
    def create_accent_colors(base_palette):
        """Create lighter and darker accent colors for variation"""
        accents = []
        for color in base_palette:
            r, g, b = color
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

            # Create lighter version
            light = OrganicColorTheory.hsv_to_rgb(h, s * 0.6, min(1.0, v * 1.3))
            accents.append(light)

            # Create darker version
            dark = OrganicColorTheory.hsv_to_rgb(h, min(1.0, s * 1.2), v * 0.6)
            accents.append(dark)

        return accents


class OrganicShapes:
    """Generate flowing, organic shapes and lines"""

    @staticmethod
    def flowing_line(start, end, curviness=0.3, segments=50):
        """Generate points for a flowing organic line"""
        x1, y1 = start
        x2, y2 = end

        points = []

        # Create control points for bezier curve with randomness
        dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)

        # Multiple control points for more organic curves
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Perpendicular offset for curve
        dx = x2 - x1
        dy = y2 - y1
        perp_x = -dy
        perp_y = dx
        length = math.sqrt(perp_x**2 + perp_y**2)
        if length > 0:
            perp_x /= length
            perp_y /= length

        offset = dist * curviness
        ctrl1_x = mid_x + perp_x * offset
        ctrl1_y = mid_y + perp_y * offset

        # Cubic bezier
        for i in range(segments + 1):
            t = i / segments

            # Cubic bezier formula
            x = (1-t)**3 * x1 + 3*(1-t)**2*t * ctrl1_x + 3*(1-t)*t**2 * mid_x + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2*t * ctrl1_y + 3*(1-t)*t**2 * mid_y + t**3 * y2

            points.append((x, y))

        return points

    @staticmethod
    def particle_burst(center, count, min_radius, max_radius, seed):
        """Generate particle positions radiating from center"""
        cx, cy = center
        particles = []

        random.seed(seed)

        for i in range(count):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(min_radius, max_radius)

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            size = random.uniform(2, 15)

            particles.append((x, y, size))

        return particles

    @staticmethod
    def wave_pattern(y_base, width, amplitude, frequency, phase, segments=200):
        """Generate wave pattern points"""
        points = []
        for i in range(segments + 1):
            x = (i / segments) * width
            y = y_base + amplitude * math.sin(frequency * x / 100 + phase)
            points.append((x, y))
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

        try:
            head_commit = self.repo.head.commit
            fingerprint_data['commit_count'] = len(list(self.repo.iter_commits()))
            fingerprint_data['authors'] = {c.author.name for c in self.repo.iter_commits()}
        except:
            pass

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
        """Generate vibrant, organic abstract art"""
        fingerprint = self.get_repo_fingerprint()

        # Create vibrant color palette
        seed = fingerprint['total_lines']
        palette = OrganicColorTheory.create_vibrant_palette(seed, count=8)
        accents = OrganicColorTheory.create_accent_colors(palette)
        all_colors = palette + accents

        # Create dynamic background
        img = self._create_dynamic_background(fingerprint, palette)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Add flowing background waves and patterns
        self._add_flowing_background(draw, fingerprint, all_colors)

        # Draw main file elements with organic shapes
        self._draw_organic_elements(draw, fingerprint, all_colors)

        # Add connecting energy lines
        self._add_energy_lines(draw, fingerprint, all_colors)

        # Add particle effects and action
        self._add_particle_effects(draw, fingerprint, all_colors)

        # Add wave patterns for movement
        self._add_wave_patterns(draw, fingerprint, all_colors)

        # Save the art
        img.save(output_path, quality=95)
        print(f"Organic art generated: {output_path}")
        print(f"Based on: {len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines of code, "
              f"{fingerprint['commit_count']} commits")
        print(f"Vibrant palette with {len(all_colors)} colors")

        return output_path

    def _create_dynamic_background(self, fingerprint, palette):
        """Create vibrant gradient background with movement"""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        # Multiple gradient centers for dynamic feel
        num_centers = 3 + (fingerprint['commit_count'] % 3)
        centers = []

        seed = fingerprint['total_lines']
        random.seed(seed)

        for i in range(num_centers):
            cx = random.randint(0, self.width)
            cy = random.randint(0, self.height)
            centers.append((cx, cy))

        for y in range(self.height):
            for x in range(self.width):
                # Calculate influence from each center
                influences = []
                for cx, cy in centers:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    max_dist = math.sqrt(self.width**2 + self.height**2)
                    influence = max(0, 1 - (dist / max_dist))
                    influences.append(influence)

                # Blend colors
                total_influence = sum(influences) + 0.001
                r, g, b = 0, 0, 0

                for i, influence in enumerate(influences):
                    weight = influence / total_influence
                    color_idx = i % len(palette)
                    pr, pg, pb = palette[color_idx]
                    r += pr * weight
                    g += pg * weight
                    b += pb * weight

                pixels[x, y] = (int(r), int(g), int(b))

        return img

    def _add_flowing_background(self, draw, fingerprint, colors):
        """Add flowing organic lines in background"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        # Create flowing lines across the canvas
        num_flows = 5 + (fingerprint['commit_count'] % 10)

        for i in range(num_flows):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)

            points = OrganicShapes.flowing_line(
                (x1, y1), (x2, y2),
                curviness=random.uniform(0.2, 0.5),
                segments=100
            )

            color = colors[i % len(colors)]

            # Draw thick flowing line with transparency
            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]],
                         fill=color + (40,),
                         width=random.randint(2, 8))

    def _draw_organic_elements(self, draw, fingerprint, colors):
        """Draw main file elements with organic, flowing shapes"""
        files = fingerprint['files']

        if not files:
            return

        sorted_files = sorted(files.items(), key=lambda x: x[1]['lines'], reverse=True)

        # Distribute files more naturally
        for idx, (file_path, file_data) in enumerate(sorted_files):
            # Use golden angle for natural distribution
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)

            # Spiral outward from center
            radius = 50 + idx * (min(self.width, self.height) / (2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            # Size based on importance
            max_lines = max(f['lines'] for f in files.values())
            min_lines = min(f['lines'] for f in files.values())

            if max_lines > min_lines:
                normalized_size = (file_data['lines'] - min_lines) / (max_lines - min_lines)
            else:
                normalized_size = 0.5

            size = 40 + normalized_size * 150

            # Get vibrant color from hash
            hash_val = int(file_data['hash'][:8], 16)
            color = colors[hash_val % len(colors)]

            # Draw organic pulsing shape
            self._draw_organic_blob(draw, x, y, size, color, file_data['hash'])

    def _draw_organic_blob(self, draw, x, y, size, color, seed_hash):
        """Draw organic blob shape with variations"""
        points = []
        segments = 24

        hash_seed = int(seed_hash[:8], 16)
        random.seed(hash_seed)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi

            # Organic variation in radius
            variation = 1 + 0.2 * math.sin(angle * 3) + random.uniform(-0.15, 0.15)
            radius = (size / 2) * variation

            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        # Draw filled shape with high opacity
        draw.polygon(points, fill=color + (200,), outline=color)

        # Add inner highlight
        inner_points = []
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            variation = 0.7
            radius = (size / 2) * variation
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            inner_points.append((px, py))

        # Lighter inner color
        r, g, b = color
        lighter = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
        draw.polygon(inner_points, fill=lighter + (150,))

    def _add_energy_lines(self, draw, fingerprint, colors):
        """Add dynamic energy lines connecting elements"""
        files = list(fingerprint['files'].items())

        if len(files) < 2:
            return

        seed = fingerprint['total_lines']
        random.seed(seed)

        # Connect files with energy lines
        connections = min(len(files) * 2, 30)  # Lots of connections!

        for i in range(connections):
            idx1 = i % len(files)
            idx2 = (i + 1) % len(files)

            # Calculate positions (same logic as in draw_organic_elements)
            golden_angle = 137.508

            angle1 = (idx1 * golden_angle) * (math.pi / 180)
            radius1 = 50 + idx1 * (min(self.width, self.height) / (2 * len(files)))
            cx, cy = self.width / 2, self.height / 2
            x1 = cx + radius1 * math.cos(angle1)
            y1 = cy + radius1 * math.sin(angle1)

            angle2 = (idx2 * golden_angle) * (math.pi / 180)
            radius2 = 50 + idx2 * (min(self.width, self.height) / (2 * len(files)))
            x2 = cx + radius2 * math.cos(angle2)
            y2 = cy + radius2 * math.sin(angle2)

            # Flowing line
            points = OrganicShapes.flowing_line(
                (x1, y1), (x2, y2),
                curviness=random.uniform(0.2, 0.6),
                segments=50
            )

            color = colors[i % len(colors)]

            # Draw with varying thickness for energy feel
            for j in range(len(points) - 1):
                thickness = 1 + int(3 * math.sin((j / len(points)) * math.pi))
                draw.line([points[j], points[j+1]],
                         fill=color + (120,),
                         width=thickness)

    def _add_particle_effects(self, draw, fingerprint, colors):
        """Add particle burst effects for action"""
        files = list(fingerprint['files'].items())

        if not files:
            return

        seed = fingerprint['total_lines']

        # Add particles around important files
        for idx, (file_path, file_data) in enumerate(files[:5]):  # Top 5 files
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius = 50 + idx * (min(self.width, self.height) / (2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)
            particle_count = 20 + (file_data['lines'] // 10)

            particles = OrganicShapes.particle_burst(
                (x, y),
                particle_count,
                30, 80,
                hash_val
            )

            color = colors[hash_val % len(colors)]

            for px, py, size in particles:
                draw.ellipse(
                    [px - size/2, py - size/2, px + size/2, py + size/2],
                    fill=color + (180,)
                )

    def _add_wave_patterns(self, draw, fingerprint, colors):
        """Add wave patterns for dynamic movement"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_waves = 3 + (fingerprint['commit_count'] % 5)

        for i in range(num_waves):
            y_base = random.randint(0, self.height)
            amplitude = random.randint(20, 60)
            frequency = random.uniform(1, 4)
            phase = random.uniform(0, 2 * math.pi)

            points = OrganicShapes.wave_pattern(
                y_base, self.width, amplitude, frequency, phase
            )

            color = colors[i % len(colors)]

            # Draw wave with varying thickness
            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]],
                         fill=color + (60,),
                         width=3)


def main():
    """Main function to generate art from current repository"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate vibrant, organic abstract art from a git repository'
    )
    parser.add_argument('--repo', default='.', help='Path to git repository (default: current directory)')
    parser.add_argument('--output', default='repo_art.png', help='Output image path')
    parser.add_argument('--size', type=int, default=1200, help='Image size (square)')

    args = parser.parse_args()

    generator = GitArtGenerator(args.repo, width=args.size, height=args.size)
    generator.generate_art(args.output)


if __name__ == '__main__':
    main()
