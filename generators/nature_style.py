"""Nature art style - organic shapes inspired by nature.

This style transforms repositories into nature scenes where:
- Background: Earth tones (browns, greens) with organic shapes (leaves, trees, grass)
- Foreground: Colorful elements based on code types (flowers, insects)
- Colors: Natural earth tones for background, vibrant repo-based colors for foreground
- Composition: Layered like a natural ecosystem
"""

from .base import BaseArtGenerator
from PIL import Image, ImageDraw, ImageFilter
import colorsys
import math
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

    @staticmethod
    def choice(hash_string, index, choices):
        """Deterministic choice from list."""
        rand_val = DeterministicRandom.from_hash(hash_string, index)
        idx = int(rand_val * len(choices))
        return choices[min(idx, len(choices) - 1)]


class EarthPalette:
    """Earth-toned color palettes for natural backgrounds."""

    EARTH_COLORS = {
        'soil': [(101, 67, 33), (123, 63, 0), (139, 90, 43), (160, 82, 45)],
        'grass': [(34, 139, 34), (46, 125, 50), (56, 142, 60), (85, 107, 47)],
        'forest': [(0, 100, 0), (34, 139, 34), (46, 125, 50), (27, 94, 32)],
        'bark': [(101, 67, 33), (85, 53, 22), (79, 64, 43), (92, 64, 51)],
        'moss': [(138, 154, 91), (85, 107, 47), (107, 142, 35), (124, 138, 90)],
        'stone': [(112, 128, 144), (119, 136, 153), (128, 128, 128), (105, 105, 105)]
    }

    @staticmethod
    def get_earth_palette():
        """Get combined earth tone palette for backgrounds."""
        all_earth_tones = []
        for colors in EarthPalette.EARTH_COLORS.values():
            all_earth_tones.extend(colors)
        return all_earth_tones


class RepositoryPalette:
    """Vibrant color palettes based on repository type."""

    PALETTES = {
        'python': [(52, 152, 219), (41, 128, 185), (26, 188, 156)],
        'javascript': [(241, 196, 15), (230, 126, 34), (255, 193, 7)],
        'php': [(142, 68, 173), (155, 89, 182), (187, 143, 206)],
        'java': [(231, 76, 60), (244, 67, 54), (211, 47, 47)],
        'ruby': [(220, 20, 60), (255, 99, 71), (233, 30, 99)],
        'systems': [(0, 173, 181), (0, 188, 212), (0, 150, 136)],
        'data': [(46, 204, 113), (76, 175, 80), (139, 195, 74)],
        'cpp': [(96, 125, 139), (84, 110, 122), (69, 90, 100)],
        'mobile': [(255, 107, 107), (255, 138, 101), (255, 167, 38)],
        'frontend': [(46, 204, 113), (52, 152, 219), (155, 89, 182)]
    }

    @staticmethod
    def select_palette_by_repo(fingerprint):
        """Select vibrant color palette based on repository language."""
        file_types = fingerprint['file_types']
        total_lines = fingerprint['total_lines']

        py_lines = file_types.get('.py', 0)
        js_lines = sum(file_types.get(ext, 0) for ext in ['.js', '.jsx', '.ts', '.tsx'])
        php_lines = file_types.get('.php', 0)
        java_lines = file_types.get('.java', 0)
        rb_lines = file_types.get('.rb', 0)
        cpp_lines = sum(file_types.get(ext, 0) for ext in ['.c', '.cpp', '.h', '.hpp'])
        mobile_lines = sum(file_types.get(ext, 0) for ext in ['.swift', '.kt', '.dart'])
        html_css_lines = sum(file_types.get(ext, 0) for ext in ['.html', '.css', '.scss'])

        threshold = total_lines * 0.3

        if py_lines > threshold:
            return 'python', RepositoryPalette.PALETTES['python']
        elif js_lines > threshold:
            return 'javascript', RepositoryPalette.PALETTES['javascript']
        elif php_lines > threshold:
            return 'php', RepositoryPalette.PALETTES['php']
        elif java_lines > threshold:
            return 'java', RepositoryPalette.PALETTES['java']
        elif rb_lines > threshold:
            return 'ruby', RepositoryPalette.PALETTES['ruby']
        elif cpp_lines > threshold:
            return 'cpp', RepositoryPalette.PALETTES['cpp']
        elif mobile_lines > threshold:
            return 'mobile', RepositoryPalette.PALETTES['mobile']
        elif html_css_lines > threshold:
            return 'frontend', RepositoryPalette.PALETTES['frontend']
        else:
            return 'data', RepositoryPalette.PALETTES['data']


class NatureShapes:
    """Generate nature-inspired organic shapes."""

    @staticmethod
    def draw_leaf(draw, x, y, size, color, seed_hash, opacity=120):
        """Draw an organic leaf shape."""
        rotation = DeterministicRandom.uniform(seed_hash, 0, 0, math.pi * 2)

        points = []
        segments = 20
        for i in range(segments):
            t = i / segments
            angle = t * math.pi - math.pi / 2

            radius = size * math.sin(t * math.pi) * 0.5
            local_x = math.cos(angle) * radius
            local_y = math.sin(angle) * size * 0.5

            px = x + local_x * math.cos(rotation) - local_y * math.sin(rotation)
            py = y + local_x * math.sin(rotation) + local_y * math.cos(rotation)
            points.append((px, py))

        if len(points) > 2:
            draw.polygon(points, fill=color + (opacity,))

    @staticmethod
    def draw_tree(draw, x, y, height, width, colors, seed_hash):
        """Draw a stylized tree with varied trunk and branch structures."""
        bark_brown = (101, 67, 33)
        dark_bark = (85, 53, 22)
        trunk_color = bark_brown if DeterministicRandom.from_hash(seed_hash, 0) > 0.5 else dark_bark

        tree_style = DeterministicRandom.randint(seed_hash, 1, 0, 3)

        if tree_style == 0:
            NatureShapes._draw_wide_tree(draw, x, y, height, width, trunk_color, colors, seed_hash)
        elif tree_style == 1:
            NatureShapes._draw_tall_tree(draw, x, y, height, width, trunk_color, colors, seed_hash)
        elif tree_style == 2:
            NatureShapes._draw_branching_tree(draw, x, y, height, width, trunk_color, colors, seed_hash)
        else:
            NatureShapes._draw_bushy_tree(draw, x, y, height, width, trunk_color, colors, seed_hash)

    @staticmethod
    def _draw_wide_tree(draw, x, y, height, width, trunk_color, foliage_colors, seed_hash):
        """Wide tree with spreading branches."""
        trunk_width = width * 0.15
        draw.line([(x, y), (x, y - height * 0.3)], fill=trunk_color + (180,), width=int(trunk_width))

        num_branches = DeterministicRandom.randint(seed_hash, 100, 4, 7)
        for i in range(num_branches):
            branch_hash = f"{seed_hash}_wb_{i}"
            start_y = y - height * DeterministicRandom.uniform(branch_hash, 0, 0.15, 0.35)
            end_x = x + DeterministicRandom.uniform(branch_hash, 1, -width * 0.4, width * 0.4)
            end_y = y - height * DeterministicRandom.uniform(branch_hash, 2, 0.3, 0.6)
            branch_width = int(trunk_width * DeterministicRandom.uniform(branch_hash, 3, 0.4, 0.7))

            draw.line([(x, start_y), (end_x, end_y)], fill=trunk_color + (180,), width=branch_width)

            foliage_size = DeterministicRandom.uniform(branch_hash, 4, width * 0.3, width * 0.5)
            color_idx = DeterministicRandom.randint(branch_hash, 5, 0, len(foliage_colors) - 1)
            color = foliage_colors[color_idx]
            draw.ellipse(
                [end_x - foliage_size/2, end_y - foliage_size/2,
                 end_x + foliage_size/2, end_y + foliage_size/2],
                fill=color + (150,)
            )

    @staticmethod
    def _draw_tall_tree(draw, x, y, height, width, trunk_color, foliage_colors, seed_hash):
        """Tall tree with upward branches."""
        trunk_width = width * 0.12
        trunk_height = height * 0.5
        draw.line([(x, y), (x, y - trunk_height)], fill=trunk_color + (180,), width=int(trunk_width))

        num_branches = DeterministicRandom.randint(seed_hash, 200, 5, 9)
        for i in range(num_branches):
            branch_hash = f"{seed_hash}_tb_{i}"
            start_y = y - trunk_height * DeterministicRandom.uniform(branch_hash, 0, 0.4, 1.0)
            angle = DeterministicRandom.uniform(branch_hash, 1, -0.6, 0.6)
            branch_length = height * DeterministicRandom.uniform(branch_hash, 2, 0.15, 0.3)
            end_x = x + math.sin(angle) * branch_length
            end_y = start_y - math.cos(angle) * branch_length
            branch_width = int(trunk_width * DeterministicRandom.uniform(branch_hash, 3, 0.3, 0.6))

            draw.line([(x, start_y), (end_x, end_y)], fill=trunk_color + (180,), width=branch_width)

            foliage_size = DeterministicRandom.uniform(branch_hash, 4, width * 0.25, width * 0.4)
            color_idx = DeterministicRandom.randint(branch_hash, 5, 0, len(foliage_colors) - 1)
            color = foliage_colors[color_idx]
            draw.ellipse(
                [end_x - foliage_size/2, end_y - foliage_size/2,
                 end_x + foliage_size/2, end_y + foliage_size/2],
                fill=color + (150,)
            )

    @staticmethod
    def _draw_branching_tree(draw, x, y, height, width, trunk_color, foliage_colors, seed_hash):
        """Tree with complex branching structure."""
        trunk_width = width * 0.13

        main_branches = DeterministicRandom.randint(seed_hash, 300, 2, 4)
        for mb in range(main_branches):
            mb_hash = f"{seed_hash}_mb_{mb}"
            base_angle = DeterministicRandom.uniform(mb_hash, 0, -1.2, 1.2)
            branch_x = x + math.sin(base_angle) * width * 0.2
            branch_y = y - height * DeterministicRandom.uniform(mb_hash, 1, 0.2, 0.4)

            draw.line([(x, y), (branch_x, branch_y)], fill=trunk_color + (180,), width=int(trunk_width))

            sub_branches = DeterministicRandom.randint(mb_hash, 2, 2, 4)
            for sb in range(sub_branches):
                sb_hash = f"{mb_hash}_sb_{sb}"
                sub_angle = base_angle + DeterministicRandom.uniform(sb_hash, 0, -0.5, 0.5)
                sub_length = height * DeterministicRandom.uniform(sb_hash, 1, 0.15, 0.25)
                end_x = branch_x + math.sin(sub_angle) * sub_length
                end_y = branch_y - math.cos(sub_angle) * sub_length
                sub_width = int(trunk_width * DeterministicRandom.uniform(sb_hash, 2, 0.4, 0.6))

                draw.line([(branch_x, branch_y), (end_x, end_y)], fill=trunk_color + (180,), width=sub_width)

                foliage_size = DeterministicRandom.uniform(sb_hash, 3, width * 0.2, width * 0.35)
                color_idx = DeterministicRandom.randint(sb_hash, 4, 0, len(foliage_colors) - 1)
                color = foliage_colors[color_idx]
                draw.ellipse(
                    [end_x - foliage_size/2, end_y - foliage_size/2,
                     end_x + foliage_size/2, end_y + foliage_size/2],
                    fill=color + (150,)
                )

    @staticmethod
    def _draw_bushy_tree(draw, x, y, height, width, trunk_color, foliage_colors, seed_hash):
        """Short bushy tree with many small branches."""
        trunk_width = width * 0.14
        trunk_height = height * 0.25
        draw.line([(x, y), (x, y - trunk_height)], fill=trunk_color + (180,), width=int(trunk_width))

        num_branches = DeterministicRandom.randint(seed_hash, 400, 6, 12)
        for i in range(num_branches):
            branch_hash = f"{seed_hash}_bb_{i}"
            start_y = y - trunk_height * DeterministicRandom.uniform(branch_hash, 0, 0.5, 1.0)
            angle = DeterministicRandom.uniform(branch_hash, 1, 0, math.pi * 2)
            branch_length = height * DeterministicRandom.uniform(branch_hash, 2, 0.1, 0.25)
            end_x = x + math.cos(angle) * branch_length
            end_y = start_y - abs(math.sin(angle)) * branch_length
            branch_width = int(trunk_width * DeterministicRandom.uniform(branch_hash, 3, 0.25, 0.5))

            draw.line([(x, start_y), (end_x, end_y)], fill=trunk_color + (180,), width=branch_width)

            foliage_size = DeterministicRandom.uniform(branch_hash, 4, width * 0.2, width * 0.3)
            color_idx = DeterministicRandom.randint(branch_hash, 5, 0, len(foliage_colors) - 1)
            color = foliage_colors[color_idx]
            draw.ellipse(
                [end_x - foliage_size/2, end_y - foliage_size/2,
                 end_x + foliage_size/2, end_y + foliage_size/2],
                fill=color + (150,)
            )

    @staticmethod
    def draw_grass_blade(draw, x, y, height, width, color, seed_hash):
        """Draw a single grass blade as a curved line."""
        curvature = DeterministicRandom.uniform(seed_hash, 0, -height * 0.3, height * 0.3)

        points = []
        segments = 10
        for i in range(segments + 1):
            t = i / segments
            curve_x = x + curvature * math.sin(t * math.pi)
            curve_y = y - t * height
            points.append((curve_x, curve_y))

        for i in range(len(points) - 1):
            thickness = int(width * (1 - i / len(points)))
            draw.line([points[i], points[i + 1]], fill=color + (150,), width=max(1, thickness))

    @staticmethod
    def draw_flower(draw, x, y, size, petal_color, center_color, seed_hash):
        """Draw an abstract expressive flower."""
        flower_style = DeterministicRandom.randint(seed_hash, 0, 0, 3)

        if flower_style == 0:
            NatureShapes._draw_splatter_flower(draw, x, y, size, petal_color, center_color, seed_hash)
        elif flower_style == 1:
            NatureShapes._draw_geometric_flower(draw, x, y, size, petal_color, center_color, seed_hash)
        elif flower_style == 2:
            NatureShapes._draw_spiral_flower(draw, x, y, size, petal_color, center_color, seed_hash)
        else:
            NatureShapes._draw_blob_flower(draw, x, y, size, petal_color, center_color, seed_hash)

    @staticmethod
    def _draw_splatter_flower(draw, x, y, size, petal_color, center_color, seed_hash):
        """Splatter/explosion style abstract flower."""
        num_splatters = DeterministicRandom.randint(seed_hash, 100, 8, 15)

        for i in range(num_splatters):
            splat_hash = f"{seed_hash}_splat_{i}"
            angle = DeterministicRandom.uniform(splat_hash, 0, 0, math.pi * 2)
            distance = DeterministicRandom.uniform(splat_hash, 1, size * 0.2, size * 0.6)
            splat_x = x + math.cos(angle) * distance
            splat_y = y + math.sin(angle) * distance
            splat_size = DeterministicRandom.uniform(splat_hash, 2, size * 0.15, size * 0.35)

            points = []
            num_points = DeterministicRandom.randint(splat_hash, 3, 4, 7)
            for p in range(num_points):
                p_angle = (p / num_points) * 2 * math.pi
                variation = DeterministicRandom.uniform(splat_hash, 10 + p, 0.5, 1.5)
                px = splat_x + math.cos(p_angle) * splat_size * variation
                py = splat_y + math.sin(p_angle) * splat_size * variation
                points.append((px, py))

            opacity = DeterministicRandom.randint(splat_hash, 4, 150, 220)
            if len(points) > 2:
                draw.polygon(points, fill=petal_color + (opacity,))

        center_size = size * 0.3
        draw.ellipse(
            [x - center_size/2, y - center_size/2, x + center_size/2, y + center_size/2],
            fill=center_color + (240,)
        )

    @staticmethod
    def _draw_geometric_flower(draw, x, y, size, petal_color, center_color, seed_hash):
        """Angular geometric abstract flower."""
        num_petals = DeterministicRandom.randint(seed_hash, 200, 5, 9)
        rotation = DeterministicRandom.uniform(seed_hash, 201, 0, math.pi)

        for i in range(num_petals):
            petal_hash = f"{seed_hash}_geo_{i}"
            angle = (i / num_petals) * 2 * math.pi + rotation
            petal_length = DeterministicRandom.uniform(petal_hash, 0, size * 0.4, size * 0.7)
            petal_width = DeterministicRandom.uniform(petal_hash, 1, size * 0.15, size * 0.3)

            angle_offset = DeterministicRandom.uniform(petal_hash, 2, -0.3, 0.3)
            end_x = x + math.cos(angle + angle_offset) * petal_length
            end_y = y + math.sin(angle + angle_offset) * petal_length

            perp_x = -math.sin(angle)
            perp_y = math.cos(angle)

            points = [
                (x, y),
                (x + perp_x * petal_width/2, y + perp_y * petal_width/2),
                (end_x, end_y),
                (x - perp_x * petal_width/2, y - perp_y * petal_width/2)
            ]

            opacity = DeterministicRandom.randint(petal_hash, 3, 160, 210)
            draw.polygon(points, fill=petal_color + (opacity,))

        center_points = []
        num_center_points = DeterministicRandom.randint(seed_hash, 300, 6, 10)
        for p in range(num_center_points):
            angle = (p / num_center_points) * 2 * math.pi
            variation = DeterministicRandom.uniform(seed_hash, 400 + p, 0.8, 1.2)
            center_size = size * 0.25 * variation
            px = x + math.cos(angle) * center_size
            py = y + math.sin(angle) * center_size
            center_points.append((px, py))

        if len(center_points) > 2:
            draw.polygon(center_points, fill=center_color + (230,))

    @staticmethod
    def _draw_spiral_flower(draw, x, y, size, petal_color, center_color, seed_hash):
        """Spiral/swirl abstract flower."""
        num_petals = DeterministicRandom.randint(seed_hash, 500, 6, 10)

        for i in range(num_petals):
            petal_hash = f"{seed_hash}_spiral_{i}"
            t = i / num_petals
            angle = t * math.pi * 4 + DeterministicRandom.uniform(petal_hash, 0, 0, 0.5)
            distance = size * t * 0.5

            petal_x = x + math.cos(angle) * distance
            petal_y = y + math.sin(angle) * distance
            petal_size = DeterministicRandom.uniform(petal_hash, 1, size * 0.2, size * 0.4)

            points = []
            segments = 8
            for s in range(segments):
                s_angle = (s / segments) * 2 * math.pi
                stretch = DeterministicRandom.uniform(petal_hash, 10 + s, 0.6, 1.4)
                px = petal_x + math.cos(s_angle) * petal_size * stretch
                py = petal_y + math.sin(s_angle) * petal_size * stretch
                points.append((px, py))

            opacity = DeterministicRandom.randint(petal_hash, 2, 140, 200)
            if len(points) > 2:
                draw.polygon(points, fill=petal_color + (opacity,))

        for layer in range(3):
            layer_hash = f"{seed_hash}_center_{layer}"
            center_size = size * (0.3 - layer * 0.08)
            num_points = 8
            points = []
            for p in range(num_points):
                angle = (p / num_points) * 2 * math.pi
                var = DeterministicRandom.uniform(layer_hash, p, 0.7, 1.3)
                px = x + math.cos(angle) * center_size * var
                py = y + math.sin(angle) * center_size * var
                points.append((px, py))

            opacity = 240 - layer * 30
            if len(points) > 2:
                draw.polygon(points, fill=center_color + (opacity,))

    @staticmethod
    def _draw_blob_flower(draw, x, y, size, petal_color, center_color, seed_hash):
        """Organic blob-based abstract flower."""
        num_blobs = DeterministicRandom.randint(seed_hash, 600, 6, 12)

        for i in range(num_blobs):
            blob_hash = f"{seed_hash}_blob_{i}"
            angle = (i / num_blobs) * 2 * math.pi + DeterministicRandom.uniform(blob_hash, 0, -0.2, 0.2)
            distance = DeterministicRandom.uniform(blob_hash, 1, size * 0.25, size * 0.55)
            blob_x = x + math.cos(angle) * distance
            blob_y = y + math.sin(angle) * distance

            blob_size = DeterministicRandom.uniform(blob_hash, 2, size * 0.25, size * 0.45)

            points = []
            num_points = DeterministicRandom.randint(blob_hash, 3, 8, 15)
            for p in range(num_points):
                p_angle = (p / num_points) * 2 * math.pi
                wave = math.sin(p_angle * 3) * 0.3
                variation = DeterministicRandom.uniform(blob_hash, 20 + p, 0.6 + wave, 1.4 + wave)
                px = blob_x + math.cos(p_angle) * blob_size * variation
                py = blob_y + math.sin(p_angle) * blob_size * variation
                points.append((px, py))

            opacity = DeterministicRandom.randint(blob_hash, 4, 150, 210)
            if len(points) > 2:
                draw.polygon(points, fill=petal_color + (opacity,))

        num_center_blobs = DeterministicRandom.randint(seed_hash, 700, 3, 6)
        for cb in range(num_center_blobs):
            cb_hash = f"{seed_hash}_cb_{cb}"
            offset_x = DeterministicRandom.uniform(cb_hash, 0, -size * 0.15, size * 0.15)
            offset_y = DeterministicRandom.uniform(cb_hash, 1, -size * 0.15, size * 0.15)
            blob_size = DeterministicRandom.uniform(cb_hash, 2, size * 0.15, size * 0.25)
            opacity = DeterministicRandom.randint(cb_hash, 3, 200, 240)

            draw.ellipse(
                [x + offset_x - blob_size/2, y + offset_y - blob_size/2,
                 x + offset_x + blob_size/2, y + offset_y + blob_size/2],
                fill=center_color + (opacity,)
            )

    @staticmethod
    def draw_butterfly(draw, x, y, size, wing_color, seed_hash):
        """Draw a stylized butterfly."""
        wing_span = size
        wing_height = size * 0.6

        left_wing = [
            (x, y),
            (x - wing_span / 2, y - wing_height / 2),
            (x - wing_span / 2, y + wing_height / 2)
        ]
        draw.polygon(left_wing, fill=wing_color + (180,))

        right_wing = [
            (x, y),
            (x + wing_span / 2, y - wing_height / 2),
            (x + wing_span / 2, y + wing_height / 2)
        ]
        draw.polygon(right_wing, fill=wing_color + (180,))

        body_length = size * 0.4
        draw.line([(x, y - body_length / 2), (x, y + body_length / 2)],
                 fill=(50, 50, 50, 200), width=max(2, int(size * 0.08)))

    @staticmethod
    def draw_bee(draw, x, y, size, seed_hash):
        """Draw a stylized bee."""
        body_color = (255, 193, 7)
        stripe_color = (66, 66, 66)

        body_width = size * 0.4
        body_height = size * 0.6
        draw.ellipse(
            [x - body_width / 2, y - body_height / 2,
             x + body_width / 2, y + body_height / 2],
            fill=body_color + (200,)
        )

        stripe_thickness = body_height * 0.15
        for i in range(3):
            stripe_y = y - body_height / 2 + (i + 1) * body_height / 4
            draw.line(
                [(x - body_width / 2, stripe_y), (x + body_width / 2, stripe_y)],
                fill=stripe_color + (200,), width=int(stripe_thickness)
            )

        wing_size = size * 0.3
        for offset in [-1, 1]:
            wing_x = x + offset * body_width * 0.3
            wing_y = y - body_height * 0.2
            draw.ellipse(
                [wing_x - wing_size / 2, wing_y - wing_size / 2,
                 wing_x + wing_size / 2, wing_y + wing_size / 2],
                fill=(200, 200, 255, 120)
            )


class NatureStyleGenerator(BaseArtGenerator):
    """Nature-inspired art style with organic shapes."""

    STYLE_NAME = "nature"
    STYLE_DESCRIPTION = "Nature-inspired art with earth-toned backgrounds and colorful organic elements"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize nature style generator."""
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

    def generate_art(self, output_path='repo_art.png'):
        """Generate nature-inspired artwork."""
        fingerprint = self.get_repo_fingerprint()
        earth_colors = EarthPalette.get_earth_palette()
        palette_name, vibrant_colors = RepositoryPalette.select_palette_by_repo(fingerprint)

        img = self._create_background(fingerprint, earth_colors)
        draw = ImageDraw.Draw(img, 'RGBA')

        self._add_expressive_brushstrokes(draw, fingerprint, earth_colors)

        self._add_background_nature(draw, fingerprint, earth_colors)

        self._add_abstract_foliage(draw, fingerprint, earth_colors, vibrant_colors)

        self._add_foreground_nature(draw, fingerprint, vibrant_colors)

        self._add_expressive_overlays(draw, fingerprint, vibrant_colors)

        img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

        img.save(output_path, quality=95)

        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files, "
              f"{fingerprint['total_lines']} lines, "
              f"{fingerprint['commit_count']} commits")
        print(f"Palette: '{palette_name}' (nature-inspired with earth tones)")

        return output_path

    def _create_background(self, fingerprint, earth_colors):
        """Create dense forest background with rich earth tones."""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img, 'RGBA')

        seed_hash = str(fingerprint['total_lines'])

        forest_green = (34, 70, 34)
        dark_forest = (20, 45, 20)

        pixels = img.load()
        for y in range(self.height):
            ratio = y / self.height
            r = int(forest_green[0] * (1 - ratio) + dark_forest[0] * ratio)
            g = int(forest_green[1] * (1 - ratio) + dark_forest[1] * ratio)
            b = int(forest_green[2] * (1 - ratio) + dark_forest[2] * ratio)

            for x in range(self.width):
                pixels[x, y] = (r, g, b)

        num_bg_trees = DeterministicRandom.randint(seed_hash, 5000, 30, 60)
        for i in range(num_bg_trees):
            tree_hash = f"{seed_hash}_bgtree_{i}"
            x = DeterministicRandom.uniform(tree_hash, 0, 0, self.width)
            y = DeterministicRandom.uniform(tree_hash, 1, 0, self.height)
            size = DeterministicRandom.uniform(tree_hash, 2, 40, 150)

            color_idx = DeterministicRandom.randint(tree_hash, 3, 0, len(earth_colors) - 1)
            color = earth_colors[color_idx]

            darker_color = (
                max(0, int(color[0] * 0.5)),
                max(0, int(color[1] * 0.5)),
                max(0, int(color[2] * 0.5))
            )

            opacity = DeterministicRandom.randint(tree_hash, 4, 100, 180)
            draw.ellipse(
                [x - size/2, y - size/2, x + size/2, y + size/2],
                fill=darker_color + (opacity,)
            )

        return img

    def _add_background_nature(self, draw, fingerprint, earth_colors):
        """Add background nature elements (trees, grass, leaves)."""
        seed_hash = str(fingerprint['total_lines'])

        foliage_colors = [(34, 139, 34), (46, 125, 50), (56, 142, 60), (85, 107, 47), (107, 142, 35)]

        num_trees = DeterministicRandom.randint(seed_hash, 100, 8, 15)
        for i in range(num_trees):
            tree_hash = f"{seed_hash}_tree_{i}"
            x = DeterministicRandom.uniform(tree_hash, 0, self.width * 0.05, self.width * 0.95)
            y = DeterministicRandom.uniform(tree_hash, 1, self.height * 0.4, self.height * 0.95)
            height = DeterministicRandom.uniform(tree_hash, 2, self.height * 0.25, self.height * 0.5)
            width = DeterministicRandom.uniform(tree_hash, 3, self.width * 0.10, self.width * 0.20)

            NatureShapes.draw_tree(draw, x, y, height, width, foliage_colors, tree_hash)

        num_grass = DeterministicRandom.randint(seed_hash, 200, 50, 100)
        for i in range(num_grass):
            grass_hash = f"{seed_hash}_grass_{i}"
            x = DeterministicRandom.uniform(grass_hash, 0, 0, self.width)
            y = DeterministicRandom.uniform(grass_hash, 1, self.height * 0.7, self.height)
            height = DeterministicRandom.uniform(grass_hash, 2, 40, 100)
            width = DeterministicRandom.randint(grass_hash, 3, 3, 6)

            grass_green = (85, 107, 47)
            bright_grass = (107, 142, 35)
            color = grass_green if i % 2 == 0 else bright_grass

            NatureShapes.draw_grass_blade(draw, x, y, height, width, color, grass_hash)

        num_leaves = DeterministicRandom.randint(seed_hash, 300, 30, 60)
        for i in range(num_leaves):
            leaf_hash = f"{seed_hash}_leaf_{i}"
            x = DeterministicRandom.uniform(leaf_hash, 0, 0, self.width)
            y = DeterministicRandom.uniform(leaf_hash, 1, 0, self.height * 0.8)
            size = DeterministicRandom.uniform(leaf_hash, 2, 25, 60)

            leaf_colors = [(34, 139, 34), (46, 125, 50), (56, 142, 60), (85, 107, 47)]
            color = leaf_colors[DeterministicRandom.randint(leaf_hash, 3, 0, len(leaf_colors) - 1)]

            NatureShapes.draw_leaf(draw, x, y, size, color, leaf_hash, opacity=140)

    def _add_foreground_nature(self, draw, fingerprint, vibrant_colors):
        """Add colorful foreground elements (flowers, insects) based on repo files."""
        files = sorted(fingerprint['files'].items(), key=lambda x: x[1]['lines'], reverse=True)

        total_files = len(files)
        if total_files > 100:
            max_elements = 50
        elif total_files > 50:
            max_elements = 40
        elif total_files > 20:
            max_elements = min(30, total_files)
        else:
            max_elements = total_files

        files_to_draw = files[:max_elements]

        for idx, (file_path, file_data) in enumerate(files_to_draw):
            file_hash = file_data['hash']

            x = DeterministicRandom.uniform(file_hash, 0, self.width * 0.10, self.width * 0.90)
            y = DeterministicRandom.uniform(file_hash, 1, self.height * 0.15, self.height * 0.75)

            normalized_size = min(1.0, file_data['lines'] / 400.0)
            size = 35 + normalized_size * 70

            color_idx = int(file_hash[:8], 16) % len(vibrant_colors)
            petal_color = vibrant_colors[color_idx]
            center_color = vibrant_colors[(color_idx + 1) % len(vibrant_colors)]

            element_type = DeterministicRandom.randint(file_hash, 2, 0, 2)

            if element_type == 0:
                NatureShapes.draw_flower(draw, x, y, size, petal_color, center_color, file_hash)
            elif element_type == 1:
                NatureShapes.draw_butterfly(draw, x, y, size * 0.7, petal_color, file_hash)
            else:
                NatureShapes.draw_bee(draw, x, y, size * 0.6, file_hash)

    def _add_expressive_brushstrokes(self, draw, fingerprint, earth_colors):
        """Add expressive brushstroke-like elements."""
        seed_hash = str(fingerprint['total_lines'])

        num_strokes = DeterministicRandom.randint(seed_hash, 6000, 15, 30)
        for i in range(num_strokes):
            stroke_hash = f"{seed_hash}_stroke_{i}"
            x1 = DeterministicRandom.uniform(stroke_hash, 0, 0, self.width)
            y1 = DeterministicRandom.uniform(stroke_hash, 1, 0, self.height)

            angle = DeterministicRandom.uniform(stroke_hash, 2, 0, math.pi * 2)
            length = DeterministicRandom.uniform(stroke_hash, 3, 50, 200)
            x2 = x1 + math.cos(angle) * length
            y2 = y1 + math.sin(angle) * length

            color_idx = DeterministicRandom.randint(stroke_hash, 4, 0, len(earth_colors) - 1)
            color = earth_colors[color_idx]

            darker = (int(color[0] * 0.6), int(color[1] * 0.6), int(color[2] * 0.6))

            width = DeterministicRandom.randint(stroke_hash, 5, 3, 15)
            opacity = DeterministicRandom.randint(stroke_hash, 6, 40, 100)

            draw.line([(x1, y1), (x2, y2)], fill=darker + (opacity,), width=width)

    def _add_abstract_foliage(self, draw, fingerprint, earth_colors, vibrant_colors):
        """Add abstract foliage shapes."""
        seed_hash = str(fingerprint['total_lines'])

        num_shapes = DeterministicRandom.randint(seed_hash, 7000, 10, 25)
        for i in range(num_shapes):
            shape_hash = f"{seed_hash}_foliage_{i}"
            x = DeterministicRandom.uniform(shape_hash, 0, 0, self.width)
            y = DeterministicRandom.uniform(shape_hash, 1, 0, self.height * 0.7)
            size = DeterministicRandom.uniform(shape_hash, 2, 40, 120)

            use_vibrant = DeterministicRandom.from_hash(shape_hash, 3) > 0.7
            if use_vibrant:
                color = vibrant_colors[DeterministicRandom.randint(shape_hash, 4, 0, len(vibrant_colors) - 1)]
            else:
                green_shades = [(46, 125, 50), (56, 142, 60), (76, 175, 80), (139, 195, 74)]
                color = green_shades[DeterministicRandom.randint(shape_hash, 4, 0, len(green_shades) - 1)]

            shape_type = DeterministicRandom.randint(shape_hash, 5, 0, 2)

            if shape_type == 0:
                points = []
                num_points = DeterministicRandom.randint(shape_hash, 6, 5, 10)
                for p in range(num_points):
                    angle = (p / num_points) * 2 * math.pi
                    r_var = DeterministicRandom.uniform(shape_hash, 100 + p, 0.5, 1.5)
                    px = x + math.cos(angle) * size * r_var
                    py = y + math.sin(angle) * size * r_var
                    points.append((px, py))

                opacity = DeterministicRandom.randint(shape_hash, 7, 60, 130)
                if len(points) > 2:
                    draw.polygon(points, fill=color + (opacity,))
            else:
                rotation = DeterministicRandom.uniform(shape_hash, 8, 0, math.pi)
                width_var = DeterministicRandom.uniform(shape_hash, 9, 0.5, 1.5)
                points = []
                for t in range(20):
                    angle = (t / 20) * math.pi - math.pi / 2
                    radius = size * math.sin((t / 20) * math.pi) * 0.5
                    local_x = math.cos(angle) * radius * width_var
                    local_y = math.sin(angle) * size * 0.5
                    px = x + local_x * math.cos(rotation) - local_y * math.sin(rotation)
                    py = y + local_x * math.sin(rotation) + local_y * math.cos(rotation)
                    points.append((px, py))

                opacity = DeterministicRandom.randint(shape_hash, 10, 80, 150)
                if len(points) > 2:
                    draw.polygon(points, fill=color + (opacity,))

    def _add_expressive_overlays(self, draw, fingerprint, vibrant_colors):
        """Add expressive color overlays and abstract elements."""
        seed_hash = str(fingerprint['total_lines'])

        num_splashes = DeterministicRandom.randint(seed_hash, 8000, 8, 15)
        for i in range(num_splashes):
            splash_hash = f"{seed_hash}_splash_{i}"
            x = DeterministicRandom.uniform(splash_hash, 0, 0, self.width)
            y = DeterministicRandom.uniform(splash_hash, 1, 0, self.height)

            color = vibrant_colors[DeterministicRandom.randint(splash_hash, 2, 0, len(vibrant_colors) - 1)]

            num_blobs = DeterministicRandom.randint(splash_hash, 3, 3, 8)
            for b in range(num_blobs):
                blob_hash = f"{splash_hash}_blob_{b}"
                offset_x = DeterministicRandom.uniform(blob_hash, 0, -60, 60)
                offset_y = DeterministicRandom.uniform(blob_hash, 1, -60, 60)
                size = DeterministicRandom.uniform(blob_hash, 2, 15, 45)
                opacity = DeterministicRandom.randint(blob_hash, 3, 30, 80)

                draw.ellipse(
                    [x + offset_x - size/2, y + offset_y - size/2,
                     x + offset_x + size/2, y + offset_y + size/2],
                    fill=color + (opacity,)
                )

        num_lines = DeterministicRandom.randint(seed_hash, 9000, 20, 40)
        for i in range(num_lines):
            line_hash = f"{seed_hash}_line_{i}"
            x1 = DeterministicRandom.uniform(line_hash, 0, 0, self.width)
            y1 = DeterministicRandom.uniform(line_hash, 1, 0, self.height)
            x2 = DeterministicRandom.uniform(line_hash, 2, 0, self.width)
            y2 = DeterministicRandom.uniform(line_hash, 3, 0, self.height)

            color = vibrant_colors[DeterministicRandom.randint(line_hash, 4, 0, len(vibrant_colors) - 1)]

            width = DeterministicRandom.randint(line_hash, 5, 2, 8)
            opacity = DeterministicRandom.randint(line_hash, 6, 50, 120)

            draw.line([(x1, y1), (x2, y2)], fill=color + (opacity,), width=width)
