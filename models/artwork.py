"""Artwork model for database operations."""

from utils.db import get_db_cursor, get_db_connection


class Artwork:
    """Model for artwork database operations."""

    @staticmethod
    def create(repo_url, repo_name, commit_hash, image_path, image_filename, art_style='expressionist'):
        """Create or update artwork record."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO artworks (repo_url, repo_name, commit_hash, art_style, image_path, image_filename)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    image_path = VALUES(image_path),
                    image_filename = VALUES(image_filename),
                    updated_at = CURRENT_TIMESTAMP
            """, (repo_url, repo_name, commit_hash, art_style, image_path, image_filename))
            return cursor.lastrowid

    @staticmethod
    def get_by_repo_and_commit(repo_url, commit_hash, art_style='expressionist'):
        """Get artwork by repository URL, commit hash, and art style."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM artworks
                WHERE repo_url = %s AND commit_hash = %s AND art_style = %s
            """, (repo_url, commit_hash, art_style))
            return cursor.fetchone()

    @staticmethod
    def get_all(order_by='created_at', order_dir='DESC', limit=None):
        """Get all artworks with optional ordering and limit."""
        allowed_orders = ['created_at', 'like_count', 'repo_name', 'art_style']
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

    @staticmethod
    def get_versions_by_repo(repo_url):
        """Get all versions of artwork for a repository, ordered by creation date."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM artworks
                WHERE repo_url = %s
                ORDER BY created_at ASC
            """, (repo_url,))
            return cursor.fetchall()

    @staticmethod
    def get_latest_by_repo(repo_url):
        """Get the latest version of artwork for a repository."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM artworks
                WHERE repo_url = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (repo_url,))
            return cursor.fetchone()

    @staticmethod
    def get_unique_repos():
        """Get all unique repositories with their latest version count."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT repo_url, repo_name, COUNT(*) as version_count
                FROM artworks
                GROUP BY repo_url, repo_name
                ORDER BY MAX(created_at) DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_repo_and_style(repo_url, art_style='expressionist'):
        """Get all artworks for a repository in a specific style."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM artworks
                WHERE repo_url = %s AND art_style = %s
                ORDER BY created_at DESC
            """, (repo_url, art_style))
            return cursor.fetchall()

    @staticmethod
    def get_styles_for_repo(repo_url):
        """Get all unique styles available for a repository."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT DISTINCT art_style, COUNT(*) as count
                FROM artworks
                WHERE repo_url = %s
                GROUP BY art_style
                ORDER BY count DESC
            """, (repo_url,))
            return cursor.fetchall()

    @staticmethod
    def get_latest_per_repo_and_style():
        """Get the latest artwork for each unique (repo_url, art_style) combination."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT a.*
                FROM artworks a
                INNER JOIN (
                    SELECT repo_url, art_style, MAX(created_at) as max_created_at
                    FROM artworks
                    GROUP BY repo_url, art_style
                ) latest
                ON a.repo_url = latest.repo_url
                AND a.art_style = latest.art_style
                AND a.created_at = latest.max_created_at
                ORDER BY a.art_style ASC, a.created_at DESC
            """)
            return cursor.fetchall()


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
