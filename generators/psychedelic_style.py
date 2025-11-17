"""Psychedelic art style - Vibrant, flowing curves with NO straight lines.

This style transforms the expressionist approach into a trippy, fluid world:
- NO straight lines anywhere - only curves and organic flows
- Vibrant psychedelic colors with high saturation
- Concentric circles, spirals, waves, and undulating patterns
- Overlapping transparent shapes creating color-mixing effects
- Hypnotic patterns and infinite-seeming flows
- Kaleidoscopic symmetry
"""

from .base import BaseArtGenerator
from PIL import Image, ImageDraw, ImageFilter
import colorsys
import math
import random
import hashlib


class DeterministicRandom:
    """Deterministic random number generator based on hash values."""

    @staticmethod
    def from_hash(hash_string, index=0):
        """Generate a deterministic random value from a hash string and index."""
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
        """Deterministic integer in range [min_val, max_val] inclusive."""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        return int(min_val + rand_val * (max_val - min_val + 1))

    @staticmethod
    def choice(hash_string, index, choices):
        """Deterministic choice from list."""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        idx = int(rand_val * len(choices))
        return choices[min(idx, len(choices) - 1)]


class PsychedelicPalette:
    """Generate vibrant, trippy color palettes."""

    VIBRANT_PALETTES = {
        'python': {
            'base': [(0, 255, 200), (0, 150, 255), (150, 100, 255), (255, 50, 200)],
            'accents': [(255, 255, 100), (100, 255, 150)],
        },
        'javascript': {
            'base': [(255, 100, 0), (255, 0, 150), (255, 200, 0), (0, 255, 100)],
            'accents': [(0, 200, 255), (255, 0, 255)],
        },
        'php': {
            'base': [(200, 0, 255), (0, 255, 255), (255, 0, 100), (150, 255, 0)],
            'accents': [(255, 100, 255), (0, 255, 200)],
        },
        'java': {
            'base': [(255, 0, 100), (0, 255, 150), (150, 0, 255), (255, 150, 0)],
            'accents': [(0, 100, 255), (255, 255, 0)],
        },
        'ruby': {
            'base': [(255, 50, 100), (255, 0, 200), (0, 255, 100), (200, 0, 255)],
            'accents': [(100, 255, 200), (255, 200, 0)],
        },
        'systems': {
            'base': [(0, 255, 100), (100, 0, 255), (255, 100, 0), (0, 150, 255)],
            'accents': [(255, 0, 150), (100, 255, 0)],
        },
        'data': {
            'base': [(0, 255, 150), (150, 0, 255), (255, 100, 0), (0, 100, 255)],
            'accents': [(200, 255, 0), (255, 0, 100)],
        },
        'cpp': {
            'base': [(100, 255, 0), (0, 200, 255), (255, 0, 200), (200, 100, 255)],
            'accents': [(255, 150, 0), (0, 255, 200)],
        },
        'mobile': {
            'base': [(255, 100, 200), (100, 255, 100), (100, 100, 255), (255, 200, 50)],
            'accents': [(200, 0, 255), (0, 255, 255)],
        },
        'frontend': {
            'base': [(0, 255, 200), (255, 0, 150), (100, 255, 0), (200, 100, 255)],
            'accents': [(255, 150, 0), (0, 200, 255)],
        },
        'documentation': {
            'base': [(200, 50, 255), (0, 255, 100), (255, 100, 200), (100, 255, 200)],
            'accents': [(255, 200, 0), (0, 100, 255)],
        }
    }

    @staticmethod
    def select_palette_by_repo(fingerprint):
        """Select vibrant psychedelic palette based on repository."""
        file_types = fingerprint['file_types']
        total_lines = fingerprint['total_lines']

        py_lines = file_types.get('.py', 0)
        js_lines = sum(file_types.get(ext, 0) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'])
        php_lines = file_types.get('.php', 0)
        java_lines = file_types.get('.java', 0)
        rb_lines = file_types.get('.rb', 0)
        go_lines = file_types.get('.go', 0)
        rs_lines = file_types.get('.rs', 0)
        cpp_lines = sum(file_types.get(ext, 0) for ext in ['.c', '.cpp', '.h', '.hpp', '.cc'])
        mobile_lines = sum(file_types.get(ext, 0) for ext in ['.swift', '.kt', '.m', '.mm', '.dart'])
        html_css_lines = sum(file_types.get(ext, 0) for ext in ['.html', '.htm', '.css', '.scss', '.sass', '.less'])
        md_lines = file_types.get('.md', 0)
        data_lines = sum(file_types.get(ext, 0) for ext in ['.csv', '.json', '.xml', '.yaml', '.yml'])

        threshold = total_lines * 0.3

        if php_lines > threshold:
            palette_name = 'php'
        elif java_lines > threshold:
            palette_name = 'java'
        elif rb_lines > threshold:
            palette_name = 'ruby'
        elif go_lines > threshold or rs_lines > threshold:
            palette_name = 'systems'
        elif cpp_lines > threshold:
            palette_name = 'cpp'
        elif mobile_lines > threshold:
            palette_name = 'mobile'
        elif html_css_lines > threshold:
            palette_name = 'frontend'
        elif js_lines > threshold:
            palette_name = 'javascript'
        elif py_lines > threshold:
            if data_lines > total_lines * 0.2:
                palette_name = 'data'
            else:
                palette_name = 'python'
        elif md_lines > total_lines * 0.5:
            palette_name = 'documentation'
        else:
            if file_types:
                sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                dominant_ext = sorted_types[0][0]
                ext_map = {
                    '.py': 'python', '.js': 'javascript', '.jsx': 'javascript', '.php': 'php',
                    '.java': 'java', '.rb': 'ruby', '.go': 'systems',
                    '.rs': 'systems', '.c': 'cpp', '.cpp': 'cpp',
                    '.swift': 'mobile', '.kt': 'mobile', '.dart': 'mobile',
                    '.html': 'frontend', '.css': 'frontend', '.scss': 'frontend',
                    '.md': 'documentation'
                }
                palette_name = ext_map.get(dominant_ext, 'documentation')
            else:
                palette_name = 'documentation'

        return palette_name, PsychedelicPalette.VIBRANT_PALETTES[palette_name]

    @staticmethod
    def get_vivid_hue_variations(base_color, seed_hash, count=5):
        """Generate vivid hue variations from a base color."""
        r, g, b = base_color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        variations = [base_color]
        random.seed(int(seed_hash, 16) % (2**32))

        for i in range(count - 1):
            hue_shift = random.uniform(-0.3, 0.3)
            new_h = (h + hue_shift) % 1.0
            new_s = min(1.0, s * random.uniform(0.9, 1.0))
            new_v = min(1.0, v * random.uniform(0.95, 1.0))

            r_new, g_new, b_new = colorsys.hsv_to_rgb(new_h, new_s, new_v)
            variations.append((int(r_new * 255), int(g_new * 255), int(b_new * 255)))

        return variations


class FluidShapes:
    """Generate flowing, organic, curved shapes - NO straight lines."""

    @staticmethod
    def wavy_line(start, end, wave_amplitude=20, wave_frequency=5, segments=100):
        """Generate a flowing wavy line from start to end (never straight)."""
        x1, y1 = start
        x2, y2 = end
        points = []

        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx**2 + dy**2)

        if dist == 0:
            return [start, end]

        # Perpendicular vector for wave offset
        perp_x = -dy / dist
        perp_y = dx / dist

        for i in range(segments + 1):
            t = i / segments

            # Base position along the line
            x = x1 + dx * t
            y = y1 + dy * t

            # Add wave motion (always curves, never straight)
            wave = math.sin(t * wave_frequency * math.pi) * wave_amplitude
            x += perp_x * wave
            y += perp_y * wave

            points.append((x, y))

        return points

    @staticmethod
    def spiral_vortex(center, start_radius, end_radius, turns, segments=300):
        """Generate a hypnotic spiral vortex."""
        cx, cy = center
        points = []

        for i in range(segments + 1):
            t = i / segments
            angle = t * turns * 2 * math.pi
            radius = start_radius + (end_radius - start_radius) * t

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))

        return points

    @staticmethod
    def concentric_waves(center, start_radius, end_radius, wave_count, segments=200):
        """Generate concentric circular waves."""
        cx, cy = center
        circles = []

        for wave_idx in range(wave_count):
            radius = start_radius + (end_radius - start_radius) * (wave_idx / max(1, wave_count - 1))
            points = []

            for i in range(segments + 1):
                angle = (i / segments) * 2 * math.pi

                # Add sine wave distortion for wavy circles
                distortion = 0.05 * radius * math.sin(angle * 3)
                actual_radius = radius + distortion

                x = cx + actual_radius * math.cos(angle)
                y = cy + actual_radius * math.sin(angle)
                points.append((x, y))

            circles.append(points)

        return circles

    @staticmethod
    def flowing_blob(center, radius, lobe_count, segments=150):
        """Generate organic flowing blob with wavy edges."""
        cx, cy = center
        points = []

        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi

            # Multiple sine waves create lobes
            lobe_variation = 1 + 0.4 * sum(math.sin(angle * (j+1)) for j in range(lobe_count)) / lobe_count
            actual_radius = radius * lobe_variation

            x = cx + actual_radius * math.cos(angle)
            y = cy + actual_radius * math.sin(angle)
            points.append((x, y))

        return points

    @staticmethod
    def mandala_pattern(center, max_radius, ring_count, segments=100):
        """Generate hypnotic mandala patterns with radiating curves."""
        cx, cy = center
        lines = []

        for ring_idx in range(ring_count):
            ring_radius = (ring_idx + 1) * max_radius / ring_count

            # Create multiple radiating "petals"
            petal_count = 6 + ring_idx % 4

            for petal in range(petal_count):
                petal_angle = (petal / petal_count) * 2 * math.pi

                # Draw a curve from center outward in this petal direction
                points = []
                for i in range(segments + 1):
                    t = i / segments
                    dist = t * ring_radius

                    # Add sinusoidal waviness
                    wave = math.sin(t * 3 * math.pi) * ring_radius * 0.15

                    angle = petal_angle + wave / ring_radius
                    x = cx + dist * math.cos(angle)
                    y = cy + dist * math.sin(angle)
                    points.append((x, y))

                lines.append(points)

        return lines

    @staticmethod
    def psychedelic_waves(y_base, width, amplitude, frequency, phase, segments=300):
        """Generate undulating waves with multiple sine curves layered."""
        points = []

        for i in range(segments + 1):
            x = (i / segments) * width

            # Layer multiple sine waves for complex motion
            y = y_base
            y += amplitude * math.sin(frequency * x / 50 + phase)
            y += amplitude * 0.5 * math.sin(frequency * x / 30 + phase * 1.5)
            y += amplitude * 0.3 * math.sin(frequency * x / 20 + phase * 2)

            points.append((x, y))

        return points


class PsychedelicStyleGenerator(BaseArtGenerator):
    """Psychedelic Git2Art style - Trippy flows with NO straight lines."""

    STYLE_NAME = "psychedelic"
    STYLE_DESCRIPTION = "Vibrant psychedelic style with flowing curves, spirals, and no straight lines"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize psychedelic style generator."""
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

    def _calculate_repo_scale(self, fingerprint):
        """Calculate scale factor based on repository size."""
        file_count = len(fingerprint['files'])
        total_lines = fingerprint['total_lines']

        if file_count <= 5:
            file_scale = 0.1 + (file_count / 5) * 0.2
        elif file_count <= 20:
            file_scale = 0.3 + ((file_count - 5) / 15) * 0.3
        elif file_count <= 50:
            file_scale = 0.6 + ((file_count - 20) / 30) * 0.2
        else:
            file_scale = min(1.0, 0.8 + ((file_count - 50) / 50) * 0.2)

        if total_lines <= 200:
            line_scale = 0.1 + (total_lines / 200) * 0.3
        elif total_lines <= 2000:
            line_scale = 0.4 + ((total_lines - 200) / 1800) * 0.3
        elif total_lines <= 10000:
            line_scale = 0.7 + ((total_lines - 2000) / 8000) * 0.2
        else:
            line_scale = min(1.0, 0.9 + ((total_lines - 10000) / 10000) * 0.1)

        scale = file_scale * 0.7 + line_scale * 0.3
        return max(0.1, min(1.0, scale))

    def generate_art(self, output_path='repo_art.png'):
        """Generate hypnotic psychedelic art."""
        fingerprint = self.get_repo_fingerprint()
        scale_factor = self._calculate_repo_scale(fingerprint)

        palette_name, palette_dict = PsychedelicPalette.select_palette_by_repo(fingerprint)

        img = self._create_psychedelic_background(fingerprint, palette_dict)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Build up layers of flowing curves and spirals
        self._add_flowing_background_waves(draw, fingerprint, palette_dict, scale_factor)
        self._add_spiral_vortices(draw, fingerprint, palette_dict, scale_factor)
        self._add_concentric_mandala_layers(draw, fingerprint, palette_dict, scale_factor)
        self._add_flowing_blobs(draw, fingerprint, palette_dict, scale_factor)
        self._add_hypnotic_waves(draw, fingerprint, palette_dict, scale_factor)
        self._add_radiating_mandalas(draw, fingerprint, palette_dict, scale_factor)

        # Apply psychedelic effects
        img = self._apply_psychedelic_filter(img, fingerprint)
        img.save(output_path, quality=95)

        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines, "
              f"{fingerprint['commit_count']} commits")
        print(f"Palette: '{palette_name}' (vibrant psychedelic)")
        print(f"Complexity scale: {scale_factor:.1%}")

        return output_path

    def _create_psychedelic_background(self, fingerprint, palette_dict):
        """Create dark, vibrant psychedelic background."""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        # Start with dark purple/black base for contrast
        base_color = (20, 10, 40)

        seed = fingerprint['total_lines']
        random.seed(seed)

        num_centers = 4 + (fingerprint['commit_count'] % 4)
        centers = []

        for i in range(num_centers):
            cx = random.randint(int(self.width * 0.1), int(self.width * 0.9))
            cy = random.randint(int(self.height * 0.1), int(self.height * 0.9))
            color_idx = i % len(palette_dict['base'])
            color = palette_dict['base'][color_idx]
            centers.append((cx, cy, color))

        for y in range(self.height):
            for x in range(self.width):
                influences = []
                colors_at_point = []

                for cx, cy, color in centers:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    max_dist = math.sqrt(self.width**2 + self.height**2)
                    influence = max(0, 1 - (dist / max_dist) ** 1.2)
                    influences.append(influence)
                    colors_at_point.append(color)

                total_influence = sum(influences) + 0.2

                r, g, b = base_color

                for i, influence in enumerate(influences):
                    weight = influence / total_influence
                    cr, cg, cb = colors_at_point[i]
                    # Reduce intensity for darker base
                    r += cr * weight * 0.3
                    g += cg * weight * 0.3
                    b += cb * weight * 0.3

                pixels[x, y] = (int(r), int(g), int(b))

        return img

    def _add_flowing_background_waves(self, draw, fingerprint, palette_dict, scale_factor):
        """Add flowing wavy background lines."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_waves = max(3, int((8 + (fingerprint['commit_count'] % 10)) * scale_factor))

        colors = palette_dict['base'] + palette_dict['accents']

        for i in range(num_waves):
            x1 = random.randint(-self.width // 2, self.width + self.width // 2)
            y1 = random.randint(-self.height // 2, self.height + self.height // 2)
            x2 = random.randint(-self.width // 2, self.width + self.width // 2)
            y2 = random.randint(-self.height // 2, self.height + self.height // 2)

            amplitude = random.randint(int(self.height * 0.05), int(self.height * 0.2))
            frequency = random.randint(2, 6)

            points = FluidShapes.wavy_line((x1, y1), (x2, y2),
                                           wave_amplitude=amplitude,
                                           wave_frequency=frequency)
            color = colors[i % len(colors)]
            stroke_width = random.randint(int(self.width * 0.02), int(self.width * 0.08))

            for j in range(len(points) - 1):
                opacity = random.randint(80, 160)
                draw.line([points[j], points[j+1]],
                         fill=color + (opacity,), width=stroke_width)

    def _add_spiral_vortices(self, draw, fingerprint, palette_dict, scale_factor):
        """Add hypnotic spiral vortices."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_spirals = max(2, int((4 + (fingerprint['commit_count'] % 6)) * scale_factor))

        colors = palette_dict['base'] + palette_dict['accents']

        for i in range(num_spirals):
            cx = random.randint(int(self.width * 0.2), int(self.width * 0.8))
            cy = random.randint(int(self.height * 0.2), int(self.height * 0.8))
            start_radius = random.randint(20, 100)
            end_radius = random.randint(int(self.width * 0.1), int(self.width * 0.3))
            turns = random.randint(3, 8)

            points = FluidShapes.spiral_vortex((cx, cy), start_radius, end_radius, turns)
            color = colors[i % len(colors)]
            stroke_width = random.randint(2, 8)

            for j in range(len(points) - 1):
                # Opacity increases toward the center of spiral
                progress = j / len(points)
                opacity = int(60 + progress * 120)
                draw.line([points[j], points[j+1]],
                         fill=color + (opacity,), width=stroke_width)

    def _add_concentric_mandala_layers(self, draw, fingerprint, palette_dict, scale_factor):
        """Add concentric mandala layers."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_mandalas = max(1, int((3 + (len(fingerprint['files']) % 4)) * scale_factor))

        colors = palette_dict['base'] + palette_dict['accents']

        for m_idx in range(num_mandalas):
            cx = random.randint(int(self.width * 0.2), int(self.width * 0.8))
            cy = random.randint(int(self.height * 0.2), int(self.height * 0.8))
            start_radius = random.randint(50, 150)
            end_radius = random.randint(int(self.width * 0.1), int(self.width * 0.25))
            wave_count = random.randint(5, 15)

            circles = FluidShapes.concentric_waves((cx, cy), start_radius, end_radius, wave_count)

            for wave_idx, circle_points in enumerate(circles):
                color = colors[(m_idx * 7 + wave_idx) % len(colors)]
                opacity = int(100 - (wave_idx / len(circles)) * 50)
                stroke_width = random.randint(2, 6)

                for j in range(len(circle_points) - 1):
                    draw.line([circle_points[j], circle_points[j+1]],
                             fill=color + (opacity,), width=stroke_width)

    def _add_flowing_blobs(self, draw, fingerprint, palette_dict, scale_factor):
        """Add organic flowing blobs."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_blobs = max(2, int((5 + (fingerprint['commit_count'] % 6)) * scale_factor))

        colors = palette_dict['base'] + palette_dict['accents']

        for i in range(num_blobs):
            cx = random.randint(int(self.width * 0.15), int(self.width * 0.85))
            cy = random.randint(int(self.height * 0.15), int(self.height * 0.85))
            radius = random.randint(int(self.width * 0.05), int(self.width * 0.15))
            lobe_count = random.randint(3, 8)

            blob_points = FluidShapes.flowing_blob((cx, cy), radius, lobe_count)
            color = colors[i % len(colors)]
            opacity = random.randint(60, 140)

            draw.polygon(blob_points, fill=color + (opacity,))

    def _add_hypnotic_waves(self, draw, fingerprint, palette_dict, scale_factor):
        """Add hypnotic undulating wave patterns."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_waves = max(3, int((6 + (fingerprint['commit_count'] % 8)) * scale_factor))

        colors = palette_dict['base'] + palette_dict['accents']

        for i in range(num_waves):
            y_base = random.randint(0, self.height)
            amplitude = random.randint(int(self.height * 0.05), int(self.height * 0.15))
            frequency = random.randint(2, 5)
            phase = random.uniform(0, 2 * math.pi)

            points = FluidShapes.psychedelic_waves(y_base, self.width, amplitude, frequency, phase)
            color = colors[i % len(colors)]
            stroke_width = random.randint(3, 8)
            opacity = random.randint(80, 150)

            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]],
                         fill=color + (opacity,), width=stroke_width)

    def _add_radiating_mandalas(self, draw, fingerprint, palette_dict, scale_factor):
        """Add radiating mandala patterns."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_mandalas = max(1, int((2 + (len(fingerprint['files']) % 3)) * scale_factor))

        colors = palette_dict['base'] + palette_dict['accents']

        for m_idx in range(num_mandalas):
            cx = random.randint(int(self.width * 0.25), int(self.width * 0.75))
            cy = random.randint(int(self.height * 0.25), int(self.height * 0.75))
            max_radius = random.randint(int(self.width * 0.1), int(self.width * 0.2))
            ring_count = random.randint(5, 12)

            mandala_lines = FluidShapes.mandala_pattern((cx, cy), max_radius, ring_count)

            for line_idx, line_points in enumerate(mandala_lines):
                color = colors[(m_idx * 11 + line_idx) % len(colors)]
                opacity = int(100 - (line_idx / max(1, len(mandala_lines))) * 40)
                stroke_width = random.randint(2, 5)

                for j in range(len(line_points) - 1):
                    draw.line([line_points[j], line_points[j+1]],
                             fill=color + (opacity,), width=stroke_width)

    def _apply_psychedelic_filter(self, img, fingerprint):
        """Apply psychedelic visual effects."""
        # Light blur for dreamy effect
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        return img
