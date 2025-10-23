#!/usr/bin/env python
"""
Passenger WSGI application entry point for Apache/cPanel deployment.
This file is required for Passenger (Ruby/Python WSGI app server) to run the Flask application.
"""

import sys
import os

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Import and create the Flask application
from app import create_app

# Create the application instance (Passenger expects this name)
application = create_app()
