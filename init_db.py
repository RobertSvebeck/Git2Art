"""Initialize the database with schema."""

from utils.db import init_database, test_connection

if __name__ == '__main__':
    print("Testing database connection...")
    success, result = test_connection()

    if success:
        print(f"✓ Connected to database: {result}")
        print("\nInitializing database schema...")
        init_database()
        print("✓ Database initialization complete!")
    else:
        print(f"✗ Failed to connect to database: {result}")
        exit(1)
