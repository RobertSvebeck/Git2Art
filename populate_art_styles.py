"""Populate art styles in the database."""

from models.art_style import ArtStyle
from generators.registry import list_available_styles


def populate_art_styles():
    """Populate art styles from generator registry into database."""
    styles = list_available_styles()

    sort_order_map = {
        'expressionist': 0,
        'nature': 1,
        'impressionist': 2,
        'watercolor': 3,
        'pixel': 4,
        'face': 5
    }

    print("Populating art styles from generator registry...")

    for style in styles:
        style_id = style['id']
        display_name = style['name'].title()
        description = style['description']
        class_name = style['class']
        sort_order = sort_order_map.get(style_id, 99)

        try:
            ArtStyle.create(
                style_id=style_id,
                display_name=display_name,
                description=description,
                class_name=class_name,
                is_active=True,
                sort_order=sort_order
            )
            print(f"✓ Added/Updated: {style_id} - {display_name}")
        except Exception as e:
            print(f"✗ Failed to add {style_id}: {e}")

    print("\n✓ Art styles populated successfully!")


if __name__ == '__main__':
    populate_art_styles()
