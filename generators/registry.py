"""Style registry and factory for art generators."""

from .expressionist_style import ExpressionistStyleGenerator
from .impressionist_style import ImpressionistStyleGenerator
from .watercolor_style import WatercolorStyleGenerator
from .pixel_style import PixelStyleGenerator
from .face_style import FaceStyleGenerator

# Registry of all available art styles
STYLE_REGISTRY = {
    'expressionist': ExpressionistStyleGenerator,
    'impressionist': ImpressionistStyleGenerator,
    'watercolor': WatercolorStyleGenerator,
    'pixel': PixelStyleGenerator,
    'face': FaceStyleGenerator,
    # Future styles will be added here:
    # 'minimalist': MinimalistStyleGenerator,
    # 'geometric': GeometricStyleGenerator,
}

# Default style to use when none is specified
DEFAULT_STYLE = 'expressionist'


def get_generator(style='expressionist', **kwargs):
    """Factory function to get an art generator by style name.

    Args:
        style: Name of the art style ('expressionist', 'minimalist', etc.)
        **kwargs: Additional parameters to pass to the generator constructor
                  (repo_path, width, height, aspect_ratio, etc.)

    Returns:
        An instance of the requested art generator

    Raises:
        ValueError: If the requested style doesn't exist

    Example:
        >>> generator = get_generator('expressionist', repo_path='/path/to/repo', width=1600)
        >>> generator.generate_art('output.png')
    """
    if style not in STYLE_REGISTRY:
        available = ', '.join(STYLE_REGISTRY.keys())
        raise ValueError(f"Unknown art style: '{style}'. Available styles: {available}")

    generator_class = STYLE_REGISTRY[style]
    return generator_class(**kwargs)


def list_available_styles():
    """Get information about all available art styles.

    Returns:
        List of dictionaries with style information:
        [
            {
                'name': 'expressionist',
                'description': 'Bold expressionist style...',
                'class': 'ExpressionistStyleGenerator'
            },
            ...
        ]
    """
    styles = []
    for style_name, generator_class in STYLE_REGISTRY.items():
        # Create temporary instance to get info (no repo needed)
        try:
            info = {
                'name': generator_class.STYLE_NAME,
                'description': generator_class.STYLE_DESCRIPTION,
                'class': generator_class.__name__,
                'id': style_name
            }
            styles.append(info)
        except Exception:
            # If we can't get info, provide basic details
            styles.append({
                'name': style_name,
                'description': 'No description available',
                'class': generator_class.__name__,
                'id': style_name
            })

    return styles


def is_valid_style(style):
    """Check if a style name is valid.

    Args:
        style: Style name to check

    Returns:
        True if style exists, False otherwise
    """
    return style in STYLE_REGISTRY


def get_default_style():
    """Get the default style name.

    Returns:
        String name of the default style
    """
    return DEFAULT_STYLE
