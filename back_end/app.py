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

from flask import Flask, jsonify, request
from flask_cors import CORS

from api.routes.user_routes import user_bp
from api.routes.config_routes import config_bp
# from api.routes.auth_routes import auth_bp  # Temporarily commented out

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register Blueprints
    # app.register_blueprint(auth_bp, url_prefix="/db/v1/api/auth")  # Temporarily commented out
    app.register_blueprint(user_bp, url_prefix="/db/v1/api/user")
    app.register_blueprint(config_bp, url_prefix="/db/v1/api")

    # Simple test endpoint to demonstrate tokens
    @app.route('/test/hello', methods=['GET'])
    def hello():
        return jsonify({
            "status": "success", 
            "message": "Server is running!", 
            "data": {"server": "Flask", "version": "1.0"}
        }), 200
    
    # Simple login test (without database)
    @app.route('/test/login', methods=['POST'])
    def test_login():
        data = request.get_json() if request.is_json else {}
        
        # Simple test credentials
        if data.get('username') == 'test' and data.get('password') == 'test123':
            # Create a simple token (not real JWT for now)
            fake_token = "test-token-abc123xyz"
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "token": fake_token,
                    "user": {"username": "test", "role": "admin"},
                    "expires_in": 3600
                }
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid credentials"
            }), 401

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
