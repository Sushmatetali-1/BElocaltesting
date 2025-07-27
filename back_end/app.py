"""
app.py
-------
Entry point for the Flask application.
- Initializes Flask app with CORS support.
- Registers API blueprints for user management and configuration endpoints.
- Handles global error responses for 404, 405, and 500.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from api.routes.user_routes import user_bp
from api.routes.config_routes import config_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(user_bp, url_prefix="/db/v1/api/user")
    app.register_blueprint(config_bp, url_prefix="/db/v1/api")

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
