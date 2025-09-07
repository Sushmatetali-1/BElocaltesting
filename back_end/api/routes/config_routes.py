from flask import Blueprint, jsonify
from sqlalchemy import text
from api.utils.db import get_engine

config_bp = Blueprint("config", __name__)

@config_bp.route("/version", methods=["GET"])
def get_version():
    return jsonify({
        "status": "success",
        "message": "API version",
        "data": {"version": "v1", "service": "User Management API"}
    }), 200

@config_bp.route("/health", methods=["GET"])
def health():
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "success", "message": "API and Database are running"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database connection failed: {str(e)}"}), 500
