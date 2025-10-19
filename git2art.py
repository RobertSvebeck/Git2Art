#!/usr/bin/env python3
"""
Git2Art: Repository-Driven Generative Art
Creates harmonious, organic art with color palettes derived from repository characteristics
Inspired by "Painting with Code" - IDEO
"""

import git
import hashlib
from PIL import Image, ImageDraw, ImageFilter
import colorsys
from pathlib import Path
from collections import defaultdict
import math
import random


class DeterministicRandom:
    """Deterministic random number generator based on hash values"""

    @staticmethod
    def from_hash(hash_string, index=0):
        """Generate a deterministic random value from a hash string and index"""
        combined = f"{hash_string}_{index}"
        hash_bytes = hashlib.md5(combined.encode()).digest()
        # Convert first 8 bytes to integer
        value = int.from_bytes(hash_bytes[:8], byteorder='big')
        # Normalize to 0-1 range
        return value / (2**64 - 1)

    @staticmethod
    def uniform(hash_string, index, min_val, max_val):
        """Deterministic uniform distribution"""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        return min_val + rand_val * (max_val - min_val)

    @staticmethod
    def randint(hash_string, index, min_val, max_val):
        """Deterministic integer in range [min_val, max_val] inclusive"""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        return int(min_val + rand_val * (max_val - min_val + 1))

    @staticmethod
    def choice(hash_string, index, choices):
        """Deterministic choice from list"""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        idx = int(rand_val * len(choices))
        return choices[min(idx, len(choices) - 1)]


class RepositoryPalette:
    """Generate harmonious color palettes based on repository characteristics"""

    # Curated professional color schemes - each represents a language/ecosystem
    PALETTES = {
        # Python projects - Cool blues and teals (like the logo)
        'python': {
            'base': [(52, 152, 219), (41, 128, 185), (26, 188, 156)],  # Sky blue, Ocean, Teal
            'accents': [(236, 240, 241), (44, 62, 80)],  # Ice, Navy
            'bg_light': (245, 248, 250),
            'bg_dark': (52, 73, 94)
        },
        # JavaScript/Web - Warm yellows and oranges (like JS logo)
        'javascript': {
            'base': [(241, 196, 15), (230, 126, 34), (211, 84, 0)],  # Yellow, Orange, Deep orange
            'accents': [(254, 250, 224), (123, 63, 0)],  # Cream, Brown
            'bg_light': (255, 252, 244),
            'bg_dark': (100, 56, 14)
        },
        # PHP - Purple and violet (distinctive PHP identity)
        'php': {
            'base': [(142, 68, 173), (155, 89, 182), (187, 143, 206)],  # Purple, Violet, Lavender
            'accents': [(244, 236, 247), (74, 35, 90)],  # Light lavender, Deep purple
            'bg_light': (250, 244, 252),
            'bg_dark': (63, 31, 77)
        },
        # Java/Enterprise - Professional burgundy and brown
        'java': {
            'base': [(231, 76, 60), (192, 57, 43), (165, 105, 79)],  # Red, Crimson, Brown
            'accents': [(255, 235, 230), (120, 40, 31)],  # Light red, Dark brown
            'bg_light': (255, 245, 243),
            'bg_dark': (100, 30, 22)
        },
        # Ruby - Rich reds and gems
        'ruby': {
            'base': [(220, 20, 60), (178, 34, 34), (255, 99, 71)],  # Crimson, Firebrick, Tomato
            'accents': [(255, 240, 245), (139, 0, 0)],  # Lavender blush, Dark red
            'bg_light': (255, 250, 250),
            'bg_dark': (100, 0, 0)
        },
        # Go/Rust - Modern cyan and steel
        'systems': {
            'base': [(0, 173, 181), (52, 152, 219), (149, 165, 166)],  # Cyan, Blue, Steel
            'accents': [(236, 240, 241), (44, 62, 80)],  # Light gray, Dark blue
            'bg_light': (245, 248, 250),
            'bg_dark': (44, 62, 80)
        },
        # Data/Science - Natural greens
        'data': {
            'base': [(46, 204, 113), (39, 174, 96), (22, 160, 133)],  # Emerald, Green, Teal
            'accents': [(232, 248, 245), (27, 79, 69)],  # Mint, Forest
            'bg_light': (240, 252, 245),
            'bg_dark': (35, 67, 56)
        },
        # C/C++ - Industrial gray and blue
        'cpp': {
            'base': [(69, 85, 96), (52, 73, 94), (93, 109, 126)],  # Charcoal, Dark blue, Slate
            'accents': [(236, 240, 241), (33, 42, 48)],  # Light gray, Almost black
            'bg_light': (245, 248, 250),
            'bg_dark': (33, 42, 48)
        },
        # Mobile/Swift - Vibrant orange and pink
        'mobile': {
            'base': [(255, 107, 107), (255, 159, 64), (255, 118, 117)],  # Coral, Orange, Pink
            'accents': [(255, 244, 230), (92, 47, 43)],  # Cream, Deep brown
            'bg_light': (255, 250, 245),
            'bg_dark': (92, 53, 48)
        },
        # Documentation/Markdown - Elegant grays
        'documentation': {
            'base': [(120, 135, 145), (178, 190, 195), (149, 165, 166)],  # Slate, Silver, Gray
            'accents': [(245, 247, 248), (69, 85, 96)],  # Pearl, Charcoal
            'bg_light': (250, 251, 252),
            'bg_dark': (69, 85, 96)
        }
    }

    @staticmethod
    def select_palette_by_repo(fingerprint):
        """Select color palette based on repository language and type - visually readable"""
        file_types = fingerprint['file_types']
        total_lines = fingerprint['total_lines']
        num_files = len(fingerprint['files'])

        # Count lines per language for accurate detection
        py_lines = file_types.get('.py', 0)
        js_lines = sum(file_types.get(ext, 0) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue'])
        php_lines = file_types.get('.php', 0)
        java_lines = file_types.get('.java', 0)
        rb_lines = file_types.get('.rb', 0)
        go_lines = file_types.get('.go', 0)
        rs_lines = file_types.get('.rs', 0)
        cpp_lines = sum(file_types.get(ext, 0) for ext in ['.c', '.cpp', '.h', '.hpp', '.cc'])
        mobile_lines = sum(file_types.get(ext, 0) for ext in ['.swift', '.kt', '.m', '.mm'])
        md_lines = file_types.get('.md', 0)
        data_lines = sum(file_types.get(ext, 0) for ext in ['.csv', '.json', '.xml', '.yaml', '.yml'])

        # Calculate dominant language (>30% of codebase)
        threshold = total_lines * 0.3

        # Priority: Most specific to least specific
        # 1. Primary languages (clear majority)
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
        elif js_lines > threshold:
            palette_name = 'javascript'
        elif py_lines > threshold:
            # Check if it's data science focused
            if data_lines > total_lines * 0.2:
                palette_name = 'data'
            else:
                palette_name = 'python'
        # 2. Documentation-heavy repos
        elif md_lines > total_lines * 0.5 and num_files <= 10:
            palette_name = 'documentation'
        # 3. Mixed/small repos - deterministic fallback
        else:
            # Deterministic based on dominant file type
            if file_types:
                sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                dominant_ext = sorted_types[0][0]
                # Map extension to palette
                ext_map = {
                    '.py': 'python', '.js': 'javascript', '.php': 'php',
                    '.java': 'java', '.rb': 'ruby', '.go': 'systems',
                    '.rs': 'systems', '.c': 'cpp', '.cpp': 'cpp',
                    '.swift': 'mobile', '.md': 'documentation'
                }
                palette_name = ext_map.get(dominant_ext, 'documentation')
            else:
                palette_name = 'documentation'

        return palette_name, RepositoryPalette.PALETTES[palette_name]

    @staticmethod
    def expand_palette(palette_dict, seed):
        """Expand palette with harmonious variations and complementary accents"""
        expanded = []
        base_colors = palette_dict['base']
        accent_colors = palette_dict['accents']

        # Add all base colors
        expanded.extend(base_colors)

        # Add tints, shades, and complementary colors for each base color
        random.seed(seed)
        for color in base_colors:
            r, g, b = color
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

            # INCREASED CONTRAST: Much lighter tints
            tint = RepositoryPalette._hsv_to_rgb(h, s * 0.4, min(1.0, v * 1.3))
            expanded.append(tint)

            # INCREASED CONTRAST: Much darker shades
            shade = RepositoryPalette._hsv_to_rgb(h, min(1.0, s * 1.2), v * 0.5)
            expanded.append(shade)

            # Add complementary color (opposite on color wheel)
            complementary_h = (h + 0.5) % 1.0
            complementary = RepositoryPalette._hsv_to_rgb(complementary_h, s * 0.9, v * 0.95)
            expanded.append(complementary)

        # Add accents
        expanded.extend(accent_colors)

        return expanded

    @staticmethod
    def get_complementary_color(color):
        """Get complementary color (opposite on color wheel)"""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        comp_h = (h + 0.5) % 1.0
        return RepositoryPalette._hsv_to_rgb(comp_h, s, v)

    @staticmethod
    def get_triadic_colors(color):
        """Get triadic colors (120 degrees apart on color wheel)"""
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
        """Get split-complementary colors (complement +/- 30 degrees)"""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        comp_h = (h + 0.5) % 1.0
        split1_h = (comp_h - 0.083) % 1.0  # -30 degrees
        split2_h = (comp_h + 0.083) % 1.0  # +30 degrees

        return [
            RepositoryPalette._hsv_to_rgb(split1_h, s, v),
            RepositoryPalette._hsv_to_rgb(split2_h, s, v)
        ]

    @staticmethod
    def get_tetradic_colors(color):
        """Get tetradic colors (rectangle on color wheel)"""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Rectangle: base, +60, +180, +240 degrees
        tet1_h = (h + 0.167) % 1.0  # +60 degrees
        tet2_h = (h + 0.5) % 1.0    # +180 degrees (complement)
        tet3_h = (h + 0.667) % 1.0  # +240 degrees

        return [
            RepositoryPalette._hsv_to_rgb(tet1_h, s, v),
            RepositoryPalette._hsv_to_rgb(tet2_h, s, v),
            RepositoryPalette._hsv_to_rgb(tet3_h, s, v)
        ]

    @staticmethod
    def expand_palette_with_theory(palette_dict, seed, contrast='high'):
        """Expand palette using advanced color wheel theory with adjustable contrast

        Args:
            palette_dict: Palette dictionary with base/accent colors
            seed: Random seed for determinism
            contrast: 'low', 'medium', or 'high' - controls tint/shade brightness
        """
        expanded = []
        base_colors = palette_dict['base']
        accent_colors = palette_dict['accents']

        # Contrast multipliers for tints and shades
        contrast_settings = {
            'low': {'tint': 1.15, 'shade': 0.7, 'sat_tint': 0.6, 'sat_shade': 1.1},
            'medium': {'tint': 1.25, 'shade': 0.55, 'sat_tint': 0.5, 'sat_shade': 1.2},
            'high': {'tint': 1.4, 'shade': 0.4, 'sat_tint': 0.3, 'sat_shade': 1.3}
        }

        settings = contrast_settings.get(contrast, contrast_settings['high'])

        random.seed(seed)

        # Add base colors
        expanded.extend(base_colors)

        # For each base color, add color theory variations
        for i, color in enumerate(base_colors):
            r, g, b = color
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

            # Contrast-adjusted variations
            very_light = RepositoryPalette._hsv_to_rgb(h, s * settings['sat_tint'], min(1.0, v * settings['tint']))
            very_dark = RepositoryPalette._hsv_to_rgb(h, min(1.0, s * settings['sat_shade']), v * settings['shade'])
            expanded.extend([very_light, very_dark])

            # Use different color theory for each base color
            if i % 3 == 0:
                # Complementary
                expanded.append(RepositoryPalette.get_complementary_color(color))
            elif i % 3 == 1:
                # Triadic
                expanded.extend(RepositoryPalette.get_triadic_colors(color))
            else:
                # Split-complementary
                expanded.extend(RepositoryPalette.get_split_complementary_colors(color))

        # Add tetradic colors for visual pop
        if len(base_colors) > 0:
            primary = base_colors[0]
            tetradic = RepositoryPalette.get_tetradic_colors(primary)
            expanded.extend(tetradic)

        # Add accents
        expanded.extend(accent_colors)

        return expanded

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        """Convert HSV to RGB (0-255)"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))


class ColorMixer:
    """Deterministic color mixing utilities"""

    @staticmethod
    def blend_colors(colors, seed_hash, count=2):
        """Blend multiple colors with deterministic ratios

        Args:
            colors: List of RGB tuples to choose from
            seed_hash: Hash string for deterministic selection
            count: Number of colors to blend (2-4)

        Returns:
            Blended RGB tuple
        """
        count = max(2, min(4, count))  # Clamp between 2-4

        # Select colors deterministically
        selected_colors = []
        for i in range(count):
            idx = DeterministicRandom.randint(seed_hash, 2000 + i, 0, len(colors) - 1)
            selected_colors.append(colors[idx])

        # Generate deterministic mixing ratios that sum to 1.0
        ratios = []
        for i in range(count):
            ratio = DeterministicRandom.uniform(seed_hash, 2100 + i, 0.1, 1.0)
            ratios.append(ratio)

        # Normalize to sum to 1.0
        total = sum(ratios)
        ratios = [r / total for r in ratios]

        # Blend colors according to ratios
        r, g, b = 0, 0, 0
        for color, ratio in zip(selected_colors, ratios):
            r += color[0] * ratio
            g += color[1] * ratio
            b += color[2] * ratio

        return (int(r), int(g), int(b))

    @staticmethod
    def get_analogous_variation(color, seed_hash, shift_range=0.05):
        """Get analogous color variation (nearby on color wheel)

        Args:
            color: Base RGB tuple
            seed_hash: Hash for deterministic variation
            shift_range: Maximum hue shift (0.05 = 18 degrees)

        Returns:
            Analogous RGB tuple
        """
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Deterministic hue shift
        shift = DeterministicRandom.uniform(seed_hash, 2200, -shift_range, shift_range)
        new_h = (h + shift) % 1.0

        # Slight saturation and value variations
        s_var = DeterministicRandom.uniform(seed_hash, 2201, 0.9, 1.1)
        v_var = DeterministicRandom.uniform(seed_hash, 2202, 0.9, 1.1)

        new_s = max(0, min(1.0, s * s_var))
        new_v = max(0, min(1.0, v * v_var))

        r_new, g_new, b_new = colorsys.hsv_to_rgb(new_h, new_s, new_v)
        return (int(r_new * 255), int(g_new * 255), int(b_new * 255))


class OrganicShapes:
    """Generate flowing, organic shapes with advanced effects"""

    @staticmethod
    def flowing_line(start, end, curviness=0.3, segments=50):
        """Generate flowing bezier curve"""
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
        """Generate spiral pattern"""
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
        """Generate circular loop"""
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
        """Generate rotating elements around a center"""
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
        """Generate particle burst"""
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
        """Generate wave pattern"""
        points = []
        for i in range(segments + 1):
            x = (i / segments) * width
            y = y_base + amplitude * math.sin(frequency * x / 100 + phase)
            points.append((x, y))
        return points

    @staticmethod
    def cornu_inspired_curve(start, end, curvature_factor, segments=150):
        """Generate Cornu-inspired (Euler spiral) curve with smooth curvature change"""
        x1, y1 = start
        x2, y2 = end
        points = []

        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)

        for i in range(segments + 1):
            t = i / segments

            # Smooth curvature increase (like Euler spiral/Cornu curve)
            # Curvature increases linearly with arc length
            theta = curvature_factor * t * t  # Quadratic for smooth transition

            # Position along the curve
            s = t * length
            x = x1 + dx * t + dy * math.sin(theta) * 0.3
            y = y1 + dy * t - dx * math.sin(theta) * 0.3

            points.append((x, y))

        return points

    @staticmethod
    def generate_texture_lines(center, radius, count, seed):
        """Generate many small texture lines for rich detail (IDEO style)"""
        cx, cy = center
        lines = []
        random.seed(seed)

        for i in range(count):
            # Random position around center
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius)
            x = cx + dist * math.cos(angle)
            y = cy + dist * math.sin(angle)

            # Small random line
            line_angle = random.uniform(0, 2 * math.pi)
            line_length = random.uniform(2, 15)
            x2 = x + line_length * math.cos(line_angle)
            y2 = y + line_length * math.sin(line_angle)

            opacity = random.randint(10, 80)
            thickness = random.uniform(0.5, 2)

            lines.append(((x, y), (x2, y2), opacity, thickness))

        return lines


class GitArtGenerator:
    # Common canvas aspect ratios
    ASPECT_RATIOS = {
        'square': (1, 1),
        '16:10': (16, 10),
        '16:9': (16, 9),
        '3:2': (3, 2),
        '4:3': (4, 3),
        '5:4': (5, 4),
        'portrait_3:4': (3, 4),
        'portrait_2:3': (2, 3),
    }

    # Common canvas sizes
    CANVAS_SIZES = {
        'medium': (1200, 1200),
        'large': (1600, 1200),   # 4:3 landscape
        'xlarge': (1920, 1200),  # 16:10 landscape
        'social': (1800, 1200),  # 3:2 landscape
        'hd': (1920, 1080),      # 16:9 landscape
        'portrait': (1200, 1600), # 3:4 portrait
    }

    @staticmethod
    def detect_aspect_ratio(fingerprint):
        """
        Automatically detect aspect ratio based on repository characteristics

        Portrait (3:4) - Mobile apps (Swift, Kotlin, Dart, Java+Android)
        Landscape (16:9) - Web frontends, documentation-heavy
        Square (1:1) - Backend, libraries, general purpose

        Returns:
            str: Aspect ratio name ('portrait_3:4', '16:9', or 'square')
        """
        file_types = fingerprint['file_types']
        total_lines = fingerprint['total_lines']

        if total_lines == 0:
            return 'square'

        # Calculate percentages for different categories
        mobile_lines = sum(file_types.get(ext, 0) for ext in ['.swift', '.kt', '.dart', '.m', '.mm'])
        mobile_pct = mobile_lines / total_lines

        web_lines = sum(file_types.get(ext, 0) for ext in ['.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'])
        web_pct = web_lines / total_lines

        doc_lines = sum(file_types.get(ext, 0) for ext in ['.md', '.rst', '.txt'])
        doc_pct = doc_lines / total_lines

        # Detection rules (lowered thresholds for polyglot projects)
        if mobile_pct > 0.15:
            return 'portrait_3:4'
        elif web_pct > 0.25 or doc_pct > 0.40:
            return '16:9'
        else:
            return 'square'

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', contrast='high'):
        """
        Initialize art generator

        Args:
            repo_path: Path to git repository
            width: Canvas width (ignored if aspect_ratio is specified)
            height: Canvas height (ignored if aspect_ratio is specified)
            aspect_ratio: Aspect ratio name from ASPECT_RATIOS or 'auto' for automatic detection
            contrast: Contrast level for color palette ('low', 'medium', 'high')
        """
        self.repo = git.Repo(repo_path)
        self.repo_path = Path(repo_path)
        self.contrast = contrast

        # Auto-detect aspect ratio if requested
        if aspect_ratio == 'auto':
            fingerprint = self.get_repo_fingerprint()
            aspect_ratio = self.detect_aspect_ratio(fingerprint)

        # Apply aspect ratio if specified
        if aspect_ratio and aspect_ratio in self.ASPECT_RATIOS:
            ratio_w, ratio_h = self.ASPECT_RATIOS[aspect_ratio]
            # Use width as the base dimension
            self.width = width
            self.height = int(width * ratio_h / ratio_w)
            self.aspect_ratio = aspect_ratio
        else:
            self.width = width
            self.height = height
            self.aspect_ratio = 'custom'

    def get_repo_fingerprint(self):
        """Generate repository fingerprint"""
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
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
                          '.pdf', '.zip', '.tar', '.gz', '.bin', '.exe'}
        skip_names = {'package-lock.json', 'yarn.lock', '.gitattributes'}
        path = Path(file_path)
        return path.suffix in skip_extensions or path.name in skip_names

    def generate_art(self, output_path='repo_art.png'):
        """Generate harmonious generative art with smooth, soft finish"""
        fingerprint = self.get_repo_fingerprint()

        # Get harmonious palette with advanced color theory
        palette_name, palette_dict = RepositoryPalette.select_palette_by_repo(fingerprint)
        all_colors = RepositoryPalette.expand_palette_with_theory(palette_dict, fingerprint['total_lines'], self.contrast)

        # Create background
        img = self._create_background(fingerprint, palette_dict)

        draw = ImageDraw.Draw(img, 'RGBA')

        # Add layers of elements with MIXED ordering for depth
        # Interleave background and foreground to create visual complexity

        # Layer 1: Deep background elements
        self._add_filled_color_areas(draw, fingerprint, all_colors)
        self._add_background_flows(draw, fingerprint, all_colors)

        # Layer 2: Some main elements (largest ones first for depth)
        self._draw_some_main_elements(draw, fingerprint, all_colors, start_idx=0, count=3)

        # Layer 3: Mid-ground texture and curves
        self._add_cornu_curves(draw, fingerprint, all_colors)
        self._add_bold_color_blocks(draw, fingerprint, all_colors)

        # Layer 4: More main elements
        self._draw_some_main_elements(draw, fingerprint, all_colors, start_idx=3, count=5)

        # Layer 5: Decorative elements
        self._add_spirals(draw, fingerprint, all_colors)
        self._add_circular_loops(draw, fingerprint, all_colors)

        # Layer 6: Remaining main elements (smaller ones on top)
        self._draw_some_main_elements(draw, fingerprint, all_colors, start_idx=8, count=None)

        # Layer 7: Fine details and texture
        self._add_rich_texture(draw, fingerprint, all_colors)
        self._add_rotating_elements(draw, fingerprint, all_colors)
        self._add_connections(draw, fingerprint, all_colors)
        self._add_particles(draw, fingerprint, all_colors)
        self._add_waves_with_fade(draw, fingerprint, all_colors)

        # Apply final smoothing for soft, polished finish
        img = self._apply_soft_finish(img, fingerprint)

        img.save(output_path, quality=95)
        print(f"🎨 Art generated: {output_path}")
        print(f"📐 Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"📊 {len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines, "
              f"{fingerprint['commit_count']} commits")
        print(f"🌈 Palette: '{palette_name}' ({len(all_colors)} harmonious colors)")

        return output_path

    def _apply_soft_finish(self, img, fingerprint):
        """Apply very light smoothing for subtle polish without losing sharpness"""
        # Much lighter blur - just to soften harsh edges slightly
        blur_radius = 0.3

        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        return img

    def _create_background(self, fingerprint, palette_dict):
        """Create dynamic, interesting background with color variations"""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        base_colors = palette_dict['base']
        bg_light = palette_dict['bg_light']
        bg_dark = palette_dict['bg_dark']

        # Create multiple gradient centers for dynamic effect
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_centers = 3 + (fingerprint['commit_count'] % 3)
        centers = []

        for i in range(num_centers):
            cx = random.randint(int(self.width * 0.2), int(self.width * 0.8))
            cy = random.randint(int(self.height * 0.2), int(self.height * 0.8))
            color_idx = i % len(base_colors)
            # Use lighter versions of base colors for background
            r, g, b = base_colors[color_idx]
            # Lighten the colors significantly for background
            light_color = (
                min(255, int(r + (255 - r) * 0.6)),
                min(255, int(g + (255 - g) * 0.6)),
                min(255, int(b + (255 - b) * 0.6))
            )
            centers.append((cx, cy, light_color))

        for y in range(self.height):
            for x in range(self.width):
                # Calculate influence from each center
                influences = []
                colors_at_point = []

                for cx, cy, color in centers:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    max_dist = math.sqrt(self.width**2 + self.height**2)
                    influence = max(0, 1 - (dist / max_dist) ** 0.8)
                    influences.append(influence)
                    colors_at_point.append(color)

                # Add corner influence for overall gradient
                corner_ratio = (x + y) / (self.width + self.height)
                corner_influence = 0.3

                total_influence = sum(influences) + corner_influence
                r, g, b = 0, 0, 0

                # Blend center colors
                for i, influence in enumerate(influences):
                    weight = influence / total_influence
                    cr, cg, cb = colors_at_point[i]
                    r += cr * weight
                    g += cg * weight
                    b += cb * weight

                # Add corner gradient
                corner_weight = corner_influence / total_influence
                r += bg_light[0] * (1 - corner_ratio) * corner_weight + bg_dark[0] * corner_ratio * corner_weight
                g += bg_light[1] * (1 - corner_ratio) * corner_weight + bg_dark[1] * corner_ratio * corner_weight
                b += bg_light[2] * (1 - corner_ratio) * corner_weight + bg_dark[2] * corner_ratio * corner_weight

                pixels[x, y] = (int(r), int(g), int(b))

        return img

    def _add_filled_color_areas(self, draw, fingerprint, colors):
        """Add large filled color areas for bold visual impact with sophisticated color mixing"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_areas = 3 + (fingerprint['commit_count'] % 5)

        for i in range(num_areas):
            # Create unique hash for this area
            area_hash = hashlib.md5(f"{seed}_{i}_area".encode()).hexdigest()

            # Large organic filled shapes
            cx = DeterministicRandom.randint(area_hash, 0, 0, self.width)
            cy = DeterministicRandom.randint(area_hash, 1, 0, self.height)

            # Make HUGE shapes
            size = DeterministicRandom.randint(area_hash, 2, int(self.width * 0.2), int(self.width * 0.5))

            # Generate organic blob shape
            segments = DeterministicRandom.randint(area_hash, 3, 6, 12)
            points = []
            for j in range(segments):
                angle = (j / segments) * 2 * math.pi
                variation = DeterministicRandom.uniform(area_hash, 100 + j, 0.7, 1.3)
                radius = size * variation
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                points.append((px, py))

            # Use sophisticated color mixing with deterministic ratios
            blend_count = DeterministicRandom.choice(area_hash, 4, [2, 2, 3, 3, 4])
            blended = ColorMixer.blend_colors(colors, area_hash, blend_count)

            opacity = DeterministicRandom.randint(area_hash, 5, 40, 100)

            draw.polygon(points, fill=blended + (opacity,))

    def _add_bold_color_blocks(self, draw, fingerprint, colors):
        """Add bold rectangular color blocks with sophisticated color mixing"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_blocks = 4 + (len(fingerprint['files']) % 6)

        for i in range(num_blocks):
            # Create unique hash for this block
            block_hash = hashlib.md5(f"{seed}_{i}_block".encode()).hexdigest()

            # Large rectangles at various angles
            x = DeterministicRandom.randint(block_hash, 0, -self.width // 4, self.width)
            y = DeterministicRandom.randint(block_hash, 1, -self.height // 4, self.height)

            width = DeterministicRandom.randint(block_hash, 2, int(self.width * 0.15), int(self.width * 0.40))
            height = DeterministicRandom.randint(block_hash, 3, int(self.height * 0.10), int(self.height * 0.30))

            # Rotate rectangle
            angle = DeterministicRandom.uniform(block_hash, 4, 0, math.pi)

            # Create rotated rectangle points
            corners = [
                (x, y),
                (x + width * math.cos(angle), y + width * math.sin(angle)),
                (x + width * math.cos(angle) - height * math.sin(angle),
                 y + width * math.sin(angle) + height * math.cos(angle)),
                (x - height * math.sin(angle), y + height * math.cos(angle))
            ]

            # Use sophisticated color mixing (typically 3-4 colors)
            blend_count = DeterministicRandom.choice(block_hash, 5, [3, 3, 3, 4])
            mixed = ColorMixer.blend_colors(colors, block_hash, blend_count)

            opacity = DeterministicRandom.randint(block_hash, 6, 50, 120)

            draw.polygon(corners, fill=mixed + (opacity,))

    def _add_background_flows(self, draw, fingerprint, colors):
        """Add flowing background lines - BOLD and THICK"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_flows = 8 + (fingerprint['commit_count'] % 10)

        for i in range(num_flows):
            x1 = random.randint(-self.width // 2, self.width + self.width // 2)
            y1 = random.randint(-self.height // 2, self.height + self.height // 2)
            x2 = random.randint(-self.width // 2, self.width + self.width // 2)
            y2 = random.randint(-self.height // 2, self.height + self.height // 2)

            points = OrganicShapes.flowing_line(
                (x1, y1), (x2, y2),
                curviness=random.uniform(0.3, 0.6),
                segments=100
            )

            color = colors[i % len(colors)]

            # SUPER THICK lines - up to 30% of canvas width!
            if random.random() < 0.3:
                # Occasionally MASSIVE strokes
                stroke_width = random.randint(int(self.width * 0.15), int(self.width * 0.30))
            else:
                # Still very thick
                stroke_width = random.randint(int(self.width * 0.05), int(self.width * 0.15))

            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]],
                         fill=color + (random.randint(60, 120),),  # Varied opacity
                         width=stroke_width)

    def _add_cornu_curves(self, draw, fingerprint, colors):
        """Add Cornu/Euler spiral curves - IDEO Tsunami style with hundreds of curves"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        # Generate many curves (50-100) like the Tsunami artwork
        num_curves = 50 + (fingerprint['commit_count'] * 5)

        for i in range(num_curves):
            x1 = random.randint(-self.width // 4, self.width + self.width // 4)
            y1 = random.randint(-self.height // 4, self.height + self.height // 4)
            x2 = random.randint(-self.width // 4, self.width + self.width // 4)
            y2 = random.randint(-self.height // 4, self.height + self.height // 4)

            curvature = random.uniform(2, 8)

            points = OrganicShapes.cornu_inspired_curve((x1, y1), (x2, y2), curvature, segments=120)

            # Select color from palette
            color = colors[i % len(colors)]

            # BOLD stroke widths - much thicker!
            if random.random() < 0.4:
                stroke_width = random.randint(int(self.width * 0.01), int(self.width * 0.08))  # Thick
            elif random.random() < 0.7:
                stroke_width = random.randint(int(self.width * 0.08), int(self.width * 0.20))  # Very thick
            else:
                stroke_width = random.randint(int(self.width * 0.20), int(self.width * 0.30))  # MASSIVE

            # Vary opacity
            opacity = random.randint(40, 150)

            # Draw the curve
            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]],
                         fill=color + (opacity,),
                         width=int(stroke_width))

    def _add_rich_texture(self, draw, fingerprint, colors):
        """Add thousands of micro-lines for rich texture - IDEO 'All Seeing Eye' style"""
        seed = fingerprint['total_lines']

        # Add texture around main elements
        files = list(fingerprint['files'].items())
        if not files:
            return

        # Generate texture for top 3 files (millions of lines would be slow, so thousands)
        for idx, (file_path, file_data) in enumerate(files[:3]):
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius_pos = 60 + idx * (min(self.width, self.height) / (2.2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius_pos * math.cos(angle)
            y = cy + radius_pos * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)

            # Generate thousands of tiny lines (IDEO: millions, but we'll do thousands for performance)
            texture_radius = 80 + idx * 30
            num_lines = 500 + (file_data['lines'] * 5)  # More lines for larger files

            texture_lines = OrganicShapes.generate_texture_lines((x, y), texture_radius, num_lines, hash_val)

            color = colors[hash_val % len(colors)]

            for (x1, y1), (x2, y2), opacity, thickness in texture_lines:
                draw.line([(x1, y1), (x2, y2)],
                         fill=color + (opacity,),
                         width=int(thickness))

    def _draw_some_main_elements(self, draw, fingerprint, colors, start_idx=0, count=None):
        """Draw a subset of main elements for layered composition"""
        files = fingerprint['files']
        if not files:
            return

        sorted_files = sorted(files.items(), key=lambda x: x[1]['lines'], reverse=True)

        # Determine which elements to draw
        if count is None:
            # Draw from start_idx to end
            elements_to_draw = sorted_files[start_idx:]
        else:
            # Draw specific count starting from start_idx
            elements_to_draw = sorted_files[start_idx:start_idx + count]

        for idx, (file_path, file_data) in enumerate(elements_to_draw):
            # Use original index for consistent positioning
            original_idx = start_idx + idx
            self._draw_single_element(draw, original_idx, file_data, colors, len(sorted_files))

    def _draw_main_elements(self, draw, fingerprint, colors):
        """Draw main file elements with extreme variety in size, shape, and placement"""
        files = fingerprint['files']
        if not files:
            return

        sorted_files = sorted(files.items(), key=lambda x: x[1]['lines'], reverse=True)

        for idx, (file_path, file_data) in enumerate(sorted_files):
            self._draw_single_element(draw, idx, file_data, colors, len(sorted_files))

    def _draw_single_element(self, draw, idx, file_data, colors, total_files):
        """Draw a single main element - 100% deterministic based on file hash"""
        golden_angle = 137.508
        angle = (idx * golden_angle) * (math.pi / 180)

        # DETERMINISTIC positioning based on file hash
        file_hash = file_data['hash']

        # Mix golden spiral with hash-based placement
        if idx < 3:
            # First 3 files use golden spiral but with wider radius
            radius = DeterministicRandom.randint(file_hash, 0, 50, min(self.width, self.height) // 3)
        else:
            # Others spread based on hash
            radius = DeterministicRandom.randint(file_hash, 0, 0, int(min(self.width, self.height) * 0.4))

        cx, cy = self.width / 2, self.height / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        # Calculate normalized size (we don't have access to all files here, so estimate)
        normalized_size = min(1.0, file_data['lines'] / 500.0)  # Rough normalization

        # EXTREME SIZE VARIETY - from tiny to 70% of canvas!
        min_size = int(min(self.width, self.height) * 0.03)  # 3% minimum
        max_size = int(min(self.width, self.height) * 0.70)  # 70% maximum!
        size = min_size + normalized_size * (max_size - min_size)

        # Add deterministic variation based on hash
        size_variation = DeterministicRandom.uniform(file_hash, 1, 0.6, 1.4)
        size = int(size * size_variation)

        hash_val = int(file_hash[:8], 16)
        color = colors[hash_val % len(colors)]

        # Choose different shape types based on hash
        shape_type = hash_val % 5
        self._draw_varied_shape(draw, x, y, size, color, file_hash, shape_type)

    def _draw_varied_shape(self, draw, x, y, size, color, seed_hash, shape_type):
        """Draw varied shapes: blob, star, polygon, stretched blob, or splatter - 100% deterministic"""
        if shape_type == 0:
            # Organic blob (original)
            self._draw_blob(draw, x, y, size, color, seed_hash)
        elif shape_type == 1:
            # Star/spiky shape
            self._draw_star_shape(draw, x, y, size, color, seed_hash)
        elif shape_type == 2:
            # Angular polygon (triangle, pentagon, hexagon)
            self._draw_polygon_shape(draw, x, y, size, color, seed_hash)
        elif shape_type == 3:
            # Stretched/elongated blob
            self._draw_stretched_blob(draw, x, y, size, color, seed_hash)
        else:
            # Splatter/irregular shape
            self._draw_splatter_shape(draw, x, y, size, color, seed_hash)

    def _draw_blob(self, draw, x, y, size, color, seed_hash):
        """Draw organic blob - 100% deterministic"""
        points = []
        segments = DeterministicRandom.randint(seed_hash, 0, 12, 24)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            # Deterministic variation based on hash + index
            rand_variation = DeterministicRandom.uniform(seed_hash, i * 2, -0.3, 0.4)
            sin_freq = DeterministicRandom.randint(seed_hash, i * 2 + 1, 2, 5)
            variation = 1 + rand_variation + 0.2 * math.sin(angle * sin_freq)
            radius = (size / 2) * variation
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_star_shape(self, draw, x, y, size, color, seed_hash):
        """Draw star/spiky shape - 100% deterministic"""
        points = []
        num_spikes = DeterministicRandom.randint(seed_hash, 100, 5, 12)

        for i in range(num_spikes * 2):
            angle = (i / (num_spikes * 2)) * 2 * math.pi
            if i % 2 == 0:
                # Outer spike
                radius = size / 2 * DeterministicRandom.uniform(seed_hash, 200 + i, 0.8, 1.2)
            else:
                # Inner valley
                radius = size / 2 * DeterministicRandom.uniform(seed_hash, 200 + i, 0.3, 0.6)

            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_polygon_shape(self, draw, x, y, size, color, seed_hash):
        """Draw smooth polygon shape with rounded corners - 100% deterministic"""
        points = []
        num_sides = DeterministicRandom.choice(seed_hash, 300, [5, 6, 7, 8, 10, 12])  # More sides for smoother
        rotation = DeterministicRandom.uniform(seed_hash, 301, 0, math.pi)

        # Generate more points between corners for smooth curves
        segments_per_side = 3  # Add intermediate points for smoothness
        for i in range(num_sides * segments_per_side):
            base_angle = (i / (num_sides * segments_per_side)) * 2 * math.pi + rotation
            side_idx = i // segments_per_side
            within_side = (i % segments_per_side) / segments_per_side

            # Interpolate radius for smooth transitions
            radius_var1 = DeterministicRandom.uniform(seed_hash, 400 + side_idx, 0.9, 1.1)
            radius_var2 = DeterministicRandom.uniform(seed_hash, 400 + side_idx + 1, 0.9, 1.1)
            radius_var = radius_var1 + (radius_var2 - radius_var1) * within_side

            radius = size / 2 * radius_var
            px = x + radius * math.cos(base_angle)
            py = y + radius * math.sin(base_angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_stretched_blob(self, draw, x, y, size, color, seed_hash):
        """Draw stretched/elongated organic shape - 100% deterministic"""
        points = []
        segments = DeterministicRandom.randint(seed_hash, 500, 15, 25)
        stretch_angle = DeterministicRandom.uniform(seed_hash, 501, 0, math.pi)
        stretch_factor = DeterministicRandom.uniform(seed_hash, 502, 1.5, 3.0)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            variation = 1 + DeterministicRandom.uniform(seed_hash, 600 + i, -0.2, 0.3)

            # Stretch along one axis
            radius_x = (size / 2) * variation
            radius_y = (size / 2) * variation / stretch_factor

            # Rotate the stretch
            local_x = radius_x * math.cos(angle)
            local_y = radius_y * math.sin(angle)

            px = x + local_x * math.cos(stretch_angle) - local_y * math.sin(stretch_angle)
            py = y + local_x * math.sin(stretch_angle) + local_y * math.cos(stretch_angle)
            points.append((px, py))

        self._draw_layered_shape(draw, points, color, seed_hash)

    def _draw_splatter_shape(self, draw, x, y, size, color, seed_hash):
        """Draw irregular splatter shape - 100% deterministic"""
        points = []
        segments = DeterministicRandom.randint(seed_hash, 700, 20, 40)

        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            # Extreme variation for splatter effect
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
        """Draw shape with multiple gradient layers using analogous and complementary variations - 100% deterministic"""
        # Convert to HSV for hue variations
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Calculate centroid
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)

        # Determine color variation strategy based on hash
        use_complementary = DeterministicRandom.from_hash(seed_hash, 900) > 0.7

        # Draw multiple layers with gradient effect
        num_layers = DeterministicRandom.randint(seed_hash, 1000, 6, 10)
        for layer in range(num_layers, 0, -1):
            layer_ratio = layer / num_layers

            # Scale points toward centroid
            layer_points = []
            for px, py in points:
                lx = cx + (px - cx) * layer_ratio
                ly = cy + (py - cy) * layer_ratio
                layer_points.append((lx, ly))

            if use_complementary and layer < num_layers // 2:
                # Use complementary color for inner layers (visual pop!)
                comp_h = (h + 0.5) % 1.0
                layer_h = comp_h
                # Adjust saturation and value for complementary
                layer_s = s * DeterministicRandom.uniform(seed_hash, 1100 + layer, 0.7, 1.1)
                v_var = DeterministicRandom.uniform(seed_hash, 1200 + layer, 0.1, 0.3)
                layer_v = min(1.0, v + (1 - layer_ratio) * v_var)
            else:
                # Use analogous variation (subtle hue shifts)
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

        # Add outer glow using analogous variation
        shadow_points = []
        for i, (px, py) in enumerate(points):
            expansion = DeterministicRandom.uniform(seed_hash, 1400 + i, 1.08, 1.2)
            sx = cx + (px - cx) * expansion
            sy = cy + (py - cy) * expansion
            shadow_points.append((sx, sy))

        # Use analogous color for shadow (more cohesive)
        shadow_color = ColorMixer.get_analogous_variation(color, seed_hash, shift_range=0.03)
        # Darken the analogous color
        sr, sg, sb = shadow_color
        darker = (max(0, sr - DeterministicRandom.randint(seed_hash, 1500, 30, 60)),
                  max(0, sg - DeterministicRandom.randint(seed_hash, 1501, 30, 60)),
                  max(0, sb - DeterministicRandom.randint(seed_hash, 1502, 30, 60)))
        shadow_opacity = DeterministicRandom.randint(seed_hash, 1503, 40, 80)
        if len(shadow_points) > 2:
            draw.polygon(shadow_points, fill=darker + (shadow_opacity,))

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB tuple"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def _add_connections(self, draw, fingerprint, colors):
        """Add connection lines"""
        files = list(fingerprint['files'].items())
        if len(files) < 2:
            return

        seed = fingerprint['total_lines']
        random.seed(seed)

        connections = min(len(files) * 2, 30)

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

            points = OrganicShapes.flowing_line(
                (x1, y1), (x2, y2),
                curviness=random.uniform(0.3, 0.5),  # More curviness for smoother flow
                segments=80  # More segments for smoother curves
            )

            color = colors[i % len(colors)]

            for j in range(len(points) - 1):
                thickness = 2 + int(4 * math.sin((j / len(points)) * math.pi))  # Thicker
                draw.line([points[j], points[j+1]],
                         fill=color + (100,),  # More opaque
                         width=thickness)

    def _add_particles(self, draw, fingerprint, colors):
        """Add particle effects"""
        files = list(fingerprint['files'].items())
        if not files:
            return

        for idx, (file_path, file_data) in enumerate(files[:5]):
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius = 60 + idx * (min(self.width, self.height) / (2.2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)
            particle_count = 18 + (file_data['lines'] // 15)  # More particles

            particles = OrganicShapes.particle_burst((x, y), particle_count, 30, 80, hash_val)  # Larger radius

            color = colors[hash_val % len(colors)]

            for px, py, size in particles:
                larger_size = size * 1.5  # Make particles bigger
                draw.ellipse(
                    [px - larger_size/2, py - larger_size/2, px + larger_size/2, py + larger_size/2],
                    fill=color + (170,)  # More opaque
                )

    def _add_spirals(self, draw, fingerprint, colors):
        """Add smooth spiral patterns emanating from key points"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        # MORE spirals for smoother, more organic look
        num_spirals = 5 + (fingerprint['commit_count'] % 5)

        for i in range(num_spirals):
            cx = random.randint(int(self.width * 0.1), int(self.width * 0.9))
            cy = random.randint(int(self.height * 0.1), int(self.height * 0.9))

            start_radius = random.randint(5, 20)
            end_radius = random.randint(80, 250)
            turns = random.uniform(3, 6)  # More turns for smoother spirals

            # MORE segments for ultra-smooth curves
            points = OrganicShapes.spiral_pattern((cx, cy), start_radius, end_radius, turns, segments=300)

            color = colors[i % len(colors)]

            # Draw spiral with fading opacity
            for j in range(len(points) - 1):
                fade_ratio = j / len(points)
                opacity = int(80 * (1 - fade_ratio))  # Fade out
                thickness = max(1, int(5 * (1 - fade_ratio * 0.5)))  # Thinner as it spirals

                draw.line([points[j], points[j+1]],
                         fill=color + (opacity,),
                         width=thickness)

    def _add_circular_loops(self, draw, fingerprint, colors):
        """Add concentric circular loops"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_loop_centers = 2 + (len(fingerprint['files']) % 3)

        for i in range(num_loop_centers):
            cx = random.randint(int(self.width * 0.15), int(self.width * 0.85))
            cy = random.randint(int(self.height * 0.15), int(self.height * 0.85))

            num_loops = random.randint(3, 6)
            base_radius = random.randint(30, 60)

            for loop in range(num_loops):
                radius = base_radius + loop * random.randint(15, 30)
                points = OrganicShapes.circle_loop((cx, cy), radius, segments=80)

                color = colors[(i + loop) % len(colors)]
                opacity = max(20, int(70 - loop * 10))  # Fade outward

                for j in range(len(points) - 1):
                    draw.line([points[j], points[j+1]],
                             fill=color + (opacity,),
                             width=2)

    def _add_rotating_elements(self, draw, fingerprint, colors):
        """Add rotating circular elements around main objects"""
        files = list(fingerprint['files'].items())
        if not files:
            return

        seed = fingerprint['total_lines']
        random.seed(seed)

        # Add rotating elements around top 3 files
        for idx, (file_path, file_data) in enumerate(files[:3]):
            golden_angle = 137.508
            angle = (idx * golden_angle) * (math.pi / 180)
            radius = 60 + idx * (min(self.width, self.height) / (2.2 * len(files)))

            cx, cy = self.width / 2, self.height / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            hash_val = int(file_data['hash'][:8], 16)
            rotation_offset = (hash_val % 360) * (math.pi / 180)

            # Create rotating pattern
            orbit_radius = 40 + idx * 15
            num_elements = 6 + (hash_val % 5)

            elements = OrganicShapes.rotating_pattern((x, y), orbit_radius, num_elements, rotation_offset, (4, 10))

            color = colors[hash_val % len(colors)]

            for ex, ey, esize, eangle in elements:
                draw.ellipse(
                    [ex - esize, ey - esize, ex + esize, ey + esize],
                    fill=color + (120,)
                )

    def _add_waves_with_fade(self, draw, fingerprint, colors):
        """Add wave patterns with directional color fading"""
        seed = fingerprint['total_lines']
        random.seed(seed)

        num_waves = 6 + (fingerprint['commit_count'] % 6)

        for i in range(num_waves):
            y_base = random.randint(int(self.height * 0.15), int(self.height * 0.85))
            amplitude = random.randint(20, 40)
            frequency = random.uniform(2.0, 3.5)
            phase = random.uniform(0, 2 * math.pi)

            points = OrganicShapes.wave_pattern(
                y_base, self.width, amplitude, frequency, phase
            )

            base_color = colors[i % len(colors)]
            r, g, b = base_color
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

            # Draw wave with fading color and opacity from left to right
            for j in range(len(points) - 1):
                # Fade ratio based on position
                fade_ratio = j / len(points)

                # Gradually shift hue across the wave
                wave_h = (h + fade_ratio * 0.1) % 1.0
                wave_v = v * (1 - fade_ratio * 0.3)  # Darker towards right
                wave_s = s * (1 - fade_ratio * 0.2)  # Less saturated towards right

                wave_color = self._hsv_to_rgb(wave_h, wave_s, wave_v)

                # Fade opacity
                opacity = int(80 * (1 - fade_ratio * 0.5))

                # Vary thickness
                thickness = max(2, int(5 * (1 - fade_ratio * 0.4)))

                draw.line([points[j], points[j+1]],
                         fill=wave_color + (opacity,),
                         width=thickness)


def main():
    """Main function"""
    import argparse
    import re
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description='Generate harmonious generative art from a git repository'
    )
    parser.add_argument('--repo', default='.', help='Path to git repository')
    parser.add_argument('--output', default=None, help='Output image path (auto-generated if not specified)')
    parser.add_argument('--size', type=int, default=1600, help='Canvas width in pixels')
    parser.add_argument('--aspect', default='auto',
                       choices=['auto'] + list(GitArtGenerator.ASPECT_RATIOS.keys()),
                       help='Canvas aspect ratio (default: auto - detects based on repo type)')
    parser.add_argument('--contrast', default='high',
                       choices=['low', 'medium', 'high'],
                       help='Color contrast level: low (subtle), medium (balanced), high (dramatic). Default: high')

    args = parser.parse_args()

    # Smart filename generation
    if args.output is None:
        # Get repo name from path
        repo = git.Repo(args.repo)
        repo_name = Path(args.repo).resolve().name

        # Sanitize repo name for filename
        sanitized_name = re.sub(r'[^\w\-]', '_', repo_name)

        # Get commit hash (short)
        try:
            commit_hash = repo.head.commit.hexsha[:7]
        except:
            commit_hash = "nocommit"

        # Get timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Calculate actual dimensions
        generator_temp = GitArtGenerator(args.repo, width=args.size, aspect_ratio=args.aspect, contrast=args.contrast)
        width = generator_temp.width
        height = generator_temp.height

        # Build filename with timestamp for uniqueness
        # Format: RepoName_WIDTHxHEIGHT_TIMESTAMP_commithash.png
        args.output = f"{sanitized_name}_{width}x{height}_{timestamp}_{commit_hash}.png"
        print(f"📝 Auto-generated filename: {args.output}")

    generator = GitArtGenerator(args.repo, width=args.size, aspect_ratio=args.aspect, contrast=args.contrast)
    generator.generate_art(args.output)


if __name__ == '__main__':
    main()
