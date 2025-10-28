"""Default art style - Bold expressionist with organic shapes.

This is the original Git2Art style featuring:
- Repository-driven color palettes
- Bold, thick strokes and filled areas
- Organic shapes and flowing lines
- IDEO-inspired techniques (Cornu curves, rich texture)
- Layered composition with varied shapes
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


class RepositoryPalette:
    """Generate harmonious color palettes based on repository characteristics."""

    PALETTES = {
        'python': {
            'base': [(52, 152, 219), (41, 128, 185), (26, 188, 156)],
            'accents': [(236, 240, 241), (44, 62, 80)],
            'bg_light': (245, 248, 250),
            'bg_dark': (52, 73, 94)
        },
        'javascript': {
            'base': [(241, 196, 15), (230, 126, 34), (211, 84, 0)],
            'accents': [(254, 250, 224), (123, 63, 0)],
            'bg_light': (255, 252, 244),
            'bg_dark': (100, 56, 14)
        },
        'php': {
            'base': [(142, 68, 173), (155, 89, 182), (187, 143, 206)],
            'accents': [(244, 236, 247), (74, 35, 90)],
            'bg_light': (250, 244, 252),
            'bg_dark': (63, 31, 77)
        },
        'java': {
            'base': [(231, 76, 60), (192, 57, 43), (165, 105, 79)],
            'accents': [(255, 235, 230), (120, 40, 31)],
            'bg_light': (255, 245, 243),
            'bg_dark': (100, 30, 22)
        },
        'ruby': {
            'base': [(220, 20, 60), (178, 34, 34), (255, 99, 71)],
            'accents': [(255, 240, 245), (139, 0, 0)],
            'bg_light': (255, 250, 250),
            'bg_dark': (100, 0, 0)
        },
        'systems': {
            'base': [(0, 173, 181), (52, 152, 219), (149, 165, 166)],
            'accents': [(236, 240, 241), (44, 62, 80)],
            'bg_light': (245, 248, 250),
            'bg_dark': (44, 62, 80)
        },
        'data': {
            'base': [(46, 204, 113), (39, 174, 96), (22, 160, 133)],
            'accents': [(232, 248, 245), (27, 79, 69)],
            'bg_light': (240, 252, 245),
            'bg_dark': (35, 67, 56)
        },
        'cpp': {
            'base': [(69, 85, 96), (52, 73, 94), (93, 109, 126)],
            'accents': [(236, 240, 241), (33, 42, 48)],
            'bg_light': (245, 248, 250),
            'bg_dark': (33, 42, 48)
        },
        'mobile': {
            'base': [(255, 107, 107), (255, 159, 64), (255, 118, 117)],
            'accents': [(255, 244, 230), (92, 47, 43)],
            'bg_light': (255, 250, 245),
            'bg_dark': (92, 53, 48)
        },
        'frontend': {
            'base': [(46, 204, 113), (52, 152, 219), (155, 89, 182)],
            'accents': [(236, 240, 241), (44, 62, 80)],
            'bg_light': (245, 252, 247),
            'bg_dark': (44, 62, 80)
        },
        'documentation': {
            'base': [(120, 135, 145), (178, 190, 195), (149, 165, 166)],
            'accents': [(245, 247, 248), (69, 85, 96)],
            'bg_light': (250, 251, 252),
            'bg_dark': (69, 85, 96)
        }
    }

    @staticmethod
    def select_palette_by_repo(fingerprint):
        """Select color palette based on repository language and type."""
        file_types = fingerprint['file_types']
        total_lines = fingerprint['total_lines']
        num_files = len(fingerprint['files'])

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
        elif md_lines > total_lines * 0.5 and num_files <= 10:
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

        return palette_name, RepositoryPalette.PALETTES[palette_name]

    @staticmethod
    def expand_palette_with_theory(palette_dict, seed, contrast='high'):
        """Expand palette using advanced color wheel theory."""
        expanded = []
        base_colors = palette_dict['base']
        accent_colors = palette_dict['accents']

        contrast_settings = {
            'low': {'tint': 1.15, 'shade': 0.7, 'sat_tint': 0.6, 'sat_shade': 1.1},
            'medium': {'tint': 1.25, 'shade': 0.55, 'sat_tint': 0.5, 'sat_shade': 1.2},
            'high': {'tint': 1.4, 'shade': 0.4, 'sat_tint': 0.3, 'sat_shade': 1.3}
        }

        settings = contrast_settings.get(contrast, contrast_settings['high'])
        random.seed(seed)
        expanded.extend(base_colors)

        for i, color in enumerate(base_colors):
            r, g, b = color
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

            very_light = RepositoryPalette._hsv_to_rgb(h, s * settings['sat_tint'], min(1.0, v * settings['tint']))
            very_dark = RepositoryPalette._hsv_to_rgb(h, min(1.0, s * settings['sat_shade']), v * settings['shade'])
            expanded.extend([very_light, very_dark])

            if i % 3 == 0:
                expanded.append(RepositoryPalette.get_complementary_color(color))
            elif i % 3 == 1:
                expanded.extend(RepositoryPalette.get_triadic_colors(color))
            else:
                expanded.extend(RepositoryPalette.get_split_complementary_colors(color))

        if len(base_colors) > 0:
            primary = base_colors[0]
            tetradic = RepositoryPalette.get_tetradic_colors(primary)
            expanded.extend(tetradic)

        expanded.extend(accent_colors)
        return expanded

    @staticmethod
    def get_complementary_color(color):
        """Get complementary color."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        comp_h = (h + 0.5) % 1.0
        return RepositoryPalette._hsv_to_rgb(comp_h, s, v)

    @staticmethod
    def get_triadic_colors(color):
        """Get triadic colors."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        triadic1_h = (h + 0.333) % 1.0
        triadic2_h = (h + 0.667) % 1.0
        return [
            RepositoryPalette._hsv_to_rgb(triadic1_h, s, v),
            RepositoryPalette._hsv_to_rgb(triadic2_h, s, v)
        ]

    @staticmethod
    def get_split_complementary_colors(color):
        """Get split-complementary colors."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        comp_h = (h + 0.5) % 1.0
        split1_h = (comp_h - 0.083) % 1.0
        split2_h = (comp_h + 0.083) % 1.0
        return [
            RepositoryPalette._hsv_to_rgb(split1_h, s, v),
            RepositoryPalette._hsv_to_rgb(split2_h, s, v)
        ]

    @staticmethod
    def get_tetradic_colors(color):
        """Get tetradic colors."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        tet1_h = (h + 0.167) % 1.0
        tet2_h = (h + 0.5) % 1.0
        tet3_h = (h + 0.667) % 1.0
        return [
            RepositoryPalette._hsv_to_rgb(tet1_h, s, v),
            RepositoryPalette._hsv_to_rgb(tet2_h, s, v),
            RepositoryPalette._hsv_to_rgb(tet3_h, s, v)
        ]

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        """Convert HSV to RGB (0-255)."""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))


class ColorMixer:
    """Deterministic color mixing utilities."""

    @staticmethod
    def blend_colors(colors, seed_hash, count=2):
        """Blend multiple colors with deterministic ratios."""
        count = max(2, min(4, count))
        selected_colors = []
        for i in range(count):
            idx = DeterministicRandom.randint(seed_hash, 2000 + i, 0, len(colors) - 1)
            selected_colors.append(colors[idx])

        ratios = []
        for i in range(count):
            ratio = DeterministicRandom.uniform(seed_hash, 2100 + i, 0.1, 1.0)
            ratios.append(ratio)

        total = sum(ratios)
        ratios = [r / total for r in ratios]

        r, g, b = 0, 0, 0
        for color, ratio in zip(selected_colors, ratios):
            r += color[0] * ratio
            g += color[1] * ratio
            b += color[2] * ratio

        return (int(r), int(g), int(b))

    @staticmethod
    def get_analogous_variation(color, seed_hash, shift_range=0.05):
        """Get analogous color variation."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        shift = DeterministicRandom.uniform(seed_hash, 2200, -shift_range, shift_range)
        new_h = (h + shift) % 1.0

        s_var = DeterministicRandom.uniform(seed_hash, 2201, 0.9, 1.1)
        v_var = DeterministicRandom.uniform(seed_hash, 2202, 0.9, 1.1)

        new_s = max(0, min(1.0, s * s_var))
        new_v = max(0, min(1.0, v * v_var))

        r_new, g_new, b_new = colorsys.hsv_to_rgb(new_h, new_s, new_v)
        return (int(r_new * 255), int(g_new * 255), int(b_new * 255))


class OrganicShapes:
    """Generate flowing, organic shapes with advanced effects."""

    @staticmethod
    def flowing_line(start, end, curviness=0.3, segments=50):
        """Generate flowing bezier curve."""
        x1, y1 = start
        x2, y2 = end
        points = []

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        dx = x2 - x1
        dy = y2 - y1
        perp_x = -dy
        perp_y = dx
        length = math.sqrt(perp_x**2 + perp_y**2)

        if length > 0:
            perp_x /= length
            perp_y /= length

        dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        offset = dist * curviness
        ctrl1_x = mid_x + perp_x * offset
        ctrl1_y = mid_y + perp_y * offset

        for i in range(segments + 1):
            t = i / segments
            x = (1-t)**3 * x1 + 3*(1-t)**2*t * ctrl1_x + 3*(1-t)*t**2 * mid_x + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2*t * ctrl1_y + 3*(1-t)*t**2 * mid_y + t**3 * y2
            points.append((x, y))

        return points

    @staticmethod
    def spiral_pattern(center, start_radius, end_radius, turns, segments=200):
        """Generate spiral pattern."""
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
    def circle_loop(center, radius, segments=100):
        """Generate circular loop."""
        cx, cy = center
        points = []

        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))

        return points

    @staticmethod
    def rotating_pattern(center, radius, count, rotation_offset, size_range):
        """Generate rotating elements around a center."""
        cx, cy = center
        elements = []

        for i in range(count):
            angle = (i / count) * 2 * math.pi + rotation_offset
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            size = random.uniform(size_range[0], size_range[1])
            elements.append((x, y, size, angle))

        return elements

    @staticmethod
    def particle_burst(center, count, min_radius, max_radius, seed):
        """Generate particle burst."""
        cx, cy = center
        particles = []
        random.seed(seed)

        for i in range(count):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(min_radius, max_radius)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            size = random.uniform(2, 10)
            particles.append((x, y, size))

        return particles

    @staticmethod
    def wave_pattern(y_base, width, amplitude, frequency, phase, segments=200):
        """Generate wave pattern."""
        points = []
        for i in range(segments + 1):
            x = (i / segments) * width
            y = y_base + amplitude * math.sin(frequency * x / 100 + phase)
            points.append((x, y))
        return points

    @staticmethod
    def cornu_inspired_curve(start, end, curvature_factor, segments=150):
        """Generate Cornu-inspired (Euler spiral) curve."""
        x1, y1 = start
        x2, y2 = end
        points = []

        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)

        for i in range(segments + 1):
            t = i / segments
            theta = curvature_factor * t * t
            s = t * length
            x = x1 + dx * t + dy * math.sin(theta) * 0.3
            y = y1 + dy * t - dx * math.sin(theta) * 0.3
            points.append((x, y))

        return points

    @staticmethod
    def generate_texture_lines(center, radius, count, seed):
        """Generate many small texture lines for rich detail."""
        cx, cy = center
        lines = []
        random.seed(seed)

        for i in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius)
            x = cx + dist * math.cos(angle)
            y = cy + dist * math.sin(angle)

            line_angle = random.uniform(0, 2 * math.pi)
            line_length = random.uniform(2, 15)
            x2 = x + line_length * math.cos(line_angle)
            y2 = y + line_length * math.sin(line_angle)

            opacity = random.randint(10, 80)
            thickness = random.uniform(0.5, 2)

            lines.append(((x, y), (x2, y2), opacity, thickness))

        return lines


class DefaultStyleGenerator(BaseArtGenerator):
    """Default Git2Art style - Bold expressionist with organic shapes."""

    STYLE_NAME = "default"
    STYLE_DESCRIPTION = "Bold expressionist style with organic shapes, thick strokes, and vibrant colors"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', contrast='high', **kwargs):
        """Initialize default style generator.

        Args:
            contrast: Color contrast level ('low', 'medium', 'high')
        """
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)
        self.contrast = contrast

    def _calculate_repo_scale(self, fingerprint):
        """Calculate a scale factor (0-1) based on repository size."""
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
        """Generate harmonious generative art with smooth, soft finish."""
        fingerprint = self.get_repo_fingerprint()
        scale_factor = self._calculate_repo_scale(fingerprint)

        palette_name, palette_dict = RepositoryPalette.select_palette_by_repo(fingerprint)
        all_colors = RepositoryPalette.expand_palette_with_theory(palette_dict, fingerprint['total_lines'], self.contrast)

        img = self._create_background(fingerprint, palette_dict)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Add layers of elements (scaled with repo size)
        if scale_factor > 0.2:
            self._add_filled_color_areas(draw, fingerprint, all_colors, scale_factor)
        if scale_factor > 0.3:
            self._add_background_flows(draw, fingerprint, all_colors, scale_factor)

        self._draw_some_main_elements(draw, fingerprint, all_colors, start_idx=0, count=3)

        if scale_factor > 0.25:
            self._add_cornu_curves(draw, fingerprint, all_colors, scale_factor)
        if scale_factor > 0.3:
            self._add_bold_color_blocks(draw, fingerprint, all_colors, scale_factor)

        self._draw_some_main_elements(draw, fingerprint, all_colors, start_idx=3, count=5)

        if scale_factor > 0.4:
            self._add_spirals(draw, fingerprint, all_colors, scale_factor)
            self._add_circular_loops(draw, fingerprint, all_colors, scale_factor)

        self._draw_some_main_elements(draw, fingerprint, all_colors, start_idx=8, count=None)

        if scale_factor > 0.3:
            self._add_rich_texture(draw, fingerprint, all_colors, scale_factor)
        if scale_factor > 0.35:
            self._add_rotating_elements(draw, fingerprint, all_colors, scale_factor)
        if scale_factor > 0.2:
            self._add_connections(draw, fingerprint, all_colors, scale_factor)
        if scale_factor > 0.25:
            self._add_particles(draw, fingerprint, all_colors, scale_factor)
        if scale_factor > 0.3:
            self._add_waves_with_fade(draw, fingerprint, all_colors, scale_factor)

        img = self._apply_soft_finish(img, fingerprint)
        img.save(output_path, quality=95)

        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines, "
              f"{fingerprint['commit_count']} commits")
        print(f"Palette: '{palette_name}' ({len(all_colors)} harmonious colors)")
        print(f"Complexity scale: {scale_factor:.1%}")

        return output_path

    def _apply_soft_finish(self, img, fingerprint):
        """Apply very light smoothing for subtle polish."""
        blur_radius = 0.3
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return img

    def _create_background(self, fingerprint, palette_dict):
        """Create dynamic background with color variations."""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        base_colors = palette_dict['base']
        bg_light = palette_dict['bg_light']
        bg_dark = palette_dict['bg_dark']

        seed = fingerprint['total_lines']
        random.seed(seed)

        num_centers = 3 + (fingerprint['commit_count'] % 3)
        centers = []

        for i in range(num_centers):
            cx = random.randint(int(self.width * 0.2), int(self.width * 0.8))
            cy = random.randint(int(self.height * 0.2), int(self.height * 0.8))
            color_idx = i % len(base_colors)
            r, g, b = base_colors[color_idx]
            light_color = (
                min(255, int(r + (255 - r) * 0.6)),
                min(255, int(g + (255 - g) * 0.6)),
                min(255, int(b + (255 - b) * 0.6))
            )
            centers.append((cx, cy, light_color))

        for y in range(self.height):
            for x in range(self.width):
                influences = []
                colors_at_point = []

                for cx, cy, color in centers:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    max_dist = math.sqrt(self.width**2 + self.height**2)
                    influence = max(0, 1 - (dist / max_dist) ** 0.8)
                    influences.append(influence)
                    colors_at_point.append(color)

                corner_ratio = (x + y) / (self.width + self.height)
                corner_influence = 0.3

                total_influence = sum(influences) + corner_influence
                r, g, b = 0, 0, 0

                for i, influence in enumerate(influences):
                    weight = influence / total_influence
                    cr, cg, cb = colors_at_point[i]
                    r += cr * weight
                    g += cg * weight
                    b += cb * weight

                corner_weight = corner_influence / total_influence
                r += bg_light[0] * (1 - corner_ratio) * corner_weight + bg_dark[0] * corner_ratio * corner_weight
                g += bg_light[1] * (1 - corner_ratio) * corner_weight + bg_dark[1] * corner_ratio * corner_weight
                b += bg_light[2] * (1 - corner_ratio) * corner_weight + bg_dark[2] * corner_ratio * corner_weight

                pixels[x, y] = (int(r), int(g), int(b))

        return img
    def _add_filled_color_areas(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add large filled color areas for bold visual impact."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_areas = max(1, int((3 + (fingerprint['commit_count'] % 5)) * scale_factor))

        for i in range(num_areas):
            area_hash = hashlib.md5(f"{seed}_{i}_area".encode()).hexdigest()
            cx = DeterministicRandom.randint(area_hash, 0, 0, self.width)
            cy = DeterministicRandom.randint(area_hash, 1, 0, self.height)
            size = DeterministicRandom.randint(area_hash, 2, int(self.width * 0.2), int(self.width * 0.5))

            segments = DeterministicRandom.randint(area_hash, 3, 6, 12)
            points = []
            for j in range(segments):
                angle = (j / segments) * 2 * math.pi
                variation = DeterministicRandom.uniform(area_hash, 100 + j, 0.7, 1.3)
                radius = size * variation
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                points.append((px, py))

            blend_count = DeterministicRandom.choice(area_hash, 4, [2, 2, 3, 3, 4])
            blended = ColorMixer.blend_colors(colors, area_hash, blend_count)
            opacity = DeterministicRandom.randint(area_hash, 5, 40, 100)
            draw.polygon(points, fill=blended + (opacity,))

    def _add_bold_color_blocks(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add bold rectangular color blocks."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_blocks = max(1, int((4 + (len(fingerprint['files']) % 6)) * scale_factor))

        for i in range(num_blocks):
            block_hash = hashlib.md5(f"{seed}_{i}_block".encode()).hexdigest()
            x = DeterministicRandom.randint(block_hash, 0, -self.width // 4, self.width)
            y = DeterministicRandom.randint(block_hash, 1, -self.height // 4, self.height)
            width = DeterministicRandom.randint(block_hash, 2, int(self.width * 0.15), int(self.width * 0.40))
            height = DeterministicRandom.randint(block_hash, 3, int(self.height * 0.10), int(self.height * 0.30))
            angle = DeterministicRandom.uniform(block_hash, 4, 0, math.pi)

            corners = [
                (x, y),
                (x + width * math.cos(angle), y + width * math.sin(angle)),
                (x + width * math.cos(angle) - height * math.sin(angle),
                 y + width * math.sin(angle) + height * math.cos(angle)),
                (x - height * math.sin(angle), y + height * math.cos(angle))
            ]

            blend_count = DeterministicRandom.choice(block_hash, 5, [3, 3, 3, 4])
            mixed = ColorMixer.blend_colors(colors, block_hash, blend_count)
            opacity = DeterministicRandom.randint(block_hash, 6, 50, 120)
            draw.polygon(corners, fill=mixed + (opacity,))

    def _add_background_flows(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add flowing background lines - BOLD and THICK."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_flows = max(1, int((8 + (fingerprint['commit_count'] % 10)) * scale_factor))

        for i in range(num_flows):
            x1 = random.randint(-self.width // 2, self.width + self.width // 2)
            y1 = random.randint(-self.height // 2, self.height + self.height // 2)
            x2 = random.randint(-self.width // 2, self.width + self.width // 2)
            y2 = random.randint(-self.height // 2, self.height + self.height // 2)

            points = OrganicShapes.flowing_line((x1, y1), (x2, y2), curviness=random.uniform(0.3, 0.6), segments=100)
            color = colors[i % len(colors)]

            if random.random() < 0.3:
                stroke_width = random.randint(int(self.width * 0.15), int(self.width * 0.30))
            else:
                stroke_width = random.randint(int(self.width * 0.05), int(self.width * 0.15))

            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]], fill=color + (random.randint(60, 120),), width=stroke_width)

    def _add_cornu_curves(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add Cornu/Euler spiral curves."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_curves = max(5, int((50 + (fingerprint['commit_count'] * 5)) * scale_factor))

        for i in range(num_curves):
            x1 = random.randint(-self.width // 4, self.width + self.width // 4)
            y1 = random.randint(-self.height // 4, self.height + self.height // 4)
            x2 = random.randint(-self.width // 4, self.width + self.width // 4)
            y2 = random.randint(-self.height // 4, self.height + self.height // 4)
            curvature = random.uniform(2, 8)

            points = OrganicShapes.cornu_inspired_curve((x1, y1), (x2, y2), curvature, segments=120)
            color = colors[i % len(colors)]

            if random.random() < 0.4:
                stroke_width = random.randint(int(self.width * 0.01), int(self.width * 0.08))
            elif random.random() < 0.7:
                stroke_width = random.randint(int(self.width * 0.08), int(self.width * 0.20))
            else:
                stroke_width = random.randint(int(self.width * 0.20), int(self.width * 0.30))

            opacity = random.randint(40, 150)

            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]], fill=color + (opacity,), width=int(stroke_width))

    def _add_rich_texture(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add thousands of micro-lines for rich texture."""
        seed = fingerprint['total_lines']
        files = list(fingerprint['files'].items())
        if not files:
            return

        max_files = max(1, int(3 * scale_factor))
        for idx, (file_path, file_data) in enumerate(files[:max_files]):
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius_pos = 60 + idx * (min(self.width, self.height) / (2.2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius_pos * math.cos(angle)
            y = cy + radius_pos * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)
            texture_radius = 80 + idx * 30
            num_lines = max(50, int((500 + (file_data['lines'] * 5)) * scale_factor))

            texture_lines = OrganicShapes.generate_texture_lines((x, y), texture_radius, num_lines, hash_val)
            color = colors[hash_val % len(colors)]

            for (x1, y1), (x2, y2), opacity, thickness in texture_lines:
                draw.line([(x1, y1), (x2, y2)], fill=color + (opacity,), width=int(thickness))

    def _draw_some_main_elements(self, draw, fingerprint, colors, start_idx=0, count=None):
        """Draw a subset of main elements for layered composition."""
        files = fingerprint['files']
        if not files:
            return

        sorted_files = sorted(files.items(), key=lambda x: x[1]['lines'], reverse=True)

        if count is None:
            elements_to_draw = sorted_files[start_idx:]
        else:
            elements_to_draw = sorted_files[start_idx:start_idx + count]

        for idx, (file_path, file_data) in enumerate(elements_to_draw):
            original_idx = start_idx + idx
            self._draw_single_element(draw, original_idx, file_data, colors, len(sorted_files))

    def _draw_single_element(self, draw, idx, file_data, colors, total_files):
        """Draw a single main element."""
        golden_angle = 137.508
        angle = (idx * golden_angle) * (math.pi / 180)
        file_hash = file_data['hash']

        if idx < 3:
            radius = DeterministicRandom.randint(file_hash, 0, 50, min(self.width, self.height) // 3)
        else:
            radius = DeterministicRandom.randint(file_hash, 0, 0, int(min(self.width, self.height) * 0.4))

        cx, cy = self.width / 2, self.height / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        normalized_size = min(1.0, file_data['lines'] / 500.0)
        min_size = int(min(self.width, self.height) * 0.03)
        max_size = int(min(self.width, self.height) * 0.70)
        size = min_size + normalized_size * (max_size - min_size)

        size_variation = DeterministicRandom.uniform(file_hash, 1, 0.6, 1.4)
        size = int(size * size_variation)

        hash_val = int(file_hash[:8], 16)
        color = colors[hash_val % len(colors)]
        shape_type = hash_val % 5
        self._draw_varied_shape(draw, x, y, size, color, file_hash, shape_type)

    def _draw_varied_shape(self, draw, x, y, size, color, seed_hash, shape_type):
        """Draw varied shapes."""
        if shape_type == 0:
            self._draw_blob(draw, x, y, size, color, seed_hash)
        elif shape_type == 1:
            self._draw_star_shape(draw, x, y, size, color, seed_hash)
        elif shape_type == 2:
            self._draw_polygon_shape(draw, x, y, size, color, seed_hash)
        elif shape_type == 3:
            self._draw_stretched_blob(draw, x, y, size, color, seed_hash)
        else:
            self._draw_splatter_shape(draw, x, y, size, color, seed_hash)

    def _draw_blob(self, draw, x, y, size, color, seed_hash):
        """Draw organic blob."""
        points = []
        segments = DeterministicRandom.randint(seed_hash, 0, 12, 24)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            rand_variation = DeterministicRandom.uniform(seed_hash, i * 2, -0.3, 0.4)
            sin_freq = DeterministicRandom.randint(seed_hash, i * 2 + 1, 2, 5)
            variation = 1 + rand_variation + 0.2 * math.sin(angle * sin_freq)
            radius = (size / 2) * variation
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_star_shape(self, draw, x, y, size, color, seed_hash):
        """Draw star/spiky shape."""
        points = []
        num_spikes = DeterministicRandom.randint(seed_hash, 100, 5, 12)

        for i in range(num_spikes * 2):
            angle = (i / (num_spikes * 2)) * 2 * math.pi
            if i % 2 == 0:
                radius = size / 2 * DeterministicRandom.uniform(seed_hash, 200 + i, 0.8, 1.2)
            else:
                radius = size / 2 * DeterministicRandom.uniform(seed_hash, 200 + i, 0.3, 0.6)

            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_polygon_shape(self, draw, x, y, size, color, seed_hash):
        """Draw smooth polygon shape."""
        points = []
        num_sides = DeterministicRandom.choice(seed_hash, 300, [5, 6, 7, 8, 10, 12])
        rotation = DeterministicRandom.uniform(seed_hash, 301, 0, math.pi)
        segments_per_side = 3

        for i in range(num_sides * segments_per_side):
            base_angle = (i / (num_sides * segments_per_side)) * 2 * math.pi + rotation
            side_idx = i // segments_per_side
            within_side = (i % segments_per_side) / segments_per_side

            radius_var1 = DeterministicRandom.uniform(seed_hash, 400 + side_idx, 0.9, 1.1)
            radius_var2 = DeterministicRandom.uniform(seed_hash, 400 + side_idx + 1, 0.9, 1.1)
            radius_var = radius_var1 + (radius_var2 - radius_var1) * within_side

            radius = size / 2 * radius_var
            px = x + radius * math.cos(base_angle)
            py = y + radius * math.sin(base_angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_stretched_blob(self, draw, x, y, size, color, seed_hash):
        """Draw stretched/elongated organic shape."""
        points = []
        segments = DeterministicRandom.randint(seed_hash, 500, 15, 25)
        stretch_angle = DeterministicRandom.uniform(seed_hash, 501, 0, math.pi)
        stretch_factor = DeterministicRandom.uniform(seed_hash, 502, 1.5, 3.0)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            variation = 1 + DeterministicRandom.uniform(seed_hash, 600 + i, -0.2, 0.3)

            radius_x = (size / 2) * variation
            radius_y = (size / 2) * variation / stretch_factor

            local_x = radius_x * math.cos(angle)
            local_y = radius_y * math.sin(angle)

            px = x + local_x * math.cos(stretch_angle) - local_y * math.sin(stretch_angle)
            py = y + local_x * math.sin(stretch_angle) + local_y * math.cos(stretch_angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_splatter_shape(self, draw, x, y, size, color, seed_hash):
        """Draw irregular splatter shape."""
        points = []
        segments = DeterministicRandom.randint(seed_hash, 700, 20, 40)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            variation = DeterministicRandom.uniform(seed_hash, 800 + i * 2, 0.4, 1.3)
            spike_check = DeterministicRandom.from_hash(seed_hash, 800 + i * 2 + 1)
            if spike_check < 0.2:
                spike_mult = DeterministicRandom.uniform(seed_hash, 800 + i * 2 + 2, 1.2, 1.8)
                variation *= spike_mult

            radius = (size / 2) * variation
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_layered_shape(self, draw, points, color, seed_hash):
        """Draw shape with multiple gradient layers."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)

        use_complementary = DeterministicRandom.from_hash(seed_hash, 900) > 0.7
        num_layers = DeterministicRandom.randint(seed_hash, 1000, 6, 10)

        for layer in range(num_layers, 0, -1):
            layer_ratio = layer / num_layers
            layer_points = []
            for px, py in points:
                lx = cx + (px - cx) * layer_ratio
                ly = cy + (py - cy) * layer_ratio
                layer_points.append((lx, ly))

            if use_complementary and layer < num_layers // 2:
                comp_h = (h + 0.5) % 1.0
                layer_h = comp_h
                layer_s = s * DeterministicRandom.uniform(seed_hash, 1100 + layer, 0.7, 1.1)
                v_var = DeterministicRandom.uniform(seed_hash, 1200 + layer, 0.1, 0.3)
                layer_v = min(1.0, v + (1 - layer_ratio) * v_var)
            else:
                hue_shift = DeterministicRandom.uniform(seed_hash, 1100 + layer, -0.08, 0.08)
                layer_h = (h + hue_shift) % 1.0
                v_var = DeterministicRandom.uniform(seed_hash, 1200 + layer, 0.1, 0.3)
                layer_v = min(1.0, v + (1 - layer_ratio) * v_var)
                layer_s = s * (0.6 + layer_ratio * 0.4)

            layer_color = self._hsv_to_rgb(layer_h, min(1.0, layer_s), layer_v)
            base_opacity = DeterministicRandom.randint(seed_hash, 1300 + layer, 120, 180)
            layer_opacity = int(base_opacity + layer_ratio * 60)

            if len(layer_points) > 2:
                draw.polygon(layer_points, fill=layer_color + (layer_opacity,))

        shadow_points = []
        for i, (px, py) in enumerate(points):
            expansion = DeterministicRandom.uniform(seed_hash, 1400 + i, 1.08, 1.2)
            sx = cx + (px - cx) * expansion
            sy = cy + (py - cy) * expansion
            shadow_points.append((sx, sy))

        shadow_color = ColorMixer.get_analogous_variation(color, seed_hash, shift_range=0.03)
        sr, sg, sb = shadow_color
        darker = (max(0, sr - DeterministicRandom.randint(seed_hash, 1500, 30, 60)),
                  max(0, sg - DeterministicRandom.randint(seed_hash, 1501, 30, 60)),
                  max(0, sb - DeterministicRandom.randint(seed_hash, 1502, 30, 60)))
        shadow_opacity = DeterministicRandom.randint(seed_hash, 1503, 40, 80)
        if len(shadow_points) > 2:
            draw.polygon(shadow_points, fill=darker + (shadow_opacity,))

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB tuple."""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def _add_connections(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add connection lines."""
        files = list(fingerprint['files'].items())
        if len(files) < 2:
            return

        seed = fingerprint['total_lines']
        random.seed(seed)
        connections = max(1, int(min(len(files) * 2, 30) * scale_factor))

        for i in range(connections):
            idx1 = i % len(files)
            idx2 = (i + random.randint(1, 3)) % len(files)

            golden_angle = 137.508
            angle1 = (idx1 * golden_angle) * (math.pi / 180)
            radius1 = 60 + idx1 * (min(self.width, self.height) / (2.2 * len(files)))
            cx, cy = self.width / 2, self.height / 2
            x1 = cx + radius1 * math.cos(angle1)
            y1 = cy + radius1 * math.sin(angle1)

            angle2 = (idx2 * golden_angle) * (math.pi / 180)
            radius2 = 60 + idx2 * (min(self.width, self.height) / (2.2 * len(files)))
            x2 = cx + radius2 * math.cos(angle2)
            y2 = cy + radius2 * math.sin(angle2)

            points = OrganicShapes.flowing_line((x1, y1), (x2, y2), curviness=random.uniform(0.3, 0.5), segments=80)
            color = colors[i % len(colors)]

            for j in range(len(points) - 1):
                thickness = 2 + int(4 * math.sin((j / len(points)) * math.pi))
                draw.line([points[j], points[j+1]], fill=color + (100,), width=thickness)

    def _add_particles(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add particle effects."""
        files = list(fingerprint['files'].items())
        if not files:
            return

        max_files = max(1, int(5 * scale_factor))
        for idx, (file_path, file_data) in enumerate(files[:max_files]):
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius = 60 + idx * (min(self.width, self.height) / (2.2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)
            particle_count = max(5, int((18 + (file_data['lines'] // 15)) * scale_factor))
            particles = OrganicShapes.particle_burst((x, y), particle_count, 30, 80, hash_val)
            color = colors[hash_val % len(colors)]

            for px, py, size in particles:
                larger_size = size * 1.5
                draw.ellipse([px - larger_size/2, py - larger_size/2, px + larger_size/2, py + larger_size/2],
                           fill=color + (170,))

    def _add_spirals(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add smooth spiral patterns."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_spirals = max(1, int((5 + (fingerprint['commit_count'] % 5)) * scale_factor))

        for i in range(num_spirals):
            cx = random.randint(int(self.width * 0.1), int(self.width * 0.9))
            cy = random.randint(int(self.height * 0.1), int(self.height * 0.9))
            start_radius = random.randint(5, 20)
            end_radius = random.randint(80, 250)
            turns = random.uniform(3, 6)

            points = OrganicShapes.spiral_pattern((cx, cy), start_radius, end_radius, turns, segments=300)
            color = colors[i % len(colors)]

            for j in range(len(points) - 1):
                fade_ratio = j / len(points)
                opacity = int(80 * (1 - fade_ratio))
                thickness = max(1, int(5 * (1 - fade_ratio * 0.5)))
                draw.line([points[j], points[j+1]], fill=color + (opacity,), width=thickness)

    def _add_circular_loops(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add concentric circular loops."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_loop_centers = max(1, int((2 + (len(fingerprint['files']) % 3)) * scale_factor))

        for i in range(num_loop_centers):
            cx = random.randint(int(self.width * 0.15), int(self.width * 0.85))
            cy = random.randint(int(self.height * 0.15), int(self.height * 0.85))
            num_loops = random.randint(3, 6)
            base_radius = random.randint(30, 60)

            for loop in range(num_loops):
                radius = base_radius + loop * random.randint(15, 30)
                points = OrganicShapes.circle_loop((cx, cy), radius, segments=80)
                color = colors[(i + loop) % len(colors)]
                opacity = max(20, int(70 - loop * 10))

                for j in range(len(points) - 1):
                    draw.line([points[j], points[j+1]], fill=color + (opacity,), width=2)

    def _add_rotating_elements(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add rotating circular elements."""
        files = list(fingerprint['files'].items())
        if not files:
            return

        seed = fingerprint['total_lines']
        random.seed(seed)
        max_files = max(1, int(3 * scale_factor))

        for idx, (file_path, file_data) in enumerate(files[:max_files]):
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius = 60 + idx * (min(self.width, self.height) / (2.2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)
            rotation_offset = (hash_val % 360) * (math.pi / 180)
            orbit_radius = 40 + idx * 15
            num_elements = 6 + (hash_val % 5)

            elements = OrganicShapes.rotating_pattern((x, y), orbit_radius, num_elements, rotation_offset, (4, 10))
            color = colors[hash_val % len(colors)]

            for ex, ey, esize, eangle in elements:
                draw.ellipse([ex - esize, ey - esize, ex + esize, ey + esize], fill=color + (120,))

    def _add_waves_with_fade(self, draw, fingerprint, colors, scale_factor=1.0):
        """Add wave patterns with directional color fading."""
        seed = fingerprint['total_lines']
        random.seed(seed)
        num_waves = max(1, int((6 + (fingerprint['commit_count'] % 6)) * scale_factor))

        for i in range(num_waves):
            y_base = random.randint(int(self.height * 0.15), int(self.height * 0.85))
            amplitude = random.randint(20, 40)
            frequency = random.uniform(2.0, 3.5)
            phase = random.uniform(0, 2 * math.pi)

            points = OrganicShapes.wave_pattern(y_base, self.width, amplitude, frequency, phase)
            base_color = colors[i % len(colors)]
            r, g, b = base_color
            h, s, v = colorsys.hsv_to_rgb(r/255, g/255, b/255)

            for j in range(len(points) - 1):
                fade_ratio = j / len(points)
                wave_h = (h + fade_ratio * 0.1) % 1.0
                wave_v = v * (1 - fade_ratio * 0.3)
                wave_s = s * (1 - fade_ratio * 0.2)
                wave_color = self._hsv_to_rgb(wave_h, wave_s, wave_v)
                opacity = int(80 * (1 - fade_ratio * 0.5))
                thickness = max(2, int(5 * (1 - fade_ratio * 0.4)))
                draw.line([points[j], points[j+1]], fill=wave_color + (opacity,), width=thickness)
