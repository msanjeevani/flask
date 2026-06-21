from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
import uuid

from app import db
from models.case import Case
from models.user import User
from models.treatement import Treatment
cases_bp = Blueprint("cases", __name__)

@cases_bp.route("/", methods=["POST"])
@jwt_required()
def create_case():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["patient_age", "patient_gender", "symptoms"]
    for f in required_fields:
        if f not in data:
            return jsonify({"error": f"{f} is required"}), 400

    new_case = Case(
        case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
        patient_age=data["patient_age"],
        patient_gender=data["patient_gender"],
        symptoms=data["symptoms"],
        diagnosis=data.get("diagnosis"),
        medical_history=data.get("medical_history"),
        lab_results=json.dumps(data.get("lab_results", {})),
        initial_treatment=data.get("initial_treatment"),
        outcome=data.get("outcome"),
        severity=data.get("severity", "moderate"),
        category=data.get("category"),
        privacy_level=data.get("privacy_level", "hospital_only"),
        hospital_id=user.hospital_id,
        doctor_id=user.id
    )

    db.session.add(new_case)
    db.session.commit()

    # treatments optional
    treatments = data.get("treatments", [])
    if isinstance(treatments, list):
        for t in treatments:
            tr = Treatment(
                case_id=new_case.id,
                treatment_type=t.get("treatment_type"),
                description=t.get("description"),
                medication=t.get("medication"),
                dosage=t.get("dosage"),
                duration=t.get("duration"),
                side_effects=t.get("side_effects"),
                effectiveness=t.get("effectiveness"),
                cost=t.get("cost")
            )
            db.session.add(tr)

        db.session.commit()

    return jsonify({"message": "Case created", "case": new_case.to_dict()}), 201


@cases_bp.route("/", methods=["GET"])
@jwt_required()
def list_cases():
    all_cases = Case.query.order_by(Case.id.desc()).all()
    return jsonify({"cases": [c.to_dict() for c in all_cases]}), 200
