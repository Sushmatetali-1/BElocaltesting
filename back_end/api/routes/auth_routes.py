from flask import Blueprint, request, jsonify
from sqlalchemy import text
from api.utils.db import get_engine
from api.utils.auth_utils import hash_password, verify_password, generate_token
from api.config.config import JWT_EXPIRATION_HOURS

auth_bp = Blueprint("auth", __name__)

# Map your user_type_id values to our 3 roles.
# If your seed data differs, update this mapping once.
USER_TYPE_ID_TO_ROLE = {
    1: "admin",
    2: "config",
    3: "general",
}

@auth_bp.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Unsupported media type - use application/json"}), 415

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "email and password are required"}), 400

    with get_engine().begin() as conn:
        user = conn.execute(
            text("SELECT user_id, user_type_id, customer_id, email, password_hash FROM user WHERE email = :email AND is_active = TRUE"),
            {"email": email}
        ).mappings().first()

    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"status": "error", "message": "invalid credentials"}), 401

    role = USER_TYPE_ID_TO_ROLE.get(int(user["user_type_id"]), "general")
    token = generate_token(
        email=user["email"],
        user_id=int(user["user_id"]),
        customer_id=int(user["customer_id"]),
        user_type_id=int(user["user_type_id"]),
        role=role
    )

    return jsonify({
        "status": "success",
        "message": "login ok",
        "data": {
            "token": token,
            "expires_in_hours": JWT_EXPIRATION_HOURS,
            "role": role
        }
    }), 200

@auth_bp.route("/whoami", methods=["GET"])
def whoami():
    # DEMO-ONLY: convenience endpoint to decode token client-side.
    return jsonify({
        "status": "success",
        "message": "Use Authorization: Bearer <token> on protected routes; or ?token=<token> for demo-only GETs"
    }), 200
