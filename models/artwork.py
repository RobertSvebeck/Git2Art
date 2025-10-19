"""Artwork model for database operations."""

from utils.db import get_db_cursor, get_db_connection


class Artwork:
    """Model for artwork database operations."""

    @staticmethod
    def create(repo_url, repo_name, commit_hash, image_path, image_filename):
        """Create or update artwork record."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO artworks (repo_url, repo_name, commit_hash, image_path, image_filename)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    image_path = VALUES(image_path),
                    image_filename = VALUES(image_filename),
                    updated_at = CURRENT_TIMESTAMP
            """, (repo_url, repo_name, commit_hash, image_path, image_filename))
            return cursor.lastrowid

    @staticmethod
    def get_by_repo_and_commit(repo_url, commit_hash):
        """Get artwork by repository URL and commit hash."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM artworks
                WHERE repo_url = %s AND commit_hash = %s
            """, (repo_url, commit_hash))
            return cursor.fetchone()

    @staticmethod
    def get_all(order_by='created_at', order_dir='DESC', limit=None):
        """Get all artworks with optional ordering and limit."""
        allowed_orders = ['created_at', 'like_count', 'repo_name']
        allowed_dirs = ['ASC', 'DESC']

        if order_by not in allowed_orders:
            order_by = 'created_at'
        if order_dir not in allowed_dirs:
            order_dir = 'DESC'

        query = f"SELECT * FROM artworks ORDER BY {order_by} {order_dir}"
        if limit:
            query += f" LIMIT {int(limit)}"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(artwork_id):
        """Get artwork by ID."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM artworks WHERE id = %s", (artwork_id,))
            return cursor.fetchone()

    @staticmethod
    def increment_like_count(artwork_id):
        """Increment like count for an artwork."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE artworks
                SET like_count = like_count + 1
                WHERE id = %s
            """, (artwork_id,))

    @staticmethod
    def decrement_like_count(artwork_id):
        """Decrement like count for an artwork."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE artworks
                SET like_count = GREATEST(0, like_count - 1)
                WHERE id = %s
            """, (artwork_id,))


class ArtworkLike:
    """Model for artwork like operations."""

    @staticmethod
    def add_like(artwork_id, user_identifier):
        """Add a like for an artwork from a user."""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                # Insert like
                cursor.execute("""
                    INSERT INTO artwork_likes (artwork_id, user_identifier)
                    VALUES (%s, %s)
                """, (artwork_id, user_identifier))

                # Increment count
                cursor.execute("""
                    UPDATE artworks
                    SET like_count = like_count + 1
                    WHERE id = %s
                """, (artwork_id,))

                connection.commit()
                return True
            except Exception:
                connection.rollback()
                return False
            finally:
                cursor.close()
                connection.close()
        except Exception:
            return False

    @staticmethod
    def remove_like(artwork_id, user_identifier):
        """Remove a like for an artwork from a user."""
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Delete like
            cursor.execute("""
                DELETE FROM artwork_likes
                WHERE artwork_id = %s AND user_identifier = %s
            """, (artwork_id, user_identifier))

            if cursor.rowcount > 0:
                # Decrement count
                cursor.execute("""
                    UPDATE artworks
                    SET like_count = GREATEST(0, like_count - 1)
                    WHERE id = %s
                """, (artwork_id,))
                connection.commit()
                return True

            connection.commit()
            return False
        except Exception:
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def has_liked(artwork_id, user_identifier):
        """Check if a user has liked an artwork."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count FROM artwork_likes
                WHERE artwork_id = %s AND user_identifier = %s
            """, (artwork_id, user_identifier))
            result = cursor.fetchone()
            return result['count'] > 0

    @staticmethod
    def get_likes_for_artwork(artwork_id):
        """Get all likes for an artwork."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM artwork_likes
                WHERE artwork_id = %s
                ORDER BY liked_at DESC
            """, (artwork_id,))
            return cursor.fetchall()
