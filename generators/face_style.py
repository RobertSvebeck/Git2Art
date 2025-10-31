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
        """Draw eyes with varied organic shapes and positions."""
        file_count = len(self.fingerprint['files'])

        # Eye size based on file count
        eye_size = int(fw * 0.08 * min(1.5, 0.7 + file_count / 50))

        # Base eye positions with variations
        base_eye_y = cy - fh // 6
        base_spacing = fw // 4

        # Determine eye styles based on repo characteristics
        left_style = DeterministicRandom.randint(self.seed, 5000, 0, 4)
        right_style = DeterministicRandom.randint(self.seed, 5001, 0, 4)

        # VARIED POSITIONS for asymmetry
        # Eye spacing variation (closer or farther apart)
        spacing_mult = DeterministicRandom.uniform(self.seed, 5010, 0.7, 1.3)

        # Left eye position (horizontal and vertical offsets)
        left_x = int(cx - base_spacing * spacing_mult + DeterministicRandom.randint(self.seed, 5011, -fw//15, fw//15))
        left_y = int(base_eye_y + DeterministicRandom.randint(self.seed, 5012, -fh//10, fh//10))

        # Right eye position (independent offsets for asymmetry)
        right_x = int(cx + base_spacing * spacing_mult + DeterministicRandom.randint(self.seed, 5013, -fw//15, fw//15))
        right_y = int(base_eye_y + DeterministicRandom.randint(self.seed, 5014, -fh//10, fh//10))

        # LEFT EYE - Multiple possible shapes
        self._draw_varied_eye(draw, left_x, left_y, eye_size, left_style, self.palette[1])

        # RIGHT EYE - Different shape and position
        self._draw_varied_eye(draw, right_x, right_y, eye_size, right_style, self.palette[2])

    def _draw_varied_eye(self, draw, x, y, size, style, color):
        """Draw eye with one of several possible shapes."""
        if style == 0:
            # Circular eye
            draw.ellipse([x - size, y - size, x + size, y + size], fill=(255, 255, 255))
            draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], fill=color)
            draw.ellipse([x - size//4, y - size//4, x + size//4, y + size//4], fill=(40, 40, 50))

        elif style == 1:
            # Almond/diamond shape
            points = [
                (x - size, y),
                (x, y - size//2),
                (x + size, y),
                (x, y + size//2)
            ]
            draw.polygon(points, fill=color)
            draw.ellipse([x - size//3, y - size//3, x + size//3, y + size//3], fill=(255, 255, 255))

        elif style == 2:
            # Organic blob eye
            blob_points = self._create_organic_blob(x, y, size, self.seed, 5100)
            draw.polygon(blob_points, fill=color)
            draw.ellipse([x - size//3, y - size//3, x + size//3, y + size//3], fill=(255, 255, 255))

        elif style == 3:
            # Square/rectangular eye
            draw.rectangle([x - size, y - size//2, x + size, y + size//2], fill=color)
            draw.ellipse([x - size//3, y - size//3, x + size//3, y + size//3], fill=(255, 255, 255))

        else:
            # Curved crescent shape
            points = []
            for i in range(10):
                angle = -math.pi/2 + (i / 9) * math.pi
                radius = size
                px = x + math.cos(angle) * radius
                py = y + math.sin(angle) * radius
                points.append((px, py))
            for i in range(10):
                angle = math.pi/2 - (i / 9) * math.pi
                radius = size * 0.6
                px = x + math.cos(angle) * radius
                py = y + math.sin(angle) * radius
                points.append((px, py))
            draw.polygon(points, fill=color)

    def _draw_nose_profile(self, draw, cx, cy, fw, fh):
        """Draw nose with varied shapes and positions."""
        commit_count = self.fingerprint['commit_count']

        # Nose size based on commits
        nose_size = int(fw * 0.10 * min(1.5, 0.7 + commit_count / 100))
        nose_color = self.palette[2]

        # VARIED POSITION for nose
        nose_x = int(cx + DeterministicRandom.randint(self.seed, 5900, -fw//12, fw//12))
        nose_y = int(cy + DeterministicRandom.randint(self.seed, 5901, -fh//12, fh//12))

        # Determine nose style
        nose_style = DeterministicRandom.randint(self.seed, 6000, 0, 4)

        if nose_style == 0:
            # Triangle nose
            points = [
                (nose_x, nose_y),
                (nose_x - nose_size//3, nose_y + nose_size),
                (nose_x + nose_size//3, nose_y + nose_size)
            ]
            draw.polygon(points, fill=nose_color)

        elif nose_style == 1:
            # Vertical rectangle
            draw.rectangle([nose_x - nose_size//4, nose_y, nose_x + nose_size//4, nose_y + nose_size],
                          fill=nose_color)

        elif nose_style == 2:
            # L-shaped profile nose
            points = [
                (nose_x - nose_size//3, nose_y + nose_size//3),
                (nose_x, nose_y),
                (nose_x + nose_size//4, nose_y + nose_size//2),
                (nose_x + nose_size//4, nose_y + nose_size),
                (nose_x - nose_size//3, nose_y + nose_size)
            ]
            draw.polygon(points, fill=nose_color)

        elif nose_style == 3:
            # Organic blob nose
            blob_points = self._create_organic_blob(nose_x, nose_y + nose_size//2, nose_size, self.seed, 6100)
            draw.polygon(blob_points, fill=nose_color)

        else:
            # Curved hook nose
            points = []
            for i in range(8):
                t = i / 7
                x = nose_x - nose_size//4 + math.sin(t * math.pi) * nose_size//3
                y = nose_y + t * nose_size
                points.append((x, y))
            for i in range(4):
                t = i / 3
                x = nose_x - nose_size//4 + nose_size//3 - t * nose_size//3
                y = nose_y + nose_size - t * nose_size//4
                points.append((x, y))
            draw.polygon(points, fill=nose_color)

    def _draw_expressive_mouth(self, draw, cx, cy, fw, fh):
        """Draw mouth with varied shapes and positions."""
        author_count = len(self.fingerprint['authors'])

        # VARIED POSITION for mouth
        base_mouth_y = cy + fh // 3
        mouth_x = int(cx + DeterministicRandom.randint(self.seed, 6900, -fw//15, fw//15))
        mouth_y = int(base_mouth_y + DeterministicRandom.randint(self.seed, 6901, -fh//12, fh//12))

        mouth_width = int(fw * 0.35 * min(1.5, 0.8 + author_count / 5))
        mouth_color = self.palette[3] if len(self.palette) > 3 else self.palette[2]

        # Determine mouth style
        mouth_style = DeterministicRandom.randint(self.seed, 7000, 0, 4)

        # More authors = happier expression
        happiness = min(1.0, 0.3 + author_count / 10)

        if mouth_style == 0:
            # Curved smile line
            curve_strength = 20 + int(happiness * 40)
            points = []
            for i in range(20):
                t = i / 19
                x = mouth_x - mouth_width // 2 + t * mouth_width
                y = mouth_y + math.sin(t * math.pi) * curve_strength
                points.append((x, y))
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=mouth_color, width=6)

        elif mouth_style == 1:
            # Open mouth (ellipse)
            height = int(mouth_width * 0.3 * happiness)
            draw.ellipse([mouth_x - mouth_width//2, mouth_y - height//2,
                         mouth_x + mouth_width//2, mouth_y + height//2],
                        fill=mouth_color)

        elif mouth_style == 2:
            # Wavy organic mouth
            points = []
            for i in range(15):
                t = i / 14
                x = mouth_x - mouth_width // 2 + t * mouth_width
                y = mouth_y + math.sin(t * math.pi * 3) * 10 + happiness * 20
                points.append((x, y))
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=mouth_color, width=8)

        elif mouth_style == 3:
            # Geometric angular mouth
            height = int(15 + happiness * 25)
            points = [
                (mouth_x - mouth_width//2, mouth_y),
                (mouth_x - mouth_width//4, mouth_y + height),
                (mouth_x, mouth_y + height * 0.7),
                (mouth_x + mouth_width//4, mouth_y + height),
                (mouth_x + mouth_width//2, mouth_y)
            ]
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=mouth_color, width=6)

        else:
            # Organic blob mouth
            blob_width = mouth_width * 0.8
            blob_height = int(20 + happiness * 30)
            blob_points = []
            for i in range(12):
                angle = (i / 12) * 2 * math.pi
                r_x = blob_width / 2 * (0.8 + DeterministicRandom.uniform(self.seed, 7100 + i, 0, 0.4))
                r_y = blob_height / 2 * (0.8 + DeterministicRandom.uniform(self.seed, 7200 + i, 0, 0.4))
                px = mouth_x + math.cos(angle) * r_x
                py = mouth_y + math.sin(angle) * r_y
                blob_points.append((px, py))
            draw.polygon(blob_points, fill=mouth_color)

    def _draw_playful_details(self, draw, cx, cy, fw, fh):
        """Add varied hair styles and decorative elements."""
        file_types = self.fingerprint['file_types']
        primary_ext = max(file_types.items(), key=lambda x: x[1])[0] if file_types else '.py'

        # Determine hair style
        hair_style = DeterministicRandom.randint(self.seed, 8000, 0, 4)
        hair_color = self.palette[0]

        # VARIED POSITION for hair
        base_hair_top = cy - fh // 2
        hair_top = int(base_hair_top + DeterministicRandom.randint(self.seed, 7950, -fh//15, fh//20))
        hair_x_offset = DeterministicRandom.randint(self.seed, 7951, -fw//12, fw//12)

        if hair_style == 0:
            # Circular tufts (classic)
            num_tufts = DeterministicRandom.randint(self.seed, 8100, 4, 7)
            for i in range(num_tufts):
                x_pos = cx + hair_x_offset - fw//3 + i * (fw * 0.666 / num_tufts)
                size = DeterministicRandom.uniform(self.seed, 8200 + i, 20, 40)
                draw.ellipse([x_pos - size, hair_top - size, x_pos + size, hair_top + size],
                            fill=hair_color)

        elif hair_style == 1:
            # Spiky triangles
            num_spikes = DeterministicRandom.randint(self.seed, 8300, 5, 9)
            for i in range(num_spikes):
                x_pos = cx + hair_x_offset - fw//3 + i * (fw * 0.666 / num_spikes)
                spike_height = DeterministicRandom.uniform(self.seed, 8400 + i, 30, 60)
                spike_width = DeterministicRandom.uniform(self.seed, 8500 + i, 20, 35)
                points = [
                    (x_pos, hair_top - spike_height),
                    (x_pos - spike_width/2, hair_top),
                    (x_pos + spike_width/2, hair_top)
                ]
                draw.polygon(points, fill=hair_color)

        elif hair_style == 2:
            # Organic blobs
            num_blobs = DeterministicRandom.randint(self.seed, 8600, 4, 8)
            for i in range(num_blobs):
                x_pos = cx + hair_x_offset - fw//2 + DeterministicRandom.uniform(self.seed, 8700 + i, 0, fw)
                y_pos = hair_top + DeterministicRandom.uniform(self.seed, 8800 + i, -30, 20)
                size = DeterministicRandom.uniform(self.seed, 8900 + i, 25, 45)
                blob_points = self._create_organic_blob(x_pos, y_pos, size, self.seed, 9000 + i)
                draw.polygon(blob_points, fill=hair_color)

        elif hair_style == 3:
            # Wavy lines
            num_waves = 3
            for w in range(num_waves):
                points = []
                y_offset = hair_top - w * 15
                for i in range(20):
                    t = i / 19
                    x = cx + hair_x_offset - fw//2 + t * fw
                    y = y_offset + math.sin(t * math.pi * 4) * 15
                    points.append((x, y))
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i + 1]], fill=hair_color, width=8)

        else:
            # Square/rectangular blocks
            num_blocks = DeterministicRandom.randint(self.seed, 9100, 4, 7)
            for i in range(num_blocks):
                x_pos = cx + hair_x_offset - fw//3 + i * (fw * 0.666 / num_blocks)
                w = DeterministicRandom.uniform(self.seed, 9200 + i, 15, 30)
                h = DeterministicRandom.uniform(self.seed, 9300 + i, 25, 50)
                draw.rectangle([x_pos - w, hair_top - h, x_pos + w, hair_top],
                              fill=hair_color)

        # Decorative elements around face
        num_decorations = DeterministicRandom.randint(self.seed, 9400, 3, 6)
        for i in range(num_decorations):
            angle = (i / num_decorations) * 2 * math.pi + DeterministicRandom.uniform(self.seed, 9500 + i, -0.5, 0.5)
            distance = fw * DeterministicRandom.uniform(self.seed, 9600 + i, 0.6, 0.8)
            x = int(cx + math.cos(angle) * distance)
            y = int(cy + math.sin(angle) * distance)
            size = DeterministicRandom.uniform(self.seed, 9700 + i, 15, 35)
            color = self.palette[(i + 2) % len(self.palette)]

            # Varied decoration shapes
            deco_type = DeterministicRandom.randint(self.seed, 9800 + i, 0, 2)
            if deco_type == 0:
                draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
            elif deco_type == 1:
                draw.rectangle([x - size, y - size, x + size, y + size], fill=color)
            else:
                blob_points = self._create_organic_blob(x, y, size, self.seed, 9900 + i)
                draw.polygon(blob_points, fill=color)

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
