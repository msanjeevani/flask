# backend/routes/case_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db  # use extensions instead of app
from models.user import User
from models.case import Case
from models.treatment import Treatment
import json, uuid

case_bp = Blueprint('cases', __name__)

@case_bp.route('/', methods=['POST'])
@jwt_required()
def create_case():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    new_case = Case(
        case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
        patient_age=data['patient_age'],
        patient_gender=data['patient_gender'],
        symptoms=data['symptoms'],
        hospital_id=user.hospital_id,
        doctor_id=user.id
    )
    db.session.add(new_case)
    db.session.commit()

    return jsonify({'message': 'Case created', 'case': new_case.to_dict()}), 201

@case_bp.route('/', methods=['GET'])
@jwt_required()
def list_cases():
    cases = Case.query.order_by(Case.id.desc()).all()
    return jsonify({'cases': [c.to_dict() for c in cases]}), 200
