"""
auth_routes.py
--------------
Handles authentication-related API routes:
- Login, logout, token refresh, password reset
- Returns JWT tokens for authenticated sessions
"""

from flask import Blueprint, request, jsonify, abort
from sqlalchemy import text
from api.utils.db import execute_query
import time
import jwt
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Configuration (move to config.py in production)
JWT_SECRET_KEY = "your-secret-key-here"  # Change this in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Simple rate limiting storage (in production, use Redis or proper storage)
request_counts = defaultdict(list)
RATE_LIMIT = 5  # requests per minute for auth endpoints
RATE_WINDOW = 60  # seconds

def hash_password(password):
    """Hash password using SHA256 (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_jwt_token(user_data):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_data['user_id'],
        'username': user_data['username'],
        'email': user_data['email'],
        'user_type_id': user_data['user_type_id'],
        'customer_id': user_data['customer_id'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def get_user_permissions(user_id):
    """Get user permissions based on user_access and role_types"""
    query = """
    SELECT DISTINCT
        ua.app_id,
        ca.title as app_title,
        ut.user_type,
        ut.description as user_type_desc,
        c.name as customer_name
    FROM user_access ua
    JOIN customer_apps ca ON ua.app_id = ca.app_id
    JOIN user u ON ua.user_id = u.user_id
    JOIN user_type ut ON u.user_type_id = ut.user_type_id
    JOIN customer c ON ua.customer_id = c.customer_id
    WHERE ua.user_id = :user_id
    """
    
    try:
        permissions = execute_query(query, {"user_id": user_id}, fetch_all=True)
        return [dict(perm._mapping) for perm in permissions] if permissions else []
    except Exception:
        return []

def check_rate_limit(client_ip):
    """Simple rate limiting check"""
    now = time.time()
    # Clean old requests
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                if now - req_time < RATE_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        abort(429)  # Too Many Requests
    
    request_counts[client_ip].append(now)

def create_response(status, message, data=None, code=200):
    response = {"status": status, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), code


# ---------- Authentication Endpoints ----------

@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    # Apply rate limiting
    check_rate_limit(request.remote_addr)
    
    # Check Content-Type
    if not request.is_json:
        abort(415)  # Unsupported Media Type
    
    try:
        data = request.get_json()
    except Exception:
        abort(400)  # Bad Request - Invalid JSON
    
    if not data or not data.get('username') or not data.get('password'):
        abort(422)  # Unprocessable Entity - Missing credentials
    
    username = data['username']
    password = data['password']
    
    try:
        # Find user by username or email
        user_query = """
        SELECT u.user_id, u.username, u.email, u.password_hash, u.user_type_id, 
               u.customer_id, u.name, u.department, ut.user_type, c.name as customer_name
        FROM user u
        JOIN user_type ut ON u.user_type_id = ut.user_type_id
        JOIN customer c ON u.customer_id = c.customer_id
        WHERE u.username = :username OR u.email = :username
        """
        
        user = execute_query(user_query, {"username": username}, fetch_one=True)
        
        if not user:
            abort(401)  # Unauthorized - User not found
        
        user_data = dict(user._mapping)
        
        # Verify password (in production, use bcrypt)
        if not verify_password(password, user_data['password_hash']):
            abort(401)  # Unauthorized - Wrong password
        
        # Generate JWT token
        token = generate_jwt_token(user_data)
        
        # Get user permissions
        permissions = get_user_permissions(user_data['user_id'])
        
        response_data = {
            "token": token,
            "user": {
                "user_id": user_data['user_id'],
                "username": user_data['username'],
                "email": user_data['email'],
                "name": user_data['name'],
                "department": user_data['department'],
                "user_type": user_data['user_type'],
                "customer_name": user_data['customer_name']
            },
            "permissions": permissions,
            "expires_in": JWT_EXPIRATION_HOURS * 3600  # seconds
        }
        
        return create_response("success", "Login successful", response_data, 200)
        
    except Exception as e:
        print(f"Login error: {e}")
        abort(500)  # Internal Server Error


@auth_bp.route("/validate", methods=["POST"])
def validate_token():
    """Validate JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401)  # Unauthorized
    
    token = auth_header.split(' ')[1]
    payload = decode_jwt_token(token)
    
    if not payload:
        abort(401)  # Unauthorized - Invalid or expired token
    
    # Verify user still exists
    user_query = "SELECT user_id, username, email FROM user WHERE user_id = :user_id"
    try:
        user = execute_query(user_query, {"user_id": payload['user_id']}, fetch_one=True)
        if not user:
            abort(401)  # Unauthorized - User not found
        
        user_data = dict(user._mapping)
        return create_response("success", "Token is valid", {
            "user": user_data,
            "expires_at": payload.get('exp')
        }, 200)
        
    except Exception:
        abort(500)  # Internal Server Error


@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """Refresh JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401)  # Unauthorized
    
    token = auth_header.split(' ')[1]
    payload = decode_jwt_token(token)
    
    if not payload:
        abort(401)  # Unauthorized - Invalid or expired token
    
    try:
        # Get fresh user data
        user_query = """
        SELECT u.user_id, u.username, u.email, u.user_type_id, 
               u.customer_id, u.name, ut.user_type, c.name as customer_name
        FROM user u
        JOIN user_type ut ON u.user_type_id = ut.user_type_id
        JOIN customer c ON u.customer_id = c.customer_id
        WHERE u.user_id = :user_id
        """
        
        user = execute_query(user_query, {"user_id": payload['user_id']}, fetch_one=True)
        if not user:
            abort(401)  # Unauthorized - User not found
        
        user_data = dict(user._mapping)
        
        # Generate new token
        new_token = generate_jwt_token(user_data)
        
        response_data = {
            "token": new_token,
            "expires_in": JWT_EXPIRATION_HOURS * 3600
        }
        
        return create_response("success", "Token refreshed", response_data, 200)
        
    except Exception as e:
        print(f"Token refresh error: {e}")
        abort(500)  # Internal Server Error


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """User logout endpoint"""
    # In a real implementation, you might:
    # 1. Blacklist the JWT token
    # 2. Clear server-side session
    # 3. Log the logout event
    
    return create_response("success", "Logout successful", {}, 200)
