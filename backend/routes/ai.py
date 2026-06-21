from flask import Blueprint, jsonify

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/', methods=['GET'])
def ai_home():
    return jsonify({"message": "AI endpoint working"})
