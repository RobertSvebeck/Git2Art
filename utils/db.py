"""Database connection manager for Git2Art."""

import pymysql
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


def get_db_connection():
    """Create and return a database connection."""
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


@contextmanager
def get_db_cursor(commit=True):
    """Context manager for database operations with automatic cleanup."""
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def init_database():
    """Initialize database tables from schema.sql."""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Remove comments
    lines = []
    for line in schema_sql.split('\n'):
        if not line.strip().startswith('--'):
            lines.append(line)
    schema_sql = '\n'.join(lines)

    # Split by semicolon and filter empty statements
    statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        for statement in statements:
            if statement:
                cursor.execute(statement)
        connection.commit()
        print("✓ Database tables initialized successfully")
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def test_connection():
    """Test database connection and return server info."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            return True, version
    except Exception as e:
        return False, str(e)
