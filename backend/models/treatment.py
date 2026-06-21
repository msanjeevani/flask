from extensions import db
from datetime import date

class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    treatment_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    medication = db.Column(db.String(255))
    dosage = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    side_effects = db.Column(db.Text)
    effectiveness = db.Column(db.String(50))
    cost = db.Column(db.Float)
    
    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "treatment_type": self.treatment_type,
            "description": self.description,
            "medication": self.medication,
            "dosage": self.dosage,
            "duration": self.duration,
            "start_date": str(self.start_date) if self.start_date else None,
            "end_date": str(self.end_date) if self.end_date else None,
            "side_effects": self.side_effects,
            "effectiveness": self.effectiveness,
            "cost": self.cost,
        }
