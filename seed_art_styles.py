"""Seed art_styles table from the generator registry."""

from models import ArtStyle
from generators import list_available_styles


def seed_art_styles():
    """Populate art_styles table from registry."""
    print("Seeding art_styles table from generator registry...\n")

    # Get all available styles from registry
    styles = list_available_styles()

    if not styles:
        print("⚠️  No styles found in registry")
        return False

    print(f"Found {len(styles)} style(s) in registry:\n")

    # Define sort order (you can customize this)
    sort_order_map = {
        'expressionist': 0,
        'impressionist': 1,
        'watercolor': 2,
        'pixel': 3,
        'face': 4,
        'nature': 5,
        'psychedelic': 6,
    }

    success_count = 0
    error_count = 0

    for style in styles:
        style_id = style['id']
        display_name = style['name'].title()  # Capitalize for display
        description = style['description']
        class_name = style['class']
        sort_order = sort_order_map.get(style_id, 999)  # Unknown styles go last

        try:
            ArtStyle.create(
                style_id=style_id,
                display_name=display_name,
                description=description,
                class_name=class_name,
                is_active=True,
                sort_order=sort_order
            )
            print(f"✓ {style_id:15} - {display_name}")
            success_count += 1
        except Exception as e:
            print(f"✗ {style_id:15} - Error: {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Seed completed: {success_count} succeeded, {error_count} failed")
    print(f"{'='*60}\n")

    # Display current art_styles table
    print("Current art styles in database:\n")
    all_styles = ArtStyle.get_all()

    if all_styles:
        print(f"{'ID':<5} {'Style ID':<15} {'Display Name':<25} {'Active':<8} {'Sort':<5}")
        print("-" * 60)
        for s in all_styles:
            active = "✓" if s['is_active'] else "✗"
            print(f"{s['id']:<5} {s['style_id']:<15} {s['display_name']:<25} {active:<8} {s['sort_order']:<5}")
    else:
        print("No styles in database")

    return error_count == 0


if __name__ == '__main__':
    try:
        success = seed_art_styles()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Seed failed: {e}")
        exit(1)
