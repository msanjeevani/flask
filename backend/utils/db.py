from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialize database with Flask app
    """
    db.init_app(app)

    with app.app_context():
        db.create_all()