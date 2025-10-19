"""Watermark utility for generated artwork."""

from PIL import Image, ImageDraw, ImageFont


def add_watermark(image_path, github_url):
    """
    Add a subtle watermark to the generated artwork.

    Args:
        image_path: Path to the image file
        github_url: GitHub repository URL to include in watermark
    """
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Get image dimensions
        width, height = img.size

        # Prepare watermark text
        watermark_text = f"git2art • {github_url}"

        # Try to use a nice font, fall back to default if not available
        try:
            font_size = max(12, width // 80)
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()

        # Calculate text position (bottom right corner)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = width - text_width - 20
        y = height - text_height - 20

        # Draw semi-transparent watermark
        # Create a new image for the watermark with transparency
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        watermark_draw = ImageDraw.Draw(watermark)

        # Draw watermark with low opacity (30% opacity = 77 alpha)
        watermark_draw.text((x, y), watermark_text, fill=(255, 255, 255, 77), font=font)

        # Composite watermark onto original image
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        img = Image.alpha_composite(img, watermark)

        # Convert back to RGB for PNG saving
        img = img.convert('RGB')

        # Save the watermarked image
        img.save(image_path, 'PNG', optimize=True)

    except Exception as e:
        # If watermarking fails, don't crash - just log and continue
        print(f"Warning: Failed to add watermark: {e}")
