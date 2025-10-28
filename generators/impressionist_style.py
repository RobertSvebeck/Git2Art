"""Impressionist art style - soft, luminous, painted with light.

Inspired by Monet, Renoir, and the Impressionist masters, this style features:
- Small, visible brush strokes (dabs and touches of color)
- Light, pastel color palette with high luminosity
- Colors applied side-by-side with minimal mixing (pointillism influence)
- Soft edges created with blur effects
- Emphasis on capturing light and atmosphere
- Layered composition with varying opacity for depth
"""

from .base import BaseArtGenerator
from PIL import Image, ImageDraw, ImageFilter
import colorsys
import hashlib
import math


class DeterministicRandom:
    """Deterministic random number generator for reproducible art."""

    @staticmethod
    def from_hash(hash_string, index=0):
        """Generate deterministic value from hash and index."""
        combined = f"{hash_string}_{index}"
        hash_bytes = hashlib.md5(combined.encode()).digest()
        value = int.from_bytes(hash_bytes[:8], byteorder='big')
        return value / (2**64 - 1)

    @staticmethod
    def uniform(hash_string, index, min_val, max_val):
        """Deterministic uniform distribution."""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        return min_val + rand_val * (max_val - min_val)

    @staticmethod
    def randint(hash_string, index, min_val, max_val):
        """Deterministic integer in range."""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        return int(min_val + rand_val * (max_val - min_val + 1))


class ImpressionistPalette:
    """Generate light, pastel palettes for impressionist style."""

    PALETTES = {
        'python': [(52, 152, 219), (41, 128, 185), (26, 188, 156)],
        'javascript': [(241, 196, 15), (230, 126, 34), (211, 84, 0)],
        'php': [(142, 68, 173), (155, 89, 182), (187, 143, 206)],
        'java': [(231, 76, 60), (192, 57, 43), (165, 105, 79)],
        'ruby': [(220, 20, 60), (178, 34, 34), (255, 99, 71)],
        'systems': [(0, 173, 181), (52, 152, 219), (149, 165, 166)],
        'data': [(46, 204, 113), (39, 174, 96), (22, 160, 133)],
        'cpp': [(69, 85, 96), (52, 73, 94), (93, 109, 126)],
    }

    @staticmethod
    def rgb_to_pastel(rgb):
        """Convert RGB color to soft pastel version."""
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Moderate lightness (55-70% for visible color)
        l = 0.55 + (l * 0.15)
        # Good saturation (50-70% for vibrant but soft)
        s = 0.50 + (s * 0.20)

        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def select_palette(fingerprint):
        """Select and convert palette to pastel tones based on repository type."""
        file_types = fingerprint['file_types']

        # Determine primary language
        if file_types.get('.py', 0) > 0:
            palette_name = 'python'
        elif file_types.get('.js', 0) + file_types.get('.jsx', 0) + file_types.get('.ts', 0) > 0:
            palette_name = 'javascript'
        elif file_types.get('.php', 0) > 0:
            palette_name = 'php'
        elif file_types.get('.java', 0) + file_types.get('.kt', 0) > 0:
            palette_name = 'java'
        elif file_types.get('.rb', 0) > 0:
            palette_name = 'ruby'
        elif file_types.get('.c', 0) + file_types.get('.cpp', 0) > 0:
            palette_name = 'cpp'
        elif file_types.get('.csv', 0) + file_types.get('.sql', 0) > 0:
            palette_name = 'data'
        else:
            palette_name = 'systems'

        base_colors = ImpressionistPalette.PALETTES[palette_name]
        pastel_colors = [ImpressionistPalette.rgb_to_pastel(rgb) for rgb in base_colors]

        # Add lighter variations
        expanded = []
        for color in pastel_colors:
            expanded.append(color)
            # Add slightly lighter tint
            r, g, b = [x / 255.0 for x in color]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            l = min(0.80, l + 0.08)
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            expanded.append((int(r * 255), int(g * 255), int(b * 255)))

        return palette_name, expanded

    @staticmethod
    def get_background_color(palette_name):
        """Get soft background color for the canvas."""
        backgrounds = {
            'python': (220, 235, 242),
            'javascript': (242, 235, 220),
            'php': (235, 225, 240),
            'java': (242, 230, 225),
            'ruby': (242, 225, 230),
            'systems': (225, 235, 240),
            'data': (225, 240, 230),
            'cpp': (230, 232, 235),
        }
        return backgrounds.get(palette_name, (230, 230, 230))


class ImpressionistStyleGenerator(BaseArtGenerator):
    """Impressionist style with soft brush strokes and luminous colors."""

    STYLE_NAME = "impressionist"
    STYLE_DESCRIPTION = "Soft, luminous style with small brush dabs and pastel colors inspired by Monet and Renoir"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize impressionist generator."""
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

        self.dab_sizes = kwargs.get('dab_sizes', [(4, 6), (6, 10), (8, 14)])
        self.blur_radius = kwargs.get('blur_radius', 2)

    def generate_art(self, output_path='repo_art.png'):
        """Generate impressionist artwork."""
        fingerprint = self.get_repo_fingerprint()
        palette_name, colors = ImpressionistPalette.select_palette(fingerprint)
        bg_color = ImpressionistPalette.get_background_color(palette_name)

        # Create canvas with soft background
        img = Image.new('RGBA', (self.width, self.height), color=bg_color + (255,))

        # Create drawing layers
        self._paint_background_atmosphere(img, colors, fingerprint)
        self._paint_brush_dabs(img, colors, fingerprint)
        self._paint_light_accents(img, colors, fingerprint)

        # Apply impressionist blur for soft edges
        img = img.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))

        # Convert to RGB for saving
        final_img = Image.new('RGB', (self.width, self.height), color=bg_color)
        final_img.paste(img, (0, 0), img)

        final_img.save(output_path, quality=95)

        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME} (impressionist)")
        print(f"Palette: {palette_name}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files painted with impressionist brush dabs")

        return output_path

    def _paint_background_atmosphere(self, img, colors, fingerprint):
        """Paint atmospheric background with soft color gradients."""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Create 3-5 soft gradient centers
        total_lines = fingerprint['total_lines']
        num_centers = DeterministicRandom.randint(str(total_lines), 0, 3, 5)

        for i in range(num_centers):
            x = DeterministicRandom.uniform(str(total_lines), i * 2, 0, self.width)
            y = DeterministicRandom.uniform(str(total_lines), i * 2 + 1, 0, self.height)

            color = colors[i % len(colors)]
            max_radius = min(self.width, self.height) * 0.6

            # Paint with decreasing opacity
            for radius in range(int(max_radius), 0, -int(max_radius / 20)):
                opacity = int(40 + (radius / max_radius) * 60)
                draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    fill=color + (opacity,)
                )

    def _paint_brush_dabs(self, img, colors, fingerprint):
        """Paint small brush dabs representing files as touches of color."""
        draw = ImageDraw.Draw(img, 'RGBA')

        files = sorted(fingerprint['files'].items(), key=lambda x: x[1]['lines'], reverse=True)

        for file_path, file_data in files:
            file_hash = file_data['hash']
            lines = file_data['lines']

            # Position based on file hash
            base_x = DeterministicRandom.uniform(file_hash, 0, self.width * 0.1, self.width * 0.9)
            base_y = DeterministicRandom.uniform(file_hash, 1, self.height * 0.1, self.height * 0.9)

            # Number of dabs based on lines of code
            num_dabs = min(int(lines / 2) + 10, 200)

            # Color selection
            color_idx = DeterministicRandom.randint(file_hash, 2, 0, len(colors) - 1)
            base_color = colors[color_idx]

            # Paint cluster of dabs
            for i in range(num_dabs):
                # Spread around base position
                spread = min(self.width, self.height) * 0.08
                x = base_x + DeterministicRandom.uniform(file_hash, i * 3, -spread, spread)
                y = base_y + DeterministicRandom.uniform(file_hash, i * 3 + 1, -spread, spread)

                # Vary dab size (small brushstrokes)
                size_min, size_max = self.dab_sizes[i % len(self.dab_sizes)]
                size = DeterministicRandom.uniform(file_hash, i * 3 + 2, size_min, size_max)

                # Slight color variation
                color = self._vary_color(base_color, file_hash, i)

                # Vary opacity for depth
                opacity = DeterministicRandom.randint(file_hash, i * 4, 150, 230)

                # Draw dab (small ellipse)
                draw.ellipse(
                    [x - size/2, y - size/2, x + size/2, y + size/2],
                    fill=color + (opacity,)
                )

    def _paint_light_accents(self, img, colors, fingerprint):
        """Add vibrant color accents for important files."""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Identify important files (largest)
        files = sorted(fingerprint['files'].items(), key=lambda x: x[1]['lines'], reverse=True)[:5]

        for idx, (file_path, file_data) in enumerate(files):
            file_hash = file_data['hash']

            # Position for color accent
            x = DeterministicRandom.uniform(file_hash, 100, self.width * 0.2, self.width * 0.8)
            y = DeterministicRandom.uniform(file_hash, 101, self.height * 0.2, self.height * 0.8)

            # Use vibrant palette color instead of white
            accent_color = colors[idx % len(colors)]
            r, g, b = [x / 255.0 for x in accent_color]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            # Slightly brighter and more saturated
            l = min(0.75, l + 0.10)
            s = min(0.80, s + 0.10)
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            bright_color = (int(r * 255), int(g * 255), int(b * 255))

            # Paint with decreasing size and opacity (color halo)
            for radius in range(50, 10, -5):
                opacity = int(50 - (50 - radius) * 0.8)
                draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    fill=bright_color + (opacity,)
                )

    def _vary_color(self, base_color, hash_string, index):
        """Create slight color variation for naturalistic effect."""
        r, g, b = base_color

        # Small random adjustments
        r_offset = DeterministicRandom.randint(hash_string, index * 5, -15, 15)
        g_offset = DeterministicRandom.randint(hash_string, index * 5 + 1, -15, 15)
        b_offset = DeterministicRandom.randint(hash_string, index * 5 + 2, -15, 15)

        return (
            max(0, min(255, r + r_offset)),
            max(0, min(255, g + g_offset)),
            max(0, min(255, b + b_offset))
        )
