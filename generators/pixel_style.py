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

        self.base_pixel_size = kwargs.get('pixel_size', 16)
        self.pixel_sizes = [8, 12, 16, 24, 32]  # Available pixel sizes
        self.grid_cols = self.width // self.base_pixel_size
        self.grid_rows = self.height // self.base_pixel_size

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
        """Draw subtle pixel pattern in background with varied sizes."""
        total_lines = fingerprint['total_lines']

        # Use smaller pixels for background (8px and 12px)
        small_sizes = [8, 12]

        for i in range(0, self.grid_cols, 2):
            for j in range(0, self.grid_rows, 2):
                pattern_seed = f"{total_lines}_{i}_{j}"
                if DeterministicRandom.uniform(pattern_seed, 0, 0, 1) < 0.15:
                    # Choose pixel size deterministically
                    size_idx = DeterministicRandom.randint(pattern_seed, 1, 0, len(small_sizes) - 1)
                    pixel_size = small_sizes[size_idx]

                    x = i * self.base_pixel_size
                    y = j * self.base_pixel_size
                    color = colors[-1]

                    r, g, b = color
                    dark_color = (
                        max(20, r // 4),
                        max(20, g // 4),
                        max(20, b // 4)
                    )

                    self._draw_pixel(draw, x, y, dark_color, pixel_size)

    def _draw_pixel_sprites(self, draw, colors, fingerprint):
        """Draw pixel sprites with varied pixel sizes based on importance."""
        files = sorted(fingerprint['files'].items(), key=lambda x: x[1]['lines'], reverse=True)

        # Calculate margins (in pixels, not grid units)
        margin = 80  # Consistent margin on all sides

        for idx, (file_path, file_data) in enumerate(files):
            file_hash = file_data['hash']
            lines = file_data['lines']

            importance = lines / fingerprint['total_lines']

            # Larger files get chunkier pixels
            if importance > 0.15:
                pixel_size = 32
            elif importance > 0.08:
                pixel_size = 24
            elif importance > 0.04:
                pixel_size = 16
            else:
                pixel_size = 12

            # Sprite size in grid units
            sprite_size = max(2, min(10, int(importance * 25) + 2))

            # Calculate max sprite dimension in actual pixels
            max_sprite_pixels = sprite_size * pixel_size

            # Position in actual pixel coordinates with proper margins
            x = int(DeterministicRandom.uniform(file_hash, 0, margin,
                                                self.width - margin - max_sprite_pixels))
            y = int(DeterministicRandom.uniform(file_hash, 1, margin,
                                                self.height - margin - max_sprite_pixels))

            # Convert back to grid coordinates for drawing functions
            grid_x = x // self.base_pixel_size
            grid_y = y // self.base_pixel_size

            color_idx = DeterministicRandom.randint(file_hash, 2, 0, len(colors) - 1)
            color = colors[color_idx]

            sprite_type = DeterministicRandom.randint(file_hash, 3, 0, 2)

            if sprite_type == 0:
                self._draw_pixel_box(draw, grid_x, grid_y, sprite_size, color, pixel_size)
            elif sprite_type == 1:
                self._draw_pixel_box_outline(draw, grid_x, grid_y, sprite_size, color, pixel_size)
            else:
                self._draw_pixel_cross(draw, grid_x, grid_y, sprite_size, color, pixel_size)

    def _draw_pixel_borders(self, draw, colors, fingerprint):
        """Draw decorative pixel borders with mixed sizes."""
        border_color = colors[0]
        corner_size = 5
        pixel_size = 16  # Medium size for borders

        # Top-left corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                self._draw_pixel(draw, i * pixel_size, j * pixel_size, border_color, pixel_size)

        # Top-right corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                x = self.width - (i + 1) * pixel_size
                y = j * pixel_size
                self._draw_pixel(draw, x, y, border_color, pixel_size)

        # Bottom-left corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                x = i * pixel_size
                y = self.height - (j + 1) * pixel_size
                self._draw_pixel(draw, x, y, border_color, pixel_size)

        # Bottom-right corner
        for i in range(corner_size):
            for j in range(corner_size - i):
                x = self.width - (i + 1) * pixel_size
                y = self.height - (j + 1) * pixel_size
                self._draw_pixel(draw, x, y, border_color, pixel_size)

    def _draw_pixel(self, draw, x, y, color, pixel_size=None):
        """Draw a single pixel block with specified size."""
        if pixel_size is None:
            pixel_size = self.base_pixel_size

        draw.rectangle(
            [x, y, x + pixel_size - 1, y + pixel_size - 1],
            fill=color
        )

    def _draw_pixel_box(self, draw, grid_x, grid_y, size, color, pixel_size=None):
        """Draw a filled box of pixels with specified pixel size."""
        if pixel_size is None:
            pixel_size = self.base_pixel_size

        for i in range(size):
            for j in range(size):
                x = grid_x * self.base_pixel_size + i * pixel_size
                y = grid_y * self.base_pixel_size + j * pixel_size
                self._draw_pixel(draw, x, y, color, pixel_size)

    def _draw_pixel_box_outline(self, draw, grid_x, grid_y, size, color, pixel_size=None):
        """Draw a hollow box outline with specified pixel size."""
        if pixel_size is None:
            pixel_size = self.base_pixel_size

        for i in range(size):
            # Top and bottom edges
            x = grid_x * self.base_pixel_size + i * pixel_size
            y_top = grid_y * self.base_pixel_size
            y_bottom = grid_y * self.base_pixel_size + (size - 1) * pixel_size
            self._draw_pixel(draw, x, y_top, color, pixel_size)
            self._draw_pixel(draw, x, y_bottom, color, pixel_size)

        for j in range(1, size - 1):
            # Left and right edges
            x_left = grid_x * self.base_pixel_size
            x_right = grid_x * self.base_pixel_size + (size - 1) * pixel_size
            y = grid_y * self.base_pixel_size + j * pixel_size
            self._draw_pixel(draw, x_left, y, color, pixel_size)
            self._draw_pixel(draw, x_right, y, color, pixel_size)

    def _draw_pixel_cross(self, draw, grid_x, grid_y, size, color, pixel_size=None):
        """Draw a cross/plus shape with specified pixel size."""
        if pixel_size is None:
            pixel_size = self.base_pixel_size

        center = size // 2

        # Vertical line
        for j in range(size):
            x = grid_x * self.base_pixel_size + center * pixel_size
            y = grid_y * self.base_pixel_size + j * pixel_size
            self._draw_pixel(draw, x, y, color, pixel_size)

        # Horizontal line
        for i in range(size):
            x = grid_x * self.base_pixel_size + i * pixel_size
            y = grid_y * self.base_pixel_size + center * pixel_size
            self._draw_pixel(draw, x, y, color, pixel_size)
