#!/usr/bin/env python3
"""
CareMesh Application Runner
"""
import os
from app import create_app

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'development')

app = create_app()

if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG'],
        threaded=True
    )