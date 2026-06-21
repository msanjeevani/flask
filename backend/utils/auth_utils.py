from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.models.user import User
from backend.utils.db import db

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def doctor_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') not in ['doctor', 'admin']:
            return jsonify({'error': 'Doctor access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def get_current_user():
    """Get the current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None

def validate_request_data(required_fields):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({'error': f'Missing fields: {missing_fields}'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(roles):
    """Decorator to check if user has required role(s)"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if isinstance(roles, str):
                allowed_roles = [roles]
            else:
                allowed_roles = roles
            
            if user_role not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {allowed_roles}'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def hospital_access_required(hospital_id_param='hospital_id'):
    """Decorator to check if user has access to hospital"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            # Get hospital_id from kwargs or request
            if hospital_id_param in kwargs:
                hospital_id = kwargs[hospital_id_param]
            else:
                data = request.get_json()
                hospital_id = data.get(hospital_id_param) if data else None
            
            # Admin can access all hospitals
            if user.role == 'admin':
                return fn(*args, **kwargs)
            
            # Doctor can only access their own hospital
            if user.role == 'doctor' and user.hospital_id != int(hospital_id):
                return jsonify({'error': 'Access denied to this hospital'}), 403
            
            # Researchers can access public hospitals only
            if user.role == 'researcher':
                # Check if hospital is public
                from backend.models.hospital import Hospital
                hospital = Hospital.query.get(hospital_id)
                if not hospital or not hospital.is_verified:
                    return jsonify({'error': 'Access denied'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def case_access_required(case_id_param='case_id'):
    """Decorator to check if user has access to case"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            # Get case_id from kwargs
            case_id = kwargs.get(case_id_param)
            
            if not case_id:
                return jsonify({'error': 'Case ID required'}), 400
            
            from backend.models.case import Case
            case = Case.query.get(case_id)
            
            if not case:
                return jsonify({'error': 'Case not found'}), 404
            
            # Admin can access all cases
            if user.role == 'admin':
                return fn(*args, **kwargs)
            
            # Check case privacy level
            if case.privacy_level == 'private':
                if case.doctor_id != user.id:
                    return jsonify({'error': 'Access denied to private case'}), 403
            
            elif case.privacy_level == 'hospital_only':
                if case.hospital_id != user.hospital_id:
                    return jsonify({'error': 'Access denied to hospital-only case'}), 403
            
            # Public cases are accessible to all authenticated users
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def generate_password_hash(password):
    """Generate password hash"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password_hash(password_hash, password):
    """Check password hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter'
    
    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter'
    
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number'
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return False, 'Password must contain at least one special character'
    
    return True, 'Password is valid'

def get_user_from_token():
    """Get user object from JWT token"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(user_id)
    except:
        pass
    return None

def require_json_content_type(fn):
    """Decorator to ensure request has JSON content type"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return fn(*args, **kwargs)
    return wrapper

def rate_limit(max_requests, window_seconds):
    """Simple rate limiting decorator"""
    from datetime import datetime, timedelta
    import time
    
    requests = {}
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            current_time = time.time()
            
            # Clean old requests
            cutoff_time = current_time - window_seconds
            requests[ip_address] = [
                req_time for req_time in requests.get(ip_address, [])
                if req_time > cutoff_time
            ]
            
            # Check rate limit
            if len(requests[ip_address]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Try again in {window_seconds} seconds'
                }), 429
            
            # Add current request
            requests[ip_address].append(current_time)
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def log_activity(action, details=None):
    """Log user activity"""
    from datetime import datetime
    
    user = get_current_user()
    if user:
        activity_log = {
            'user_id': user.id,
            'user_email': user.email,
            'user_role': user.role,
            'action': action,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None
        }
        
        # Here you can save to database or log file
        # For now, just print to console
        print(f"[ACTIVITY LOG] {activity_log}")
        
        return activity_log
    
    return None

def handle_exceptions(fn):
    """Decorator to handle exceptions"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            # Log the error
            import traceback
            error_details = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'endpoint': request.path,
                'method': request.method
            }
            print(f"[ERROR] {error_details}")
            
            # Return appropriate error response
            return jsonify({
                'error': 'Internal server error',
                'message': 'Something went wrong. Please try again later.'
            }), 500
    return wrapper