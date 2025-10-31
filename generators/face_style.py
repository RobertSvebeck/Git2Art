"""Face art style - human face built from repository code.

Creates abstract human faces where facial features are determined by code metrics:
- Face shape based on repository size
- Eyes, nose, mouth based on file counts, commits, authors
- Hair style based on primary language
- Colors derived from repository palette
- Deterministic: same repo = same face
"""

from .base import BaseArtGenerator
from PIL import Image, ImageDraw
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
    STYLE_DESCRIPTION = "Human face built from repository code - features determined by metrics"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fingerprint = self.get_repo_fingerprint()
        self.palette = FacePalette.select_palette(self.fingerprint)
        self.seed = str(self.fingerprint['total_lines'])

    def generate_art(self, output_path='repo_art.png'):
        """Generate face artwork."""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img, 'RGBA')

        print(f"🎨 Generating face art...")
        print(f"📐 Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"📊 Repository metrics:")
        print(f"   Total lines: {self.fingerprint['total_lines']}")
        print(f"   Files: {len(self.fingerprint['files'])}")
        print(f"   Commits: {self.fingerprint['commit_count']}")
        print(f"   Authors: {len(self.fingerprint['authors'])}")

        # Calculate face proportions
        center_x = self.width // 2
        center_y = self.height // 2
        face_height = int(self.height * 0.7)
        face_width = int(face_height * 0.75)

        # Draw layers
        self._draw_background(draw)
        self._draw_face_base(draw, center_x, center_y, face_width, face_height)
        self._draw_eyes(draw, center_x, center_y, face_width, face_height)
        self._draw_nose(draw, center_x, center_y, face_width, face_height)
        self._draw_mouth(draw, center_x, center_y, face_width, face_height)
        self._draw_hair(draw, center_x, center_y, face_width, face_height)

        img.save(output_path, 'PNG')
        print(f"✅ Face art saved to {output_path}")

    def _draw_background(self, draw):
        """Draw gradient background."""
        bg_color = self._lighten_color(self.palette[0], 0.8)
        draw.rectangle([0, 0, self.width, self.height], fill=bg_color)

    def _draw_face_base(self, draw, cx, cy, fw, fh):
        """Draw face outline and skin."""
        # Determine face shape based on total lines
        total_lines = self.fingerprint['total_lines']

        if total_lines < 1000:
            # Small repo = round face
            draw.ellipse([cx - fw//2, cy - fh//2, cx + fw//2, cy + fh//2],
                        fill=self._get_skin_tone(), outline=None)
        elif total_lines < 5000:
            # Medium repo = oval face
            draw.ellipse([cx - fw//2, cy - fh//2, cx + fw//2, cy + fh//2],
                        fill=self._get_skin_tone(), outline=None)
        else:
            # Large repo = angular face (rounded rectangle)
            self._draw_rounded_rectangle(draw,
                                        [cx - fw//2, cy - fh//2, cx + fw//2, cy + fh//2],
                                        radius=50, fill=self._get_skin_tone())

    def _draw_eyes(self, draw, cx, cy, fw, fh):
        """Draw eyes based on file count."""
        file_count = len(self.fingerprint['files'])

        # Eye size based on file count
        eye_size = min(fw // 10, max(20, file_count * 2))

        # Eye positions (at 50% height, 30% from center)
        eye_y = cy - fh // 8
        eye_spacing = fw // 4

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing

        # Eye color from palette
        eye_color = self.palette[1]

        # Determine eye shape based on file types
        web_ratio = self._get_file_type_ratio(['.html', '.css', '.js', '.jsx', '.ts', '.tsx'])

        if web_ratio > 0.3:
            # Round eyes for frontend-heavy repos
            self._draw_round_eye(draw, left_eye_x, eye_y, eye_size, eye_color)
            self._draw_round_eye(draw, right_eye_x, eye_y, eye_size, eye_color)
        else:
            # Almond eyes for backend-heavy repos
            self._draw_almond_eye(draw, left_eye_x, eye_y, eye_size, eye_color)
            self._draw_almond_eye(draw, right_eye_x, eye_y, eye_size, eye_color)

    def _draw_nose(self, draw, cx, cy, fw, fh):
        """Draw nose based on commit count."""
        commit_count = self.fingerprint['commit_count']

        # Nose size based on commits
        nose_height = min(fh // 6, max(30, commit_count * 2))
        nose_width = nose_height // 3

        # Nose position (at 60% height)
        nose_y = cy

        # Simple triangular nose
        nose_color = self._darken_color(self._get_skin_tone(), 0.1)
        points = [
            (cx, nose_y - nose_height // 2),
            (cx - nose_width // 2, nose_y + nose_height // 2),
            (cx + nose_width // 2, nose_y + nose_height // 2)
        ]
        draw.polygon(points, fill=nose_color)

    def _draw_mouth(self, draw, cx, cy, fw, fh):
        """Draw mouth based on author count."""
        author_count = len(self.fingerprint['authors'])

        # More authors = bigger smile
        smile_width = min(fw // 3, max(40, author_count * 10))
        mouth_y = cy + fh // 4

        # Draw smile curve
        mouth_color = self.palette[2]

        if author_count > 3:
            # Happy face - upward curve
            self._draw_smile(draw, cx, mouth_y, smile_width, mouth_color, happy=True)
        elif author_count > 1:
            # Neutral face - straight line
            draw.line([cx - smile_width // 2, mouth_y, cx + smile_width // 2, mouth_y],
                     fill=mouth_color, width=4)
        else:
            # Solo developer - slight smile
            self._draw_smile(draw, cx, mouth_y, smile_width // 2, mouth_color, happy=True)

    def _draw_hair(self, draw, cx, cy, fw, fh):
        """Draw hair based on primary language and file diversity."""
        # Hair color from palette
        hair_color = self.palette[0]

        # Hair style based on primary language
        file_types = self.fingerprint['file_types']
        primary_ext = max(file_types.items(), key=lambda x: x[1])[0] if file_types else '.py'

        # Hair region (top 40% of head)
        hair_top = cy - fh // 2
        hair_bottom = cy - fh // 4

        # Different hair styles for different languages
        if primary_ext in ['.py', '.rb']:
            # Curly hair (multiple arcs)
            self._draw_curly_hair(draw, cx, hair_top, fw, hair_color)
        elif primary_ext in ['.js', '.ts', '.jsx', '.tsx']:
            # Spiky hair (triangles)
            self._draw_spiky_hair(draw, cx, hair_top, fw, hair_color)
        elif primary_ext in ['.java', '.cpp', '.c']:
            # Short straight hair (rectangle)
            draw.rectangle([cx - fw // 2, hair_top, cx + fw // 2, hair_bottom],
                          fill=hair_color)
        else:
            # Wavy hair (sine waves)
            self._draw_wavy_hair(draw, cx, hair_top, fw, hair_color)

    # Helper methods for drawing specific elements

    def _draw_round_eye(self, draw, x, y, size, color):
        """Draw round eye."""
        # White of eye
        draw.ellipse([x - size, y - size, x + size, y + size], fill='white', outline='black')
        # Iris
        draw.ellipse([x - size // 2, y - size // 2, x + size // 2, y + size // 2],
                    fill=color, outline=None)
        # Pupil
        draw.ellipse([x - size // 4, y - size // 4, x + size // 4, y + size // 4],
                    fill='black', outline=None)

    def _draw_almond_eye(self, draw, x, y, size, color):
        """Draw almond-shaped eye."""
        points = [
            (x - size, y),
            (x - size // 2, y - size // 2),
            (x + size, y),
            (x + size // 2, y + size // 2)
        ]
        draw.polygon(points, fill='white', outline='black')
        # Iris
        draw.ellipse([x - size // 3, y - size // 3, x + size // 3, y + size // 3],
                    fill=color, outline=None)
        # Pupil
        draw.ellipse([x - size // 6, y - size // 6, x + size // 6, y + size // 6],
                    fill='black', outline=None)

    def _draw_smile(self, draw, cx, cy, width, color, happy=True):
        """Draw smile curve."""
        curve_height = width // 4
        control_y = cy + curve_height if happy else cy - curve_height

        # Draw arc using multiple line segments
        points = []
        for i in range(20):
            t = i / 19.0
            # Quadratic bezier curve
            x = cx - width // 2 + t * width
            y = cy + 2 * (1 - t) * t * (control_y - cy)
            points.append((x, y))

        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=color, width=4)

    def _draw_curly_hair(self, draw, cx, top_y, width, color):
        """Draw curly hair with overlapping circles."""
        num_curls = DeterministicRandom.randint(self.seed, 100, 8, 12)
        curl_size = width // 8

        for i in range(num_curls):
            x = DeterministicRandom.uniform(self.seed, 100 + i, cx - width // 2, cx + width // 2)
            y = DeterministicRandom.uniform(self.seed, 200 + i, top_y, top_y + width // 4)
            draw.ellipse([x - curl_size, y - curl_size, x + curl_size, y + curl_size],
                        fill=color, outline=None)

    def _draw_spiky_hair(self, draw, cx, top_y, width, color):
        """Draw spiky hair with triangles."""
        num_spikes = DeterministicRandom.randint(self.seed, 300, 6, 10)
        spike_height = width // 6
        spike_width = width // num_spikes

        for i in range(num_spikes):
            x = cx - width // 2 + i * spike_width
            points = [
                (x, top_y + spike_height),
                (x + spike_width // 2, top_y),
                (x + spike_width, top_y + spike_height)
            ]
            draw.polygon(points, fill=color, outline=None)

    def _draw_wavy_hair(self, draw, cx, top_y, width, color):
        """Draw wavy hair with sine curves."""
        # Draw base rectangle
        draw.rectangle([cx - width // 2, top_y, cx + width // 2, top_y + width // 4],
                      fill=color)

        # Add waves on top
        wave_color = self._lighten_color(color, 0.2)
        num_waves = 3
        for w in range(num_waves):
            points = []
            y_offset = top_y + w * 20
            for i in range(50):
                x = cx - width // 2 + (i / 49.0) * width
                y = y_offset + math.sin(i * 0.3) * 10
                points.append((x, y))

            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=wave_color, width=3)

    def _draw_rounded_rectangle(self, draw, bbox, radius, fill):
        """Draw rectangle with rounded corners."""
        x1, y1, x2, y2 = bbox
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + 2*radius, y1 + 2*radius], fill=fill)
        draw.ellipse([x2 - 2*radius, y1, x2, y1 + 2*radius], fill=fill)
        draw.ellipse([x1, y2 - 2*radius, x1 + 2*radius, y2], fill=fill)
        draw.ellipse([x2 - 2*radius, y2 - 2*radius, x2, y2], fill=fill)

    def _get_skin_tone(self):
        """Generate skin tone from palette."""
        base_color = self.palette[0]
        # Lighten and desaturate for skin-like tone
        h, s, v = colorsys.rgb_to_hsv(base_color[0]/255, base_color[1]/255, base_color[2]/255)
        # Shift to warm tones and lighten
        h = 0.08  # Orange-ish hue for skin
        s = 0.3   # Low saturation
        v = 0.85  # High brightness
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def _lighten_color(self, color, factor=0.5):
        """Lighten a color."""
        return tuple(min(255, int(c + (255 - c) * factor)) for c in color)

    def _darken_color(self, color, factor=0.1):
        """Darken a color."""
        return tuple(max(0, int(c * (1 - factor))) for c in color)

    def _get_file_type_ratio(self, extensions):
        """Get ratio of files with given extensions."""
        total = self.fingerprint['total_lines']
        if total == 0:
            return 0
        matching = sum(self.fingerprint['file_types'].get(ext, 0) for ext in extensions)
        return matching / total
