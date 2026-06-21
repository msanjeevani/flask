from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from backend.models.user import User
from backend.models.hospital import Hospital
from backend.utils.db import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['email', 'password', 'name', 'role']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing fields: {missing_fields}'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate hospital if provided
    if 'hospital_id' in data:
        hospital = Hospital.query.get(data['hospital_id'])
        if not hospital:
            return jsonify({'error': 'Invalid hospital ID'}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        name=data['name'],
        role=data['role'],
        hospital_id=data.get('hospital_id'),
        specialization=data.get('specialization'),
        license_number=data.get('license_number')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'role': user.role,
            'email': user.email,
            'hospital_id': user.hospital_id
        },
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update allowed fields
    allowed_fields = ['name', 'specialization', 'license_number']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200