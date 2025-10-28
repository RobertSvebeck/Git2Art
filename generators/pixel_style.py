"""Pixel art style - retro, blocky, 8-bit aesthetic.

Inspired by classic video games and early computer graphics, featuring:
- Blocky, pixelated appearance with clear grid structure
- Limited color palette (8-16 colors) for authentic retro feel
- Sharp edges and rectangular shapes
- Nostalgic 8-bit/16-bit aesthetic
- Grid-based layout for organized composition
"""

from .base import BaseArtGenerator
from PIL import Image, ImageDraw
import colorsys
import hashlib


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


class PixelPalette:
    """Generate limited, vibrant color palettes for pixel art style."""

    # Classic 8-bit inspired palettes
    PALETTES = {
        'python': [
            (41, 128, 185),   # Blue
            (52, 152, 219),   # Light Blue
            (26, 188, 156),   # Teal
            (22, 160, 133),   # Dark Teal
            (241, 196, 15),   # Yellow
            (243, 156, 18),   # Orange
            (230, 126, 34),   # Dark Orange
            (211, 84, 0),     # Red-Orange
        ],
        'javascript': [
            (241, 196, 15),   # Yellow
            (243, 156, 18),   # Orange
            (230, 126, 34),   # Dark Orange
            (211, 84, 0),     # Red
            (192, 57, 43),    # Dark Red
            (231, 76, 60),    # Crimson
            (149, 165, 166),  # Gray
            (127, 140, 141),  # Dark Gray
        ],
        'php': [
            (155, 89, 182),   # Purple
            (142, 68, 173),   # Dark Purple
            (187, 143, 206),  # Light Purple
            (175, 122, 197),  # Mid Purple
            (52, 73, 94),     # Navy
            (44, 62, 80),     # Dark Navy
            (236, 240, 241),  # White
            (189, 195, 199),  # Light Gray
        ],
        'default': [
            (231, 76, 60),    # Red
            (241, 196, 15),   # Yellow
            (46, 204, 113),   # Green
            (52, 152, 219),   # Blue
            (155, 89, 182),   # Purple
            (230, 126, 34),   # Orange
            (52, 73, 94),     # Dark
            (236, 240, 241),  # Light
        ]
    }

    @staticmethod
    def select_palette(fingerprint):
        """Select pixel art palette based on repository type."""
        file_types = fingerprint['file_types']

        if file_types.get('.py', 0) > 0:
            palette_name = 'python'
        elif file_types.get('.js', 0) + file_types.get('.jsx', 0) + file_types.get('.ts', 0) > 0:
            palette_name = 'javascript'
        elif file_types.get('.php', 0) > 0:
            palette_name = 'php'
        else:
            palette_name = 'default'

        return palette_name, PixelPalette.PALETTES[palette_name]


class PixelStyleGenerator(BaseArtGenerator):
    """Pixel art style with blocky, retro 8-bit aesthetic."""

    STYLE_NAME = "pixel"
    STYLE_DESCRIPTION = "Retro pixel art with blocky shapes and limited color palette inspired by 8-bit games"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize pixel art generator."""
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

        self.pixel_size = kwargs.get('pixel_size', 16)  # Size of each "pixel" block
        self.grid_cols = self.width // self.pixel_size
        self.grid_rows = self.height // self.pixel_size

    def generate_art(self, output_path='repo_art.png'):
        """Generate pixel art."""
        fingerprint = self.get_repo_fingerprint()
        palette_name, colors = PixelPalette.select_palette(fingerprint)

        # Create canvas with dark background (classic game screen)
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)

        # Draw pixel grid background
        self._draw_background_pattern(draw, colors, fingerprint)

        # Draw file elements as pixel sprites
        self._draw_pixel_sprites(draw, colors, fingerprint)

        # Draw decorative pixel borders
        self._draw_pixel_borders(draw, colors, fingerprint)

        img.save(output_path, quality=95)

        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME} (pixel art)")
        print(f"Palette: {palette_name}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files rendered as pixel sprites")

        return output_path

    def _draw_background_pattern(self, draw, colors, fingerprint):
        """Draw subtle pixel pattern in background."""
        total_lines = fingerprint['total_lines']

        # Create a subtle background pattern
        for i in range(0, self.grid_cols, 4):
            for j in range(0, self.grid_rows, 4):
                # Deterministic pattern
                pattern_seed = f"{total_lines}_{i}_{j}"
                if DeterministicRandom.uniform(pattern_seed, 0, 0, 1) < 0.1:
                    # Draw a faint pixel
                    x = i * self.pixel_size
                    y = j * self.pixel_size
                    color = colors[-1]  # Use last color (usually gray/dark)

                    # Make it very dark
                    r, g, b = color
                    dark_color = (
                        max(20, r // 4),
                        max(20, g // 4),
                        max(20, b // 4)
                    )

                    self._draw_pixel(draw, x, y, dark_color)

    def _draw_pixel_sprites(self, draw, colors, fingerprint):
        """Draw pixel sprites representing files."""
        files = sorted(fingerprint['files'].items(), key=lambda x: x[1]['lines'], reverse=True)

        for idx, (file_path, file_data) in enumerate(files):
            file_hash = file_data['hash']
            lines = file_data['lines']

            # Position on grid
            grid_x = DeterministicRandom.randint(file_hash, 0, 2, self.grid_cols - 10)
            grid_y = DeterministicRandom.randint(file_hash, 1, 2, self.grid_rows - 10)

            # Size based on lines of code (in grid units)
            sprite_size = max(2, min(8, int(lines / fingerprint['total_lines'] * 20) + 2))

            # Color selection
            color_idx = DeterministicRandom.randint(file_hash, 2, 0, len(colors) - 1)
            color = colors[color_idx]

            # Draw sprite shape (box or cross pattern)
            sprite_type = DeterministicRandom.randint(file_hash, 3, 0, 2)

            if sprite_type == 0:
                # Filled box
                self._draw_pixel_box(draw, grid_x, grid_y, sprite_size, color)
            elif sprite_type == 1:
                # Hollow box
                self._draw_pixel_box_outline(draw, grid_x, grid_y, sprite_size, color)
            else:
                # Cross/Plus shape
                self._draw_pixel_cross(draw, grid_x, grid_y, sprite_size, color)

    def _draw_pixel_borders(self, draw, colors, fingerprint):
        """Draw decorative pixel borders."""
        total_lines = fingerprint['total_lines']
        border_color = colors[0]

        # Draw corner decorations
        corner_size = 5

        # Top-left corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                self._draw_pixel(draw, i * self.pixel_size, j * self.pixel_size, border_color)

        # Top-right corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                x = (self.grid_cols - i - 1) * self.pixel_size
                y = j * self.pixel_size
                self._draw_pixel(draw, x, y, border_color)

        # Bottom-left corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                x = i * self.pixel_size
                y = (self.grid_rows - j - 1) * self.pixel_size
                self._draw_pixel(draw, x, y, border_color)

        # Bottom-right corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                x = (self.grid_cols - i - 1) * self.pixel_size
                y = (self.grid_rows - j - 1) * self.pixel_size
                self._draw_pixel(draw, x, y, border_color)

    def _draw_pixel(self, draw, x, y, color):
        """Draw a single pixel block."""
        draw.rectangle(
            [x, y, x + self.pixel_size - 1, y + self.pixel_size - 1],
            fill=color
        )

    def _draw_pixel_box(self, draw, grid_x, grid_y, size, color):
        """Draw a filled box of pixels."""
        for i in range(size):
            for j in range(size):
                x = (grid_x + i) * self.pixel_size
                y = (grid_y + j) * self.pixel_size
                self._draw_pixel(draw, x, y, color)

    def _draw_pixel_box_outline(self, draw, grid_x, grid_y, size, color):
        """Draw a hollow box outline."""
        for i in range(size):
            # Top and bottom edges
            x = (grid_x + i) * self.pixel_size
            y_top = grid_y * self.pixel_size
            y_bottom = (grid_y + size - 1) * self.pixel_size
            self._draw_pixel(draw, x, y_top, color)
            self._draw_pixel(draw, x, y_bottom, color)

        for j in range(1, size - 1):
            # Left and right edges
            x_left = grid_x * self.pixel_size
            x_right = (grid_x + size - 1) * self.pixel_size
            y = (grid_y + j) * self.pixel_size
            self._draw_pixel(draw, x_left, y, color)
            self._draw_pixel(draw, x_right, y, color)

    def _draw_pixel_cross(self, draw, grid_x, grid_y, size, color):
        """Draw a cross/plus shape."""
        center = size // 2

        # Vertical line
        for j in range(size):
            x = (grid_x + center) * self.pixel_size
            y = (grid_y + j) * self.pixel_size
            self._draw_pixel(draw, x, y, color)

        # Horizontal line
        for i in range(size):
            x = (grid_x + i) * self.pixel_size
            y = (grid_y + center) * self.pixel_size
            self._draw_pixel(draw, x, y, color)
