# Required to prevent writing .pyc files
import sys
sys.dont_write_bytecode = True

from flask import Flask, jsonify
from flask_cors import CORS
import jwt
from api.config.config import DEBUG, HOST, PORT
from api.routes.user_routes import user_bp
from api.routes.config_routes import config_bp
from api.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)

    # Register Blueprints - Temporarily disabled for testing without database
    app.register_blueprint(auth_bp, url_prefix="/db/v1/api/auth")
    app.register_blueprint(user_bp, url_prefix="/db/v1/api/user")
    app.register_blueprint(config_bp, url_prefix="/db/v1/api")

    @app.route("/")
    def home():
        return jsonify({
            "status": "success",
            "message": "User Management API",
            "data": {
                "api_version": "v1",
                "endpoints": {
                    "auth": "/db/v1/api/auth/*",
                    "user": "/db/v1/api/user/*",
                    "config": "/db/v1/api/*"
                }
            }
        }), 200

    # ---- Error handlers ----
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

    @app.errorhandler(415)
    def unsupported_media_type(e):
        return jsonify({'status': 'error', 'message': 'Unsupported media type - use application/json'}), 415

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({'status': 'error', 'message': 'Unprocessable entity - validation errors'}), 422

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({'status': 'error', 'message': 'Too many requests - rate limit exceeded'}), 429

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

if __name__ == "__main__":
    app = create_app()
    app.run(debug=DEBUG, host=HOST, port=PORT)
