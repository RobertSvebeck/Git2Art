"""Cubist Face art style - playful abstract faces from repository code.

Creates expressive faces inspired by Picasso and Matisse:
- Multiple viewpoints in one face (profile + frontal combined)
- Bold, vibrant color blocks (not transparent)
- Simple shapes with strong contrasts
- Playful asymmetry and personality
- Eyes, nose, mouth distributed creatively
- Warm, human, joyful energy
- Inspired by Picasso's cubism + Matisse's cutouts
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


class FacePalette:
    """Generate harmonious color palettes for face style."""

    # Curated palettes based on repository type
    PALETTES = {
        'python': [(41, 128, 185), (52, 152, 219), (26, 188, 156), (22, 160, 133)],
        'javascript': [(241, 196, 15), (243, 156, 18), (230, 126, 34), (211, 84, 0)],
        'java': [(244, 67, 54), (233, 30, 99), (156, 39, 176), (103, 58, 183)],
        'ruby': [(231, 76, 60), (192, 57, 43), (241, 148, 138), (245, 183, 177)],
        'go': [(0, 188, 212), (0, 172, 193), (0, 151, 167), (0, 131, 143)],
        'rust': [(255, 87, 34), (244, 81, 30), (230, 74, 25), (216, 67, 21)],
        'default': [(155, 89, 182), (142, 68, 173), (52, 73, 94), (44, 62, 80)]
    }

    @staticmethod
    def select_palette(fingerprint):
        """Select palette based on repository type."""
        file_types = fingerprint['file_types']

        if file_types.get('.py', 0) > 0:
            palette_name = 'python'
        elif file_types.get('.js', 0) + file_types.get('.jsx', 0) + file_types.get('.ts', 0) > 0:
            palette_name = 'javascript'
        elif file_types.get('.java', 0) > 0:
            palette_name = 'java'
        elif file_types.get('.rb', 0) > 0:
            palette_name = 'ruby'
        elif file_types.get('.go', 0) > 0:
            palette_name = 'go'
        elif file_types.get('.rs', 0) > 0:
            palette_name = 'rust'
        else:
            palette_name = 'default'

        return FacePalette.PALETTES[palette_name]


class FaceStyleGenerator(BaseArtGenerator):
    """Generate human face art from repository code metrics."""

    STYLE_NAME = "face"
    STYLE_DESCRIPTION = "Expressionist face built from code - bold strokes and distorted features"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fingerprint = self.get_repo_fingerprint()
        self.palette = FacePalette.select_palette(self.fingerprint)
        self.seed = str(self.fingerprint['total_lines'])

    def generate_art(self, output_path='repo_art.png'):
        """Generate cubist face artwork."""
        # Base color from palette (will be covered by organic shapes)
        base = self.palette[0]
        base_color = tuple(min(255, int(c + (255 - c) * 0.7)) for c in base)
        img = Image.new('RGB', (self.width, self.height), base_color)
        draw = ImageDraw.Draw(img, 'RGBA')

        print(f"Generating playful cubist face art...")
        print(f"Canvas: {self.width}x{self.height}")
        print(f"Style: Picasso + Matisse inspired")
        print(f"Features from code:")
        print(f"   {self.fingerprint['total_lines']} lines -> complexity")
        print(f"   {len(self.fingerprint['files'])} files -> eye style")
        print(f"   {self.fingerprint['commit_count']} commits -> expression")
        print(f"   {len(self.fingerprint['authors'])} authors -> mood")

        # Calculate face proportions
        center_x = self.width // 2
        center_y = self.height // 2
        face_height = int(self.height * 0.65)
        face_width = int(face_height * 0.8)

        # Draw solid, bold shapes
        self._draw_background_shapes(draw)
        self._draw_face_planes(draw, center_x, center_y, face_width, face_height)
        self._draw_cubist_eyes(draw, center_x, center_y, face_width, face_height)
        self._draw_nose_profile(draw, center_x, center_y, face_width, face_height)
        self._draw_expressive_mouth(draw, center_x, center_y, face_width, face_height)
        self._draw_playful_details(draw, center_x, center_y, face_width, face_height)

        # Light blur to soften edges slightly (not ghostly)
        img = img.filter(ImageFilter.GaussianBlur(radius=2))

        img.save(output_path, 'PNG')
        print(f"Cubist face saved to {output_path}")

    def _draw_background_shapes(self, draw):
        """Draw organic flowing background shapes - full coverage."""
        # Fill entire canvas with organic flowing shapes
        num_large_shapes = 6

        for i in range(num_large_shapes):
            color = self.palette[i % len(self.palette)]

            # Large organic flowing shapes
            x = DeterministicRandom.uniform(self.seed, 400 + i, -self.width * 0.2, self.width * 1.2)
            y = DeterministicRandom.uniform(self.seed, 410 + i, -self.height * 0.2, self.height * 1.2)
            size = DeterministicRandom.uniform(self.seed, 420 + i, self.width * 0.4, self.width * 0.8)

            # Create flowing organic blob
            points = self._create_organic_blob(x, y, size, self.seed, 430 + i)
            draw.polygon(points, fill=color)

        # Add more smaller shapes to fill gaps
        for i in range(8):
            color = self.palette[i % len(self.palette)]
            x = DeterministicRandom.uniform(self.seed, 500 + i, 0, self.width)
            y = DeterministicRandom.uniform(self.seed, 510 + i, 0, self.height)
            size = DeterministicRandom.uniform(self.seed, 520 + i, self.width * 0.15, self.width * 0.35)

            points = self._create_organic_blob(x, y, size, self.seed, 530 + i)
            draw.polygon(points, fill=color)

    def _draw_face_planes(self, draw, cx, cy, fw, fh):
        """Draw face as bold flat planes like Picasso cubism."""
        # Face built entirely from angular planes (no base ellipse)
        # Use lighter versions of palette for skin-like tones

        # More planes for a complete face structure
        planes = [
            # Left cheek (large)
            {
                'points': [
                    (cx - fw//2, cy - fh//4),
                    (cx - fw//6, cy - fh//3),
                    (cx - fw//6, cy + fh//4),
                    (cx - fw//2, cy + fh//5)
                ],
                'color': self._lighten_color(self.palette[0], 0.5)
            },
            # Right cheek (large)
            {
                'points': [
                    (cx + fw//6, cy - fh//3),
                    (cx + fw//2, cy - fh//4),
                    (cx + fw//2, cy + fh//5),
                    (cx + fw//6, cy + fh//4)
                ],
                'color': self._lighten_color(self.palette[1], 0.5)
            },
            # Forehead plane
            {
                'points': [
                    (cx - fw//3, cy - fh//2),
                    (cx + fw//3, cy - fh//2),
                    (cx + fw//4, cy - fh//6),
                    (cx - fw//4, cy - fh//6)
                ],
                'color': self.palette[0]
            },
            # Center face plane
            {
                'points': [
                    (cx - fw//6, cy - fh//4),
                    (cx + fw//6, cy - fh//4),
                    (cx + fw//5, cy + fh//5),
                    (cx - fw//5, cy + fh//5)
                ],
                'color': self._lighten_color(self.palette[2], 0.6)
            },
            # Chin plane
            {
                'points': [
                    (cx - fw//4, cy + fh//4),
                    (cx + fw//4, cy + fh//4),
                    (cx + fw//5, cy + fh//2),
                    (cx - fw//5, cy + fh//2)
                ],
                'color': self.palette[1]
            },
            # Side profile plane
            {
                'points': [
                    (cx - fw//3, cy - fh//6),
                    (cx - fw//8, cy - fh//4),
                    (cx - fw//8, cy + fh//6),
                    (cx - fw//3, cy + fh//8)
                ],
                'color': self.palette[2]
            }
        ]

        for plane in planes:
            draw.polygon(plane['points'], fill=plane['color'])

    def _draw_cubist_eyes(self, draw, cx, cy, fw, fh):
        """Draw eyes with Picasso-style multiple viewpoints."""
        file_count = len(self.fingerprint['files'])

        # Eye size and style based on file count
        eye_size = int(fw * 0.08)
        eye_y = cy - fh // 6

        # LEFT EYE - Profile view (almond shaped)
        left_x = cx - fw // 4
        # Almond shape for left eye
        points = [
            (left_x - eye_size, eye_y),
            (left_x, eye_y - eye_size//2),
            (left_x + eye_size, eye_y),
            (left_x, eye_y + eye_size//2)
        ]
        draw.polygon(points, fill=(50, 50, 60))
        # Highlight
        draw.ellipse([left_x - eye_size//3, eye_y - eye_size//3,
                     left_x + eye_size//3, eye_y + eye_size//3],
                    fill=(255, 255, 255))

        # RIGHT EYE - Frontal view (round)
        right_x = cx + fw // 4
        # Full round eye (no border)
        draw.ellipse([right_x - eye_size, eye_y - eye_size,
                     right_x + eye_size, eye_y + eye_size],
                    fill=(255, 255, 255))
        # Iris
        iris_size = eye_size // 2
        iris_color = self.palette[1]
        draw.ellipse([right_x - iris_size, eye_y - iris_size,
                     right_x + iris_size, eye_y + iris_size],
                    fill=iris_color)
        # Pupil
        pupil_size = eye_size // 4
        draw.ellipse([right_x - pupil_size, eye_y - pupil_size,
                     right_x + pupil_size, eye_y + pupil_size],
                    fill=(30, 30, 40))

    def _draw_nose_profile(self, draw, cx, cy, fw, fh):
        """Draw nose as simple bold shape."""
        # Simple triangular or L-shaped nose (profile + frontal)
        nose_color = self._darken_color(self._lighten_color(self.palette[0], 0.6), 0.15)

        # Triangle for nose
        nose_size = int(fw * 0.12)
        points = [
            (cx, cy),
            (cx - nose_size//3, cy + nose_size),
            (cx + nose_size//3, cy + nose_size)
        ]
        draw.polygon(points, fill=nose_color)

        # Add nostril dots for character
        nostril_y = cy + nose_size * 0.8
        nostril_size = nose_size // 8
        draw.ellipse([cx - nose_size//4 - nostril_size, nostril_y - nostril_size,
                     cx - nose_size//4 + nostril_size, nostril_y + nostril_size],
                    fill=(60, 60, 70))
        draw.ellipse([cx + nose_size//4 - nostril_size, nostril_y - nostril_size,
                     cx + nose_size//4 + nostril_size, nostril_y + nostril_size],
                    fill=(60, 60, 70))

    def _draw_expressive_mouth(self, draw, cx, cy, fw, fh):
        """Draw bold expressive mouth with personality."""
        author_count = len(self.fingerprint['authors'])

        mouth_y = cy + fh // 3
        mouth_width = int(fw * 0.35)

        # More authors = happier smile
        if author_count > 2:
            # Big smile - curve upward
            curve_strength = 30 + author_count * 5
        else:
            # Neutral or slight smile
            curve_strength = 15

        # Bold curved line for mouth
        mouth_color = self.palette[2]
        points = []
        num_points = 20
        for i in range(num_points):
            t = i / (num_points - 1)
            x = cx - mouth_width // 2 + t * mouth_width
            y = mouth_y + math.sin(t * math.pi) * curve_strength
            points.append((x, y))

        # Draw thick mouth line
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=mouth_color, width=6)

        # Add lip detail
        lip_y = mouth_y - 5
        draw.ellipse([cx - mouth_width//6, lip_y - 8,
                     cx + mouth_width//6, lip_y + 8],
                    fill=self._darken_color(mouth_color, 0.2))

    def _draw_playful_details(self, draw, cx, cy, fw, fh):
        """Add playful Matisse-style decorative elements."""
        # Hair/crown as bold shapes above head
        hair_color = self.palette[0]

        # Simple curved shapes for hair
        hair_top = cy - fh // 2
        num_hair_elements = 5

        for i in range(num_hair_elements):
            x_pos = cx - fw//3 + i * (fw * 0.666 / num_hair_elements)
            size = DeterministicRandom.uniform(self.seed, 2700 + i, 20, 40)

            # Circle for hair tuft
            draw.ellipse([x_pos - size, hair_top - size,
                         x_pos + size, hair_top + size],
                        fill=hair_color)

        # Add some playful decorative circles around face (like Matisse)
        for i in range(4):
            angle = (i / 4) * 2 * math.pi
            distance = fw * 0.7
            x = int(cx + math.cos(angle) * distance)
            y = int(cy + math.sin(angle) * distance)
            size = DeterministicRandom.uniform(self.seed, 3200 + i, 15, 30)
            color = self.palette[(i + 2) % len(self.palette)]

            draw.ellipse([x - size, y - size, x + size, y + size],
                        fill=color)

    # Helper methods

    def _create_organic_blob(self, cx, cy, size, seed, offset):
        """Create irregular organic blob shape."""
        points = []
        num_points = 12

        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            radius_var = DeterministicRandom.uniform(seed, offset + i, 0.7, 1.3)
            radius = size / 2 * radius_var

            px = cx + math.cos(angle) * radius
            py = cy + math.sin(angle) * radius
            points.append((px, py))

        return points

    def _lighten_color(self, color, factor=0.5):
        """Lighten a color."""
        return tuple(min(255, int(c + (255 - c) * factor)) for c in color)

    def _darken_color(self, color, factor=0.1):
        """Darken a color."""
        return tuple(max(0, int(c * (1 - factor))) for c in color)
