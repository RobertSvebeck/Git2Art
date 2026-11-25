"""Save artwork images in the format their file extension asks for."""

from PIL import Image

WEBP_QUALITY = 90
FLAT_COLOURS = 512


def save_artwork(image, path):
    """WebP at high quality for .webp (artworks on the site); optimised PNG for .png."""
    if image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')
    lower = str(path).lower()
    if lower.endswith('.webp'):
        if image.getcolors(maxcolors=FLAT_COLOURS) is not None:
            # Flat-colour art (pixel art, hard-edged fields) is smaller and crisper lossless
            image.save(path, 'WEBP', lossless=True, quality=100, method=5)
        else:
            image.save(path, 'WEBP', quality=WEBP_QUALITY, method=5)
    elif lower.endswith('.png'):
        image.save(path, 'PNG', optimize=True)
    else:
        image.save(path)


def to_png_bytes(path):
    """Re-encode an artwork as PNG in memory (for downloads of WebP masters)."""
    import io
    buffer = io.BytesIO()
    with Image.open(path) as image:
        image.convert('RGB').save(buffer, 'PNG', optimize=False)
    return buffer.getvalue()
