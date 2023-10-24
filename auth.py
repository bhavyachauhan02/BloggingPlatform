import jwt
from flask import request, jsonify
from functools import wraps

SECRET_KEY = 'your_secret_key'

def generate_token(username, role):
    payload = {
        'username': username,
        'role': role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        decoded_token = decode_token(token)
        if decoded_token:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Unauthorized'}), 401  # Unauthorized
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        decoded_token = decode_token(token)
        if decoded_token and decoded_token.get('role') == 'admin':
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Unauthorized'}), 403  # Forbidden
    return decorated_function
