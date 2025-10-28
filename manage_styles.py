"""Utility script for managing art styles in the database."""

import sys
import argparse
from models import ArtStyle


def list_styles(active_only=False):
    """List all art styles."""
    styles = ArtStyle.get_all(active_only=active_only)

    if not styles:
        print("No styles found in database")
        return

    filter_text = "(active only)" if active_only else "(all)"
    print(f"\nArt Styles {filter_text}:\n")
    print(f"{'ID':<5} {'Style ID':<15} {'Display Name':<25} {'Active':<8} {'Sort':<5}")
    print("-" * 65)

    for s in styles:
        active = "✓" if s['is_active'] else "✗"
        print(f"{s['id']:<5} {s['style_id']:<15} {s['display_name']:<25} {active:<8} {s['sort_order']:<5}")

    print(f"\nTotal: {len(styles)} style(s)")


def show_style(style_id):
    """Show detailed information about a specific style."""
    style = ArtStyle.get_by_id(style_id)

    if not style:
        print(f"Style '{style_id}' not found")
        return False

    print(f"\nStyle Details:\n")
    print(f"  ID:           {style['id']}")
    print(f"  Style ID:     {style['style_id']}")
    print(f"  Display Name: {style['display_name']}")
    print(f"  Description:  {style['description']}")
    print(f"  Class Name:   {style['class_name']}")
    print(f"  Active:       {'Yes' if style['is_active'] else 'No'}")
    print(f"  Sort Order:   {style['sort_order']}")
    print(f"  Created:      {style['created_at']}")
    print(f"  Updated:      {style['updated_at']}")

    return True


def enable_style(style_id):
    """Enable an art style."""
    if ArtStyle.update_status(style_id, True):
        print(f"✓ Style '{style_id}' enabled")
        return True
    else:
        print(f"✗ Failed to enable style '{style_id}'")
        return False


def disable_style(style_id):
    """Disable an art style."""
    if ArtStyle.update_status(style_id, False):
        print(f"✓ Style '{style_id}' disabled")
        return True
    else:
        print(f"✗ Failed to disable style '{style_id}'")
        return False


def show_usage_stats():
    """Show usage statistics for each style."""
    stats = ArtStyle.get_usage_stats()

    if not stats:
        print("No statistics available")
        return

    print(f"\nArt Style Usage Statistics:\n")
    print(f"{'Style ID':<15} {'Display Name':<25} {'Active':<8} {'Artworks':<10} {'Likes':<10}")
    print("-" * 75)

    for s in stats:
        active = "✓" if s['is_active'] else "✗"
        print(f"{s['style_id']:<15} {s['display_name']:<25} {active:<8} {s['artwork_count']:<10} {s['total_likes']:<10}")

    print(f"\nTotal styles: {len(stats)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Manage art styles in the database')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List command
    list_parser = subparsers.add_parser('list', help='List all art styles')
    list_parser.add_argument('--active', action='store_true', help='Show only active styles')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show details of a specific style')
    show_parser.add_argument('style_id', help='Style ID to show')

    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable an art style')
    enable_parser.add_argument('style_id', help='Style ID to enable')

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable an art style')
    disable_parser.add_argument('style_id', help='Style ID to disable')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show usage statistics')

    args = parser.parse_args()

    if args.command == 'list':
        list_styles(active_only=args.active)
    elif args.command == 'show':
        show_style(args.style_id)
    elif args.command == 'enable':
        enable_style(args.style_id)
    elif args.command == 'disable':
        disable_style(args.style_id)
    elif args.command == 'stats':
        show_usage_stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
