import sys
import os

# Add the project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application  # Import your Flask app instance and set it as the WSGI application
