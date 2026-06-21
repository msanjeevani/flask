"""
Routes package initialization
Centralize route registration for the Flask application
"""

from flask import Blueprint
from flask_cors import CORS
import os

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_routes(app):
    """
    Initialize and register all route blueprints with the Flask app
    
    Args:
        app: Flask application instance
    """
    # Import route modules here to avoid circular imports
    from .auth import auth_bp
    from .hospital_routes import hospital_bp
    from .case_routes import case_bp
    from .recommendation import recommendation_bp
    
    # Register blueprints under the main API blueprint
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    api_bp.register_blueprint(hospital_bp, url_prefix='/hospitals')
    api_bp.register_blueprint(case_bp, url_prefix='/cases')
    api_bp.register_blueprint(recommendation_bp, url_prefix='/recommendations')
    
    # Register the main API blueprint with the app
    app.register_blueprint(api_bp)
    
    # Enable CORS for all routes if needed
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Optional: Add health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Medical Case Management API'}, 200
    
    @app.route('/')
    def index():
        return {
            'message': 'Medical Case Management API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth/*',
                'hospitals': '/api/hospitals/*',
                'cases': '/api/cases/*',
                'recommendations': '/api/recommendations/*'
            }
        }

# Optional: Export commonly used items
__all__ = ['init_routes', 'api_bp']