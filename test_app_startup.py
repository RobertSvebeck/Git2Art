#!/usr/bin/env python3
"""
Diagnostic script to test Git2Art Flask app startup.
Run this on your cPanel server to identify startup errors.
"""

import sys
import os

print("=" * 60)
print("GIT2ART STARTUP DIAGNOSTIC")
print("=" * 60)

# 1. Check Python version
print("\n[1] Python Version:")
print(f"    Python {sys.version}")
print(f"    Path: {sys.executable}")

# 2. Check current directory
print(f"\n[2] Current Directory:")
print(f"    {os.getcwd()}")

# 3. Check .env file
print(f"\n[3] .env File:")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"    ✓ .env exists at {env_path}")
else:
    print(f"    ✗ .env NOT FOUND at {env_path}")

# 4. Test imports
print(f"\n[4] Testing Imports:")

try:
    import flask
    print(f"    ✓ Flask {flask.__version__}")
except ImportError as e:
    print(f"    ✗ Flask: {e}")

try:
    import dotenv
    print(f"    ✓ python-dotenv")
except ImportError as e:
    print(f"    ✗ python-dotenv: {e}")

try:
    import pymysql
    print(f"    ✓ PyMySQL")
except ImportError as e:
    print(f"    ✗ PyMySQL: {e}")

try:
    import PIL
    print(f"    ✓ Pillow")
except ImportError as e:
    print(f"    ✗ Pillow: {e}")

try:
    import git
    print(f"    ✓ GitPython")
except ImportError as e:
    print(f"    ✗ GitPython: {e}")

try:
    import numpy
    print(f"    ✓ NumPy")
except ImportError as e:
    print(f"    ✗ NumPy: {e}")

# 5. Test environment variables
print(f"\n[5] Environment Variables:")
try:
    from dotenv import load_dotenv
    load_dotenv(env_path)

    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_name = os.getenv('DB_NAME')

    if all([db_host, db_user, db_name]):
        print(f"    ✓ DB_HOST: {db_host}")
        print(f"    ✓ DB_USER: {db_user}")
        print(f"    ✓ DB_NAME: {db_name}")
    else:
        print(f"    ✗ Missing database environment variables")
        print(f"      DB_HOST: {db_host}")
        print(f"      DB_USER: {db_user}")
        print(f"      DB_NAME: {db_name}")
except Exception as e:
    print(f"    ✗ Error loading environment: {e}")

# 6. Test database connection
print(f"\n[6] Database Connection:")
try:
    import pymysql
    from dotenv import load_dotenv
    load_dotenv(env_path)

    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
    )
    print(f"    ✓ Connected to database")
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"    ✓ Database Version: {version}")
    conn.close()
except Exception as e:
    print(f"    ✗ Database Connection Failed: {e}")

# 7. Test Flask app creation
print(f"\n[7] Flask App Creation:")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from app import create_app
    app = create_app()
    print(f"    ✓ Flask app created successfully")
    print(f"    ✓ App root path: {app.root_path}")
    print(f"    ✓ Generated images dir: {app.config['GENERATED_IMAGES_DIR']}")
    print(f"    ✓ Temp repos dir: {app.config['TEMP_REPOS_DIR']}")
except Exception as e:
    print(f"    ✗ Flask app creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
