from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
from backend.models.case import Case
from backend.models.treatment import Treatment
from backend.models.user import User
from backend.utils.db import db
from sqlalchemy import func

recommendation_bp = Blueprint('recommendations', __name__)

@recommendation_bp.route('/similar-cases', methods=['POST'])
@jwt_required()
def find_similar_cases():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Query existing cases
    query = Case.query.filter(Case.privacy_level.in_(['public', 'hospital_only']))
    
    # Filter by hospital if not admin
    if user.role == 'doctor':
        query = query.filter(
            (Case.hospital_id == user.hospital_id) | (Case.privacy_level == 'public')
        )
    
    # Apply category filter if provided
    if 'category' in data:
        query = query.filter_by(category=data['category'])
    
    # Get existing cases
    existing_cases = query.limit(50).all()
    
    if not existing_cases:
        return jsonify({'message': 'No cases found for comparison'}), 404
    
    # Simple similarity calculation based on symptoms
    search_symptoms = data.get('symptoms', '').lower()
    results = []
    
    for case in existing_cases:
        case_symptoms = case.symptoms.lower() if case.symptoms else ''
        
        # Simple word matching for similarity
        search_words = set(search_symptoms.split())
        case_words = set(case_symptoms.split())
        
        if search_words and case_words:
            common_words = search_words.intersection(case_words)
            similarity = len(common_words) / len(search_words) if search_words else 0
            
            if similarity > 0.1:  # Only include if some similarity
                case_data = case.to_dict()
                treatments = Treatment.query.filter_by(case_id=case.id).all()
                case_data['treatments'] = [t.to_dict() for t in treatments[:3]]
                
                results.append({
                    'case_data': case_data,
                    'similarity': round(similarity, 3)
                })
    
    # Sort by similarity
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Format response
    response = []
    for item in results[:10]:  # Top 10 results
        case = item['case_data']
        response.append({
            'case_id': case['case_id'],
            'similarity_score': item['similarity'],
            'patient_age': case['patient_age'],
            'patient_gender': case['patient_gender'],
            'symptoms': case['symptoms'],
            'diagnosis': case.get('diagnosis'),
            'treatments': case.get('treatments', [])
        })
    
    return jsonify({
        'similar_cases': response,
        'total_found': len(response)
    }), 200

@recommendation_bp.route('/treatment-recommendations', methods=['POST'])
@jwt_required()
def get_treatment_recommendations():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Query successful cases
    query = Case.query.filter(
        Case.privacy_level.in_(['public', 'hospital_only']),
        Case.outcome.in_(['recovered', 'improved'])
    )
    
    if user.role == 'doctor':
        query = query.filter(
            (Case.hospital_id == user.hospital_id) | (Case.privacy_level == 'public')
        )
    
    if 'category' in data:
        query = query.filter_by(category=data['category'])
    
    existing_cases = query.limit(50).all()
    
    if not existing_cases:
        return jsonify({'message': 'No successful cases found'}), 404
    
    # Get treatments from successful cases
    treatment_stats = {}
    
    for case in existing_cases:
        treatments = Treatment.query.filter_by(case_id=case.id).filter(
            Treatment.effectiveness.in_(['excellent', 'good'])
        ).all()
        
        for treatment in treatments:
            treatment_type = treatment.treatment_type
            
            if treatment_type not in treatment_stats:
                treatment_stats[treatment_type] = {
                    'count': 0,
                    'effectiveness_scores': []
                }
            
            effectiveness_map = {
                'excellent': 1.0,
                'good': 0.75,
                'fair': 0.5,
                'poor': 0.25
            }
            
            treatment_stats[treatment_type]['count'] += 1
            treatment_stats[treatment_type]['effectiveness_scores'].append(
                effectiveness_map.get(treatment.effectiveness, 0.5)
            )
    
    # Calculate recommendations
    recommendations = []
    for treatment_type, stats in treatment_stats.items():
        if stats['count'] == 0:
            continue
        
        avg_effectiveness = np.mean(stats['effectiveness_scores'])
        
        recommendations.append({
            'treatment_type': treatment_type,
            'frequency': stats['count'],
            'average_effectiveness': round(avg_effectiveness, 3),
            'confidence_score': round(avg_effectiveness, 3)  # Simple confidence score
        })
    
    # Sort by confidence score
    recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return jsonify({
        'recommendations': recommendations[:10],
        'based_on_cases': len(existing_cases)
    }), 200

@recommendation_bp.route('/analytics/treatment-effectiveness', methods=['GET'])
@jwt_required()
def get_treatment_effectiveness():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Join cases and treatments
    query = db.session.query(
        Treatment.treatment_type,
        Treatment.effectiveness,
        func.count(Treatment.id).label('count')
    ).join(Case)
    
    if user.role == 'doctor':
        query = query.filter(Case.hospital_id == user.hospital_id)
    
    effectiveness_data = query.filter(
        Treatment.effectiveness.isnot(None),
        Treatment.treatment_type.isnot(None)
    ).group_by(
        Treatment.treatment_type,
        Treatment.effectiveness
    ).all()
    
    # Format response
    result = {}
    for treatment_type, effectiveness, count in effectiveness_data:
        if treatment_type not in result:
            result[treatment_type] = {}
        result[treatment_type][effectiveness] = count
    
    return jsonify({'effectiveness': result}), 200