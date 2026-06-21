from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.hospital import Hospital
from backend.models.case import Case
from backend.models.user import User
from backend.utils.db import db

hospital_bp = Blueprint('hospitals', __name__)

@hospital_bp.route('/', methods=['POST'])
@jwt_required()
def create_hospital():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user is admin
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' not in data:
        return jsonify({'error': 'Hospital name required'}), 400
    
    hospital = Hospital(
        name=data['name'],
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        country=data.get('country'),
        phone=data.get('phone'),
        email=data.get('email'),
        website=data.get('website'),
        bed_capacity=data.get('bed_capacity'),
        specialty=data.get('specialty')
    )
    
    db.session.add(hospital)
    db.session.commit()
    
    return jsonify({
        'message': 'Hospital created successfully',
        'hospital': hospital.to_dict()
    }), 201

@hospital_bp.route('/', methods=['GET'])
@jwt_required()
def get_hospitals():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Hospital.query
    
    if search:
        query = query.filter(
            Hospital.name.ilike(f'%{search}%') |
            Hospital.city.ilike(f'%{search}%') |
            Hospital.specialty.ilike(f'%{search}%')
        )
    
    hospitals = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'hospitals': [h.to_dict() for h in hospitals.items],
        'total': hospitals.total,
        'page': hospitals.page,
        'per_page': hospitals.per_page,
        'pages': hospitals.pages
    }), 200

@hospital_bp.route('/<int:hospital_id>', methods=['GET'])
@jwt_required()
def get_hospital(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    return jsonify({'hospital': hospital.to_dict()}), 200

@hospital_bp.route('/<int:hospital_id>/cases', methods=['GET'])
@jwt_required()
def get_hospital_cases(hospital_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user belongs to this hospital (unless admin)
    if user.role != 'admin' and user.hospital_id != hospital_id:
        return jsonify({'error': 'Access denied'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    severity = request.args.get('severity')
    
    query = Case.query.filter_by(hospital_id=hospital_id)
    
    if category:
        query = query.filter_by(category=category)
    if severity:
        query = query.filter_by(severity=severity)
    
    cases = query.order_by(Case.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'cases': [case.to_dict() for case in cases.items],
        'total': cases.total,
        'page': cases.page,
        'pages': cases.pages
    }), 200

@hospital_bp.route('/<int:hospital_id>/stats', methods=['GET'])
@jwt_required()
def get_hospital_stats(hospital_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin' and user.hospital_id != hospital_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get total cases
    total_cases = Case.query.filter_by(hospital_id=hospital_id).count()
    
    # Get cases by severity
    severity_counts = db.session.query(
        Case.severity, db.func.count(Case.id)
    ).filter_by(hospital_id=hospital_id).group_by(Case.severity).all()
    
    # Get cases by outcome
    outcome_counts = db.session.query(
        Case.outcome, db.func.count(Case.id)
    ).filter_by(hospital_id=hospital_id).group_by(Case.outcome).all()
    
    # Get cases by category (top 10)
    category_counts = db.session.query(
        Case.category, db.func.count(Case.id)
    ).filter_by(hospital_id=hospital_id).group_by(Case.category).order_by(
        db.func.count(Case.id).desc()
    ).limit(10).all()
    
    return jsonify({
        'total_cases': total_cases,
        'severity_distribution': dict(severity_counts),
        'outcome_distribution': dict(outcome_counts),
        'top_categories': dict(category_counts)
    }), 200