"""ArtStyle model for database operations."""

from utils.db import get_db_cursor


class ArtStyle:
    """Model for art style database operations."""

    @staticmethod
    def create(style_id, display_name, description, class_name, is_active=True, sort_order=0):
        """Create or update an art style record."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO art_styles (style_id, display_name, description, class_name, is_active, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    description = VALUES(description),
                    class_name = VALUES(class_name),
                    is_active = VALUES(is_active),
                    sort_order = VALUES(sort_order),
                    updated_at = CURRENT_TIMESTAMP
            """, (style_id, display_name, description, class_name, is_active, sort_order))
            return cursor.lastrowid

    @staticmethod
    def get_by_id(style_id):
        """Get art style by style_id."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM art_styles
                WHERE style_id = %s
            """, (style_id,))
            return cursor.fetchone()

    @staticmethod
    def get_all(active_only=False, order_by='sort_order'):
        """Get all art styles."""
        allowed_orders = ['sort_order', 'style_id', 'display_name', 'created_at']
        if order_by not in allowed_orders:
            order_by = 'sort_order'

        query = f"SELECT * FROM art_styles"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += f" ORDER BY {order_by} ASC, style_id ASC"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_active_styles():
        """Get all active art styles for UX display."""
        return ArtStyle.get_all(active_only=True, order_by='sort_order')

    @staticmethod
    def update_status(style_id, is_active):
        """Enable or disable an art style."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE art_styles
                SET is_active = %s, updated_at = CURRENT_TIMESTAMP
                WHERE style_id = %s
            """, (is_active, style_id))
            return cursor.rowcount > 0

    @staticmethod
    def update_sort_order(style_id, sort_order):
        """Update the sort order of an art style."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE art_styles
                SET sort_order = %s, updated_at = CURRENT_TIMESTAMP
                WHERE style_id = %s
            """, (sort_order, style_id))
            return cursor.rowcount > 0

    @staticmethod
    def delete(style_id):
        """Delete an art style (use with caution - may affect existing artworks)."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM art_styles
                WHERE style_id = %s
            """, (style_id,))
            return cursor.rowcount > 0

    @staticmethod
    def exists(style_id):
        """Check if an art style exists."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count FROM art_styles
                WHERE style_id = %s
            """, (style_id,))
            result = cursor.fetchone()
            return result['count'] > 0

    @staticmethod
    def is_active(style_id):
        """Check if an art style is active."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT is_active FROM art_styles
                WHERE style_id = %s
            """, (style_id,))
            result = cursor.fetchone()
            return result['is_active'] if result else False

    @staticmethod
    def get_usage_stats():
        """Get usage statistics for each art style."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT
                    s.style_id,
                    s.display_name,
                    s.is_active,
                    COUNT(a.id) as artwork_count,
                    COALESCE(SUM(a.like_count), 0) as total_likes
                FROM art_styles s
                LEFT JOIN artworks a ON s.style_id = a.art_style
                GROUP BY s.style_id, s.display_name, s.is_active
                ORDER BY artwork_count DESC
            """)
            return cursor.fetchall()
