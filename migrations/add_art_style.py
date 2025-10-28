"""Migration: Add art_style field to artworks table and mark existing art as 'default'."""

import sys
import os

# Add parent directory to path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db_cursor, get_db_connection

def migrate():
    """Add art_style column and update existing records."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        print("Starting migration: add_art_style...")

        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'artworks'
            AND COLUMN_NAME = 'art_style'
        """)
        result = cursor.fetchone()

        if result['count'] > 0:
            print("✓ Column 'art_style' already exists")
        else:
            print("Adding 'art_style' column...")
            cursor.execute("""
                ALTER TABLE artworks
                ADD COLUMN art_style VARCHAR(50) NOT NULL DEFAULT 'default'
                AFTER commit_hash
            """)
            print("✓ Column added")

        # Update all existing records to have 'default' style
        print("Setting existing artworks to 'default' style...")
        cursor.execute("""
            UPDATE artworks
            SET art_style = 'default'
            WHERE art_style IS NULL OR art_style = ''
        """)
        affected = cursor.rowcount
        print(f"✓ Updated {affected} existing artworks to 'default' style")

        # Add index if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'artworks'
            AND INDEX_NAME = 'idx_art_style'
        """)
        result = cursor.fetchone()

        if result['count'] > 0:
            print("✓ Index 'idx_art_style' already exists")
        else:
            print("Adding index on art_style...")
            cursor.execute("""
                ALTER TABLE artworks
                ADD INDEX idx_art_style (art_style)
            """)
            print("✓ Index added")

        # Drop old unique constraint if exists
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'artworks'
            AND INDEX_NAME = 'unique_repo_commit'
        """)
        result = cursor.fetchone()

        if result['count'] > 0:
            print("Dropping old unique constraint 'unique_repo_commit'...")
            cursor.execute("""
                ALTER TABLE artworks
                DROP INDEX unique_repo_commit
            """)
            print("✓ Old constraint dropped")

        # Add new unique constraint including art_style
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'artworks'
            AND INDEX_NAME = 'unique_repo_commit_style'
        """)
        result = cursor.fetchone()

        if result['count'] > 0:
            print("✓ Unique constraint 'unique_repo_commit_style' already exists")
        else:
            print("Adding new unique constraint...")
            cursor.execute("""
                ALTER TABLE artworks
                ADD UNIQUE KEY unique_repo_commit_style (repo_url, commit_hash, art_style)
            """)
            print("✓ New constraint added")

        connection.commit()
        print("\n✅ Migration completed successfully!")
        return True

    except Exception as e:
        connection.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
