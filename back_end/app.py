"""
app.py
-------
Entry point for the Flask application.
- Initializes Flask app with CORS support.
- Registers API blueprints for user management and configuration endpoints.
- Handles global error responses for 404, 405, and 500.
"""

# Required to prevent writing .pyc files
import sys
sys.dont_write_bytecode = True

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import jwt
import hashlib
from datetime import datetime, timedelta

# Mock the database routes temporarily
# from api.routes.user_routes import user_bp
# from api.routes.config_routes import config_bp
# from api.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)

    # Register Blueprints - Temporarily disabled for testing without database
    # app.register_blueprint(auth_bp, url_prefix="/db/v1/api/auth")
    # app.register_blueprint(user_bp, url_prefix="/db/v1/api/user")
    # app.register_blueprint(config_bp, url_prefix="/db/v1/api")

    # Configuration
    JWT_SECRET_KEY = "your-secret-key-here"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

    # Mock users for testing - Only two user types: Admin (1) and Regular User (2)
    MOCK_USERS = {
        "test": {
            "password": "test123",
            "user_id": 1000,
            "username": "test",
            "email": "test@example.com",
            "name": "Test User",
            "user_type_id": 2,  # Regular user
            "customer_id": 1000
        },
        "acmeadmin": {
            "password": "password123",
            "user_id": 2001,
            "username": "acmeadmin",
            "email": "alice.admin@acme.com",
            "name": "Alice Admin",
            "user_type_id": 1,  # Admin - full privileges
            "customer_id": 1001
        },
        "globexmgr": {
            "password": "password123",
            "user_id": 2002,
            "username": "globexmgr",
            "email": "bob.manager@globex.com",
            "name": "Bob Manager",
            "user_type_id": 2,  # Regular user - limited privileges
            "customer_id": 1002
        }
    }

    def verify_password(password, stored_password):
        """Verify password - for testing, compare directly"""
        return password == stored_password

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
            return None
        except jwt.InvalidTokenError:
            return None

    def create_response(status, message, data=None, status_code=200):
        """Create standardized response"""
        response = {
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if data is not None:
            response["data"] = data
        return jsonify(response), status_code

    def get_user_permissions(user_type_id):
        """Get user permissions: Admin and Regular User"""
        if user_type_id == 1:  # Admin
            return {
                "access_level": "admin",
                "allowed_operations": ["create", "read", "update", "delete", "list", "search", "manage"],
                "description": "Full system access with all privileges"
            }
        else:  # All other user types become regular users (type_id 2)
            return {
                "access_level": "user", 
                "allowed_operations": ["list", "search", "login", "logout"],
                "description": "Limited access - can only view and search users"
            }

    # Additional helper functions needed for authentication routes
    def generate_token(user):
        """Generate JWT token for user"""
        payload = {
            'user_id': user['user_id'],
            'username': user['username'],
            'user_type_id': user['user_type_id'],
            'customer_id': user.get('customer_id', 0),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def verify_token(token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def extract_token_from_request(request):
        """Extract JWT token from request headers"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def hash_password(password):
        """Hash password (simplified for mock)"""
        # In production, use proper password hashing like bcrypt
        # For mock, we'll just return the password as is
        return password

    def check_authentication():
        """Check JWT token authentication"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)
        return payload

    # Serve the UI at new endpoint
    @app.route('/api_test.html')
    def serve_ui():
        """Serve the API testing UI"""
        return send_from_directory('static', 'index.html')

    @app.route('/ui')
    def serve_ui_alt():
        """Alternative route for UI"""
        return send_from_directory('static', 'index.html')

    @app.route('/api_testing')
    def serve_api_testing():
        """Serve the comprehensive API testing dashboard"""
        return send_from_directory('static', 'index.html')

    @app.route('/')
    def home():
        """Home endpoint with API information"""
        return jsonify({
            "status": "success",
            "message": "Flask Authentication API Server",
            "data": {
                "server": "Flask",
                "version": "1.0",
                "api_version": "v1",
                "endpoints": {
                    "ui": "/ui",
                    "api_testing": "/api_testing",
                    "health": "/test/hello",
                    "simple_login": "/test/login",
                    "db_login": "/db/v1/api/auth/login",
                    "user_endpoints": "/db/v1/api/user/*"
                },
                "test_credentials": {
                    "simple": {"username": "test", "password": "test123"},
                    "admin": {"username": "acmeadmin", "password": "password123", "privileges": "Full access - create, update, delete users"},
                    "user": {"username": "globexmgr", "password": "password123", "privileges": "Limited access - list and search users only"}
                },
                "user_types": {
                    "1": "Admin - Full system privileges",
                    "2": "Regular User - Limited privileges (list, search, login, logout only)"
                }
            }
        })

    # Simple test endpoints
    @app.route('/test/hello', methods=['GET'])
    def hello():
        return create_response("success", "Server is running!", {"server": "Flask", "version": "1.0"})

    @app.route('/test/login', methods=['POST'])
    def test_login():
        data = request.get_json() if request.is_json else {}
        
        if data.get('username') == 'test' and data.get('password') == 'test123':
            fake_token = "test-token-abc123xyz"
            return create_response("success", "Login successful", {
                "token": fake_token,
                "user": {"username": "test", "role": "test"},
                "expires_in": 3600
            })
        else:
            return create_response("error", "Invalid credentials", None, 401)

    @app.route('/test/logout', methods=['POST'])
    def test_logout():
        return create_response("success", "Logout successful", {})

    # Database authentication routes (mock implementation)
    @app.route('/db/v1/api/auth/login', methods=['POST'])
    def db_auth_login():
        """Database authentication login endpoint"""
        data = request.get_json() if request.is_json else {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return create_response("error", "Username and password are required", None, 400)
        
        # Check against mock users
        user = MOCK_USERS.get(username)
        if not user:
            return create_response("error", "Invalid credentials", None, 401)
            
        # Verify password (simplified for mock - passwords stored in plain text)
        if password != user['password']:
            return create_response("error", "Invalid credentials", None, 401)
        
        # Generate JWT token
        token = generate_token(user)
        
        return create_response("success", "Login successful", {
            "token": token,
            "user": {
                "id": user['user_id'],
                "username": user['username'],
                "user_type_id": user['user_type_id'],
                "role": "Admin" if user['user_type_id'] == 1 else "User",
                "permissions": get_user_permissions(user['user_type_id'])
            },
            "expires_in": 86400  # 24 hours
        })

    @app.route('/db/v1/api/auth/validate', methods=['POST'])
    def db_auth_validate():
        """Validate JWT token"""
        token = extract_token_from_request(request)
        if not token:
            return create_response("error", "No token provided", None, 401)
        
        payload = verify_token(token)
        if not payload:
            return create_response("error", "Invalid or expired token", None, 401)
        
        return create_response("success", "Token is valid", {
            "user": {
                "id": payload['user_id'],
                "username": payload['username'],
                "user_type_id": payload['user_type_id'],
                "role": "Admin" if payload['user_type_id'] == 1 else "User"
            }
        })

    @app.route('/db/v1/api/auth/logout', methods=['POST'])
    def db_auth_logout():
        """Logout endpoint (JWT is stateless, so this is mainly for UI)"""
        return create_response("success", "Logout successful", {})

    # User management routes
    @app.route('/db/v1/api/user/list', methods=['GET'])
    def user_list():
        """List all users (available to all authenticated users)"""
        token = extract_token_from_request(request)
        if not token:
            return create_response("error", "Authentication required", None, 401)
        
        payload = verify_token(token)
        if not payload:
            return create_response("error", "Invalid or expired token", None, 401)
        
        # Return list of users (without passwords)
        users_list = []
        for username, user in MOCK_USERS.items():
            users_list.append({
                "id": user['user_id'],
                "username": user['username'],
                "user_type_id": user['user_type_id'],
                "role": "Admin" if user['user_type_id'] == 1 else "User",
                "email": user.get('email', ''),
                "name": user.get('name', ''),
                "created_at": "2024-01-01T00:00:00Z"
            })
        
        return create_response("success", "Users retrieved successfully", {
            "users": users_list,
            "total": len(users_list)
        })

    @app.route('/db/v1/api/user/search', methods=['GET'])
    def user_search():
        """Search users (available to all authenticated users)"""
        token = extract_token_from_request(request)
        if not token:
            return create_response("error", "Authentication required", None, 401)
        
        payload = verify_token(token)
        if not payload:
            return create_response("error", "Invalid or expired token", None, 401)
        
        search_term = request.args.get('q', '').lower()
        
        # Filter users based on search term
        filtered_users = []
        for username, user in MOCK_USERS.items():
            if search_term in username.lower():
                filtered_users.append({
                    "id": user['user_id'],
                    "username": user['username'],
                    "user_type_id": user['user_type_id'],
                    "role": "Admin" if user['user_type_id'] == 1 else "User",
                    "email": user.get('email', ''),
                    "name": user.get('name', '')
                })
        
        return create_response("success", "Search completed", {
            "users": filtered_users,
            "total": len(filtered_users),
            "search_term": search_term
        })

    @app.route('/db/v1/api/user/create', methods=['POST'])
    def user_create():
        """Create new user (Admin only)"""
        token = extract_token_from_request(request)
        if not token:
            return create_response("error", "Authentication required", None, 401)
        
        payload = verify_token(token)
        if not payload:
            return create_response("error", "Invalid or expired token", None, 401)
        
        # Check if user is admin
        if payload['user_type_id'] != 1:
            return create_response("error", "Admin access required", None, 403)
        
        data = request.get_json() if request.is_json else {}
        new_username = data.get('username', '').strip()
        new_password = data.get('password', '').strip()
        user_type_id = data.get('user_type_id', 2)  # Default to regular user (type 2)
        
        if not new_username or not new_password:
            return create_response("error", "Username and password are required", None, 400)
        
        # Validate user_type_id - only allow 1 (Admin) or 2 (Regular User)
        if user_type_id not in [1, 2]:
            return create_response("error", "Invalid user_type_id. Must be 1 (Admin) or 2 (Regular User)", None, 400)
        
        if new_username in MOCK_USERS:
            return create_response("error", "Username already exists", None, 409)
        
        # Create new user
        new_user_id = max([user['user_id'] for user in MOCK_USERS.values()]) + 1
        MOCK_USERS[new_username] = {
            'user_id': new_user_id,
            'username': new_username,
            'password': new_password,
            'user_type_id': user_type_id,
            'email': f"{new_username}@example.com",
            'name': new_username.title(),
            'customer_id': 1000
        }
        
        return create_response("success", "User created successfully", {
            "user": {
                "id": new_user_id,
                "username": new_username,
                "user_type_id": user_type_id,
                "role": "Admin" if user_type_id == 1 else "User"
            }
        })

    @app.route('/db/v1/api/user/update', methods=['PUT'])
    def user_update():
        """Update user (Admin only)"""
        token = extract_token_from_request(request)
        if not token:
            return create_response("error", "Authentication required", None, 401)
        
        payload = verify_token(token)
        if not payload:
            return create_response("error", "Invalid or expired token", None, 401)
        
        # Check if user is admin
        if payload['user_type_id'] != 1:
            return create_response("error", "Admin access required", None, 403)
        
        return create_response("success", "User update functionality not implemented in mock", {})

    @app.route('/db/v1/api/user/delete', methods=['DELETE'])
    def user_delete():
        """Delete user (Admin only)"""
        token = extract_token_from_request(request)
        if not token:
            return create_response("error", "Authentication required", None, 401)
        
        payload = verify_token(token)
        if not payload:
            return create_response("error", "Invalid or expired token", None, 401)
        
        # Check if user is admin
        if payload['user_type_id'] != 1:
            return create_response("error", "Admin access required", None, 403)
        
        return create_response("success", "User delete functionality not implemented in mock", {})

    # Debug endpoint to test login functionality
    @app.route('/debug/login', methods=['POST'])
    def debug_login():
        """Debug login endpoint to troubleshoot issues"""
        data = request.get_json() if request.is_json else {}
        
        return jsonify({
            "status": "debug",
            "message": "Debug login endpoint",
            "data": {
                "received_data": data,
                "content_type": request.content_type,
                "method": request.method,
                "headers": dict(request.headers),
                "username_received": data.get('username', 'NOT_PROVIDED'),
                "password_length": len(data.get('password', '')) if data.get('password') else 0
            }
        }), 200

    # Client Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'status': 'error', 'message': 'Bad request - validation errors'}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'status': 'error', 'message': 'Unauthorized - authentication required'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'status': 'error', 'message': 'Forbidden - not allowed'}), 403
 
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({'status': 'error', 'message': 'Conflict - duplicate resources'}), 409

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({'status': 'error', 'message': 'Unprocessable entity - validation errors'}), 422

    @app.errorhandler(415)
    def unsupported_media_type(e):
        return jsonify({'status': 'error', 'message': 'Unsupported media type - use application/json'}), 415

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({'status': 'error', 'message': 'Too many requests - rate limit exceeded'}), 429

    # Server Error Handlers
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    @app.errorhandler(502)
    def bad_gateway(e):
        return jsonify({'status': 'error', 'message': 'Bad gateway - upstream issues'}), 502

    @app.errorhandler(503)
    def service_unavailable(e):
        return jsonify({'status': 'error', 'message': 'Service unavailable - maintenance'}), 503

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
