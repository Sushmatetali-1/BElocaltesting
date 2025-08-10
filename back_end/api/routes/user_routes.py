"""
user_routes.py
---------------
Handles all user-related API routes:
- Create, list, update, delete, and fetch user by ID.
- Validates input and returns consistent JSON responses.
"""

from flask import Blueprint, request, jsonify, abort
from sqlalchemy import text
from api.utils.db import execute_query
from api.models.sql_queries import USER_QUERIES
import time
import jwt
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)

# Configuration (move to config.py in production)
JWT_SECRET_KEY = "your-secret-key-here"  # Change this in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Simple rate limiting storage (in production, use Redis or proper storage)
request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute
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

def check_authentication():
    """Enhanced authentication check using JWT and database verification"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        abort(401)  # Unauthorized
    
    # Check Bearer token format
    if not auth_header.startswith('Bearer '):
        abort(401)  # Unauthorized
    
    token = auth_header.split(' ')[1]
    
    # Decode JWT token
    payload = decode_jwt_token(token)
    if not payload:
        abort(401)  # Unauthorized - Invalid or expired token
    
    # Verify user still exists and is active
    user_query = "SELECT user_id, username, email, user_type_id, customer_id FROM user WHERE user_id = :user_id"
    try:
        user = execute_query(user_query, {"user_id": payload['user_id']}, fetch_one=True)
        if not user:
            abort(401)  # Unauthorized - User not found
        
        # Store user info in request context for later use
        request.current_user = dict(user._mapping)
        return True
        
    except Exception:
        abort(401)  # Unauthorized

def check_admin_permission():
    """Check if user has admin permissions"""
    if not hasattr(request, 'current_user'):
        abort(401)  # Unauthorized
    
    # Get user type
    user_type_query = "SELECT user_type FROM user_type WHERE user_type_id = :user_type_id"
    try:
        user_type = execute_query(user_type_query, {"user_type_id": request.current_user['user_type_id']}, fetch_one=True)
        if not user_type:
            abort(403)  # Forbidden
        
        user_type_name = dict(user_type._mapping)['user_type'].lower()
        
        # Only Admin and Manager types can perform admin actions
        if user_type_name not in ['admin', 'manager']:
            abort(403)  # Forbidden
            
    except Exception:
        abort(403)  # Forbidden

def check_app_access(app_id):
    """Check if user has access to specific app"""
    if not hasattr(request, 'current_user'):
        abort(401)  # Unauthorized
    
    access_query = """
    SELECT ua.user_id 
    FROM user_access ua 
    WHERE ua.user_id = :user_id AND ua.app_id = :app_id
    """
    
    try:
        access = execute_query(access_query, {
            "user_id": request.current_user['user_id'],
            "app_id": app_id
        }, fetch_one=True)
        
        if not access:
            abort(403)  # Forbidden - No access to this app
            
    except Exception:
        abort(403)  # Forbidden

def check_customer_access(customer_id):
    """Check if user belongs to the specified customer"""
    if not hasattr(request, 'current_user'):
        abort(401)  # Unauthorized
    
    if request.current_user['customer_id'] != customer_id:
        abort(403)  # Forbidden - Different customer

def create_response(status, message, data=None, code=200):
    response = {"status": status, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), code


# ---------- Authentication Endpoints ----------

@user_bp.route("/login", methods=["POST"])
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
               u.customer_id, u.name, ut.user_type, c.name as customer_name
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


@user_bp.route("/logout", methods=["POST"])
def logout():
    """User logout endpoint"""
    # Check authentication
    check_authentication()
    
    # In a real implementation, you might:
    # 1. Blacklist the JWT token
    # 2. Clear server-side session
    # 3. Log the logout event
    
    return create_response("success", "Logout successful", {}, 200)


@user_bp.route("/profile", methods=["GET"])
def get_profile():
    """Get current user profile"""
    # Apply rate limiting
    check_rate_limit(request.remote_addr)
    
    # Check authentication
    check_authentication()
    
    try:
        user_id = request.current_user['user_id']
        
        # Get detailed user info
        user_query = """
        SELECT u.user_id, u.username, u.email, u.name, u.department, u.contact_info,
               u.created_at, u.updated_at, ut.user_type, ut.description as user_type_desc,
               c.name as customer_name, c.address, c.phone
        FROM user u
        JOIN user_type ut ON u.user_type_id = ut.user_type_id
        JOIN customer c ON u.customer_id = c.customer_id
        WHERE u.user_id = :user_id
        """
        
        user = execute_query(user_query, {"user_id": user_id}, fetch_one=True)
        
        if not user:
            abort(404)  # Not Found
        
        user_data = dict(user._mapping)
        
        # Get user permissions
        permissions = get_user_permissions(user_id)
        
        response_data = {
            "user": user_data,
            "permissions": permissions
        }
        
        return create_response("success", "Profile retrieved", response_data, 200)
        
    except Exception as e:
        print(f"Profile error: {e}")
        abort(500)  # Internal Server Error


@user_bp.route("/permissions", methods=["GET"])
def get_user_permissions_endpoint():
    """Get current user's permissions"""
    # Check authentication
    check_authentication()
    
    try:
        user_id = request.current_user['user_id']
        permissions = get_user_permissions(user_id)
        
        return create_response("success", "Permissions retrieved", {"permissions": permissions}, 200)
        
    except Exception as e:
        print(f"Permissions error: {e}")
        abort(500)  # Internal Server Error


# ---------- Create User ----------
@user_bp.route("/create", methods=["POST"])
def create_user():
    # Apply rate limiting
    check_rate_limit(request.remote_addr)
    
    # Check authentication (only authenticated users can create users)
    check_authentication()
    
    # Check admin permissions (only admins/managers can create users)
    check_admin_permission()
    
    # Check Content-Type for POST requests
    if not request.is_json:
        abort(415)  # Unsupported Media Type
    
    try:
        data = request.get_json(force=True)
    except Exception:
        abort(400)  # Bad Request - Invalid JSON
    
    if not data:
        abort(400)  # Bad Request - No data provided

    required_fields = ["user_id", "user_type_id", "customer_id", "email", "username", "name", "password"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        abort(422)  # Unprocessable Entity - Missing required fields
    
    # Basic validation
    if not data.get("email") or "@" not in data["email"]:
        abort(422)  # Unprocessable Entity - Invalid email format
    
    if not data.get("username") or len(data["username"]) < 3:
        abort(422)  # Unprocessable Entity - Invalid username
    
    if not data.get("password") or len(data["password"]) < 6:
        abort(422)  # Unprocessable Entity - Password too short

    # Check if creating user for same customer (unless super admin)
    current_user_type_query = "SELECT user_type FROM user_type WHERE user_type_id = :user_type_id"
    user_type = execute_query(current_user_type_query, {"user_type_id": request.current_user['user_type_id']}, fetch_one=True)
    
    if user_type and dict(user_type._mapping)['user_type'].lower() != 'admin':
        # Non-admin users can only create users for their own customer
        check_customer_access(data["customer_id"])

    params = {
        "user_id": data["user_id"],
        "user_type_id": data["user_type_id"],
        "customer_id": data["customer_id"],
        "email": data["email"],
        "password_hash": hash_password(data["password"]),  # Hash the password
        "username": data["username"],
        "department": data.get("department"),
        "name": data["name"],
        "contact_info": data.get("contact_info")
    }

    try:
        # Check if user already exists
        existing_user = execute_query(USER_QUERIES["get_by_id"], {"user_id": data["user_id"]}, fetch_one=True)
        if existing_user:
            abort(409)  # Conflict - User already exists
        
        # Check if email/username already exists
        email_check = execute_query("SELECT user_id FROM user WHERE email = :email", {"email": data["email"]}, fetch_one=True)
        if email_check:
            abort(409)  # Conflict - Email already exists
            
        username_check = execute_query("SELECT user_id FROM user WHERE username = :username", {"username": data["username"]}, fetch_one=True)
        if username_check:
            abort(409)  # Conflict - Username already exists
        
        execute_query(USER_QUERIES["create"], params)
        created_row = execute_query(USER_QUERIES["get_by_id"], {"user_id": data["user_id"]}, fetch_one=True)
        
        if not created_row:
            abort(500)  # Internal Server Error - Creation failed
        
        # Don't return password hash in response
        user_data = dict(created_row._mapping)
        user_data.pop('password_hash', None)
            
        return create_response("success", "User created", user_data, 201)  # 201 Created
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error


# ---------- List Users ----------
@user_bp.route("/list", methods=["GET"])
def list_users():
    # Apply rate limiting
    check_rate_limit(request.remote_addr)
    
    # Check authentication
    check_authentication()
    
    try:
        rows = execute_query(USER_QUERIES["list_base"], fetch_all=True)
        users_data = [dict(row._mapping) for row in rows]
        return create_response("success", "User list retrieved", users_data, 200)  # 200 OK
    except Exception as e:
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error


# ---------- Update User ----------
@user_bp.route("/update/<int:user_id>", methods=["PUT", "PATCH"])
def update_user(user_id):
    # Validate Content-Type
    if not request.is_json:
        abort(415)  # Unsupported Media Type
    
    try:
        data = request.get_json()
    except Exception:
        abort(400)  # Bad Request - Invalid JSON
    
    if not data:
        abort(400)  # Bad Request - No data provided

    try:
        # Check if user exists
        current_row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
        if not current_row:
            abort(404)  # Not Found

        current_data = dict(current_row._mapping)
        
        # Validate updateable fields
        allowed_fields = ["email", "username", "department", "name", "contact_info"]
        fields = []
        params = {"user_id": user_id}
        
        for field in data:
            if field not in allowed_fields:
                abort(422)  # Unprocessable Entity - Invalid field
            
            # Basic validation for specific fields
            if field == "email" and data[field] and "@" not in data[field]:
                abort(422)  # Unprocessable Entity - Invalid email
            
            if field == "username" and data[field] and len(data[field]) < 3:
                abort(422)  # Unprocessable Entity - Invalid username
            
            fields.append(f"{field} = :{field}")
            params[field] = data[field]

        if not fields:
            abort(400)  # Bad Request - Nothing to update

        query = text(USER_QUERIES["update_base"].format(fields=", ".join(fields)))
        execute_query(query, params)

        updated_row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
        updated_data = dict(updated_row._mapping)

        # Find changed columns and return only those
        changes = {}
        for key, old_value in current_data.items():
            new_value = updated_data.get(key)
            if old_value != new_value:
                changes[key] = new_value

        return create_response("success", "User updated successfully", changes, 200)  # 200 OK
        
    except Exception as e:
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error


# ---------- Get Update History ----------
@user_bp.route("/update/<int:user_id>", methods=["GET"])
def get_update_history(user_id):
    try:
        # Get the record
        row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
        if not row:
            abort(404)  # Not Found

        user_data = dict(row._mapping)

        # Return only the columns that changed since last update
        updated_columns = {}

        # Only return the fields that can be updated by the user
        for col in ["department", "name", "email", "username", "contact_info"]:
            if user_data["updated_at"] != user_data["created_at"]:
                updated_columns[col] = user_data[col]

        # If no updated columns
        if not updated_columns:
            return create_response("success", "No recently updated columns", {}, 200)  # 200 OK

        return create_response("success", "Recently updated column(s)", updated_columns, 200)  # 200 OK
        
    except Exception as e:
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error

# ---------- Delete User ----------
@user_bp.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # Apply rate limiting
    check_rate_limit(request.remote_addr)
    
    # Check authentication
    check_authentication()
    
    # Check admin permissions (only admins can delete users)
    check_admin_permission()
    
    try:
        # Check if user exists first
        existing_user = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
        if not existing_user:
            abort(404)  # Not Found
        
        rows_deleted = execute_query(USER_QUERIES["delete"], {"user_id": user_id})
        
        if rows_deleted == 0:
            abort(500)  # Internal Server Error - Delete failed
        
        # Return 204 No Content for successful deletion
        return '', 204
        
    except Exception as e:
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error


# ---------- Get User by ID ----------
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    # Apply rate limiting
    check_rate_limit(request.remote_addr)
    
    # Check authentication
    check_authentication()
    
    try:
        row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
        if not row:
            abort(404)  # Not Found

        return create_response("success", "User data retrieved", dict(row._mapping), 200)  # 200 OK
        
    except Exception as e:
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error


# ---------- Health Check Endpoint ----------
@user_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint that can demonstrate 502/503 errors"""
    try:
        # Try to connect to database
        test_query = "SELECT 1"
        execute_query(test_query, fetch_one=True)
        
        # Check if external services are available (simulated)
        external_service_status = check_external_services()
        
        if not external_service_status:
            abort(502)  # Bad Gateway - External service unavailable
        
        return create_response("success", "Service is healthy", {"status": "healthy"}, 200)
        
    except Exception as e:
        print(f"Health check failed: {e}")
        # If database is down, return 503 Service Unavailable
        abort(503)  # Service Unavailable


def check_external_services():
    """Simulate checking external services (email, payment gateway, etc.)"""
    # In real implementation, this would check actual external services
    # For demo purposes, return True
    # You could simulate failures by returning False
    return True


# ---------- Admin Only Endpoint (Demonstrates 403) ----------
@user_bp.route("/admin/stats", methods=["GET"])
def get_admin_stats():
    """Admin-only endpoint to demonstrate 403 Forbidden"""
    # Check authentication first
    check_authentication()
    
    # Check admin permissions
    check_admin_permission()  # This will abort(403) if not admin
    
    try:
        # Get user statistics (admin only)
        total_users = execute_query("SELECT COUNT(*) as count FROM users", fetch_one=True)
        stats = {
            "total_users": dict(total_users._mapping)["count"] if total_users else 0,
            "endpoint_access": "admin_only"
        }
        
        return create_response("success", "Admin statistics", stats, 200)
        
    except Exception as e:
        print(f"Database error: {e}")
        abort(500)  # Internal Server Error
