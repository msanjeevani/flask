from backend.utils.db import db
from datetime import datetime
import json

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(50), unique=True, nullable=False)
    patient_age = db.Column(db.Integer, nullable=False)
    patient_gender = db.Column(db.Enum('male', 'female', 'other'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    lab_results = db.Column(db.Text)
    imaging_results = db.Column(db.Text)
    initial_treatment = db.Column(db.Text)
    outcome = db.Column(db.Enum('recovered', 'improved', 'stable', 'worsened', 'deceased'))
    severity = db.Column(db.Enum('mild', 'moderate', 'severe', 'critical'))
    category = db.Column(db.String(100))
    anonymized_data = db.Column(db.Text)
    attachments = db.Column(db.Text)
    is_anonymous = db.Column(db.Boolean, default=True)
    privacy_level = db.Column(db.Enum('public', 'hospital_only', 'private'), default='hospital_only')
    
    # Foreign keys
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admission_date = db.Column(db.Date)
    discharge_date = db.Column(db.Date)
    
    # Relationships
    treatments = db.relationship('Treatment', backref='case', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'patient_age': self.patient_age,
            'patient_gender': self.patient_gender,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'medical_history': self.medical_history,
            'lab_results': self.lab_results,
            'imaging_results': self.imaging_results,
            'initial_treatment': self.initial_treatment,
            'outcome': self.outcome,
            'severity': self.severity,
            'category': self.category,
            'privacy_level': self.privacy_level,
            'hospital_id': self.hospital_id,
            'doctor_id': self.doctor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'discharge_date': self.discharge_date.isoformat() if self.discharge_date else None
        }