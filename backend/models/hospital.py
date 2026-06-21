from backend.utils.db import db
from datetime import datetime

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    bed_capacity = db.Column(db.Integer)
    specialty = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cases = db.relationship('Case', backref='hospital', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'bed_capacity': self.bed_capacity,
            'specialty': self.specialty,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }