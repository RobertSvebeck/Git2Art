"""Watercolor art style - soft, flowing, and translucent.

Inspired by traditional watercolor painting, this style features:
- Soft, blurred edges for organic appearance
- Transparent, overlapping color washes
- Light, airy composition with color bleeding effects
- Multiple layers with varying opacity
- Gentle gradients and smooth transitions
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


class WatercolorPalette:
    """Generate soft, translucent color palettes for watercolor style."""

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
    def rgb_to_watercolor(rgb):
        """Convert RGB to soft watercolor version with reduced saturation."""
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Lighter and less saturated for watercolor effect
        l = 0.75 + (l * 0.15)
        s = 0.35 + (s * 0.15)

        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def select_palette(fingerprint):
        """Select and convert palette to watercolor tones."""
        file_types = fingerprint['file_types']

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

        base_colors = WatercolorPalette.PALETTES[palette_name]
        watercolor_colors = [WatercolorPalette.rgb_to_watercolor(rgb) for rgb in base_colors]

        return palette_name, watercolor_colors


class WatercolorStyleGenerator(BaseArtGenerator):
    """Watercolor style with soft, flowing, translucent appearance."""

    STYLE_NAME = "watercolor"
    STYLE_DESCRIPTION = "Soft, flowing watercolor effect with transparent washes and blurred edges"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize watercolor generator."""
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

        self.blur_radius = kwargs.get('blur_radius', 8)
        self.wash_layers = kwargs.get('wash_layers', 5)

    def generate_art(self, output_path='repo_art.png'):
        """Generate watercolor artwork."""
        fingerprint = self.get_repo_fingerprint()
        palette_name, colors = WatercolorPalette.select_palette(fingerprint)

        # Create canvas with paper texture (very light background)
        img = Image.new('RGBA', (self.width, self.height), color=(252, 251, 248, 255))

        # Paint multiple transparent layers
        self._paint_background_washes(img, colors, fingerprint)
        self._paint_main_elements(img, colors, fingerprint)
        self._paint_detail_washes(img, colors, fingerprint)

        # Apply watercolor blur
        img = img.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))

        # Convert to RGB for saving
        final_img = Image.new('RGB', (self.width, self.height), color=(252, 251, 248))
        final_img.paste(img, (0, 0), img)

        final_img.save(output_path, quality=95)

        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME} (watercolor)")
        print(f"Palette: {palette_name}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files painted with watercolor washes")

        return output_path

    def _paint_background_washes(self, img, colors, fingerprint):
        """Paint large, soft background washes."""
        draw = ImageDraw.Draw(img, 'RGBA')
        total_lines = fingerprint['total_lines']

        num_washes = DeterministicRandom.randint(str(total_lines), 0, 3, 5)

        for i in range(num_washes):
            x = DeterministicRandom.uniform(str(total_lines), i * 3, 0, self.width)
            y = DeterministicRandom.uniform(str(total_lines), i * 3 + 1, 0, self.height)

            color = colors[i % len(colors)]
            size = min(self.width, self.height) * DeterministicRandom.uniform(str(total_lines), i * 3 + 2, 0.3, 0.6)

            # Very transparent wash
            opacity = DeterministicRandom.randint(str(total_lines), i * 4, 20, 40)

            draw.ellipse(
                [x - size/2, y - size/2, x + size/2, y + size/2],
                fill=color + (opacity,)
            )

    def _paint_main_elements(self, img, colors, fingerprint):
        """Paint main watercolor shapes for each file."""
        draw = ImageDraw.Draw(img, 'RGBA')
        files = sorted(fingerprint['files'].items(), key=lambda x: x[1]['lines'], reverse=True)

        for file_path, file_data in files:
            file_hash = file_data['hash']
            lines = file_data['lines']

            # Position based on file hash
            x = DeterministicRandom.uniform(file_hash, 0, self.width * 0.15, self.width * 0.85)
            y = DeterministicRandom.uniform(file_hash, 1, self.height * 0.15, self.height * 0.85)

            # Size based on file importance
            base_size = min(self.width, self.height) * 0.05
            size = base_size + (lines / fingerprint['total_lines']) * base_size * 3

            # Color selection
            color_idx = DeterministicRandom.randint(file_hash, 2, 0, len(colors) - 1)
            color = colors[color_idx]

            # Paint multiple overlapping washes for depth
            for layer in range(self.wash_layers):
                offset_x = DeterministicRandom.uniform(file_hash, layer * 5, -size * 0.2, size * 0.2)
                offset_y = DeterministicRandom.uniform(file_hash, layer * 5 + 1, -size * 0.2, size * 0.2)

                layer_size = size * (1 - layer * 0.1)
                opacity = DeterministicRandom.randint(file_hash, layer * 6, 30, 60)

                # Vary the shape slightly
                shape_type = DeterministicRandom.randint(file_hash, layer * 7, 0, 2)

                if shape_type == 0:
                    # Ellipse
                    draw.ellipse(
                        [x + offset_x - layer_size/2, y + offset_y - layer_size/2,
                         x + offset_x + layer_size/2, y + offset_y + layer_size/2],
                        fill=color + (opacity,)
                    )
                else:
                    # Irregular blob using polygon
                    points = []
                    num_points = 8
                    for p in range(num_points):
                        angle = (p / num_points) * 2 * math.pi
                        radius_var = DeterministicRandom.uniform(file_hash, layer * 8 + p, 0.7, 1.3)
                        px = x + offset_x + math.cos(angle) * layer_size/2 * radius_var
                        py = y + offset_y + math.sin(angle) * layer_size/2 * radius_var
                        points.append((px, py))

                    draw.polygon(points, fill=color + (opacity,))

    def _paint_detail_washes(self, img, colors, fingerprint):
        """Paint small detail washes for texture."""
        draw = ImageDraw.Draw(img, 'RGBA')
        total_lines = fingerprint['total_lines']

        # Add small details based on file count
        num_details = min(len(fingerprint['files']) * 2, 50)

        for i in range(num_details):
            x = DeterministicRandom.uniform(str(total_lines), i * 10, 0, self.width)
            y = DeterministicRandom.uniform(str(total_lines), i * 10 + 1, 0, self.height)

            size = DeterministicRandom.uniform(str(total_lines), i * 10 + 2, 20, 60)
            color = colors[i % len(colors)]
            opacity = DeterministicRandom.randint(str(total_lines), i * 11, 15, 35)

            draw.ellipse(
                [x - size/2, y - size/2, x + size/2, y + size/2],
                fill=color + (opacity,)
            )
