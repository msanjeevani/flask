"""
WSGI entry point for production servers (Gunicorn, uWSGI)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app

# Create application instance
app = create_app('production')

if __name__ == '__main__':
    app.run()