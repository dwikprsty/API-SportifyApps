from flask_jwt_extended import get_jwt
from functools import wraps
from flask import jsonify

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            roles = claims.get('roles', [])
            if required_role not in roles:
                return jsonify({"msg": "Access forbidden: insufficient permissions"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
