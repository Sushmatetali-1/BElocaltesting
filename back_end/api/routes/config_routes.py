"""
config_routes.py
-----------------
Defines API endpoints for service configuration and health checks:
- /version: Returns API version and service name.
- /health: Returns server health status.
"""

from flask import Blueprint, jsonify
from sqlalchemy import text
config_bp = Blueprint('config', __name__)

# Version endpoint
@config_bp.route("/version", methods=["GET"])
def get_version():
    return jsonify({
        "status": "success",
        "message": "API version",
        "data": {"version": "v1", "service": "User Management API"}
    })

# Health endpoint
@config_bp.route("/health", methods=["GET"])
def health():
    try:
        # Import engine inside the function (lazy import)
        from api.utils.db import engine

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return jsonify({
            "status": "success",
            "message": "API and Database are running"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 500