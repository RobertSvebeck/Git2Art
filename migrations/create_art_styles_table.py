"""Migration: Create art_styles table for managing available art styles."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db_cursor, get_db_connection


def migrate():
    """Create art_styles table."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        print("Starting migration: create_art_styles_table...")

        # Check if table already exists
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'art_styles'
        """)
        result = cursor.fetchone()

        if result['count'] > 0:
            print("✓ Table 'art_styles' already exists")
        else:
            print("Creating 'art_styles' table...")
            cursor.execute("""
                CREATE TABLE art_styles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    style_id VARCHAR(50) NOT NULL UNIQUE,
                    display_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    class_name VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    sort_order INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_style_id (style_id),
                    INDEX idx_is_active (is_active),
                    INDEX idx_sort_order (sort_order)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ Table created")

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
