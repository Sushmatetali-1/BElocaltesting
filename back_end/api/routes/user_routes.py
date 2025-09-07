from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from api.utils.db import get_engine
from api.utils.auth_utils import require_auth, require_self_or_roles, hash_password
from api.models.sql_queries import USER_QUERIES

user_bp = Blueprint("user", __name__)

# ---------------------------
# Helpers / validation
# ---------------------------
def _only_allowed_fields(payload, allowed):
    return {k: v for k, v in payload.items() if k in allowed and v is not None}

def _build_update_sql_and_params(base_sql, fields: dict, email: str):
    parts = []
    params = {}
    for k, v in fields.items():
        parts.append(f"{k} = :{k}")
        params[k] = v
    if not parts:
        return None, None
    sql = base_sql.format(fields=", ".join(parts))
    params["email"] = email
    return sql, params

# ---------------------------
# CREATE
# ---------------------------
@user_bp.route("/create", methods=["POST"])
@require_auth(roles=["admin", "config"])
def create_user():
    """
    Required fields:
      user_id, user_type_id, customer_id, email, username, name, password
    Optional:
      department, contact_info
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Unsupported media type - use application/json"}), 415

    body = request.get_json(silent=True) or {}
    required = ["user_id", "user_type_id", "customer_id", "email", "username", "name", "password"]
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"status": "error", "message": f"Missing required: {', '.join(missing)}"}), 422

    # Enforce same customer scope
    creator_cid = int(g.user["customer_id"])
    target_cid = int(body["customer_id"])
    if creator_cid != target_cid:
        return jsonify({"status": "error", "message": "Forbidden - cross-customer create not allowed"}), 403

    email = body["email"].strip().lower()
    username = body["username"].strip()
    password_hash = hash_password(body["password"])

    with get_engine().begin() as conn:
        # unique checks
        exists_email = conn.execute(text(USER_QUERIES["email_exists"]), {"email": email}).first()
        if exists_email:
            return jsonify({"status": "error", "message": "Email already exists"}), 409

        exists_username = conn.execute(text(USER_QUERIES["username_exists"]), {"username": username}).first()
        if exists_username:
            return jsonify({"status": "error", "message": "Username already exists"}), 409

        # user_type must exist
        ut_exists = conn.execute(text(USER_QUERIES["user_type_exists"]), {"user_type_id": int(body["user_type_id"])}).first()
        if not ut_exists:
            return jsonify({"status": "error", "message": "user_type_id does not exist"}), 422

        conn.execute(
            text(USER_QUERIES["create_user"]),
            {
                "user_id": int(body["user_id"]),
                "user_type_id": int(body["user_type_id"]),
                "customer_id": target_cid,
                "email": email,
                "password_hash": password_hash,
                "username": username,
                "department": body.get("department"),
                "name": body["name"],
                "contact_info": body.get("contact_info"),
            }
        )

    return jsonify({
        "status": "success",
        "message": "user created",
        "data": {"email": email}
    }), 201

# ---------------------------
# UPDATE
# ---------------------------
@user_bp.route("/update/<path:email>", methods=["PUT"])
@require_self_or_roles("email", allowed_roles=["admin", "config"])
def update_user(email):
    """
    Admin/Config can update any user fields except primary keys.
    General users can update only themselves and only:
        username, name, department, contact_info, password (hash), new_email
    To change email, pass { "new_email": "..." }
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Unsupported media type - use application/json"}), 415

    email = email.strip().lower()
    body = request.get_json(silent=True) or {}

    # Which fields are allowed?
    role = g.user["role"]
    allowed_fields_admin = {"username", "name", "department", "contact_info", "password_hash", "user_type_id", "customer_id"}
    allowed_fields_general = {"username", "name", "department", "contact_info", "password_hash"}

    fields = {}

    # Convert plain password -> password_hash if provided
    if body.get("password"):
        fields["password_hash"] = hash_password(body["password"])

    for key in ["username", "name", "department", "contact_info", "user_type_id", "customer_id"]:
        if key in body:
            fields[key] = body[key]

    # Apply role-based filter
    if role in ("admin", "config"):
        fields = _only_allowed_fields(fields, allowed_fields_admin)
    else:
        # general user: must be self; decorator already allows self or admin/config
        fields = _only_allowed_fields(fields, allowed_fields_general)

    if not fields and not body.get("new_email"):
        return jsonify({"status": "error", "message": "No updatable fields supplied"}), 422

    with get_engine().begin() as conn:
        # Scope to same customer for non-admin/config update to others (handled by decorator), but
        # also protect cross-customer when admin/config explicitly set customer_id
        if role in ("admin", "config"):
            # enforce same customer by default
            if "customer_id" in fields and int(fields["customer_id"]) != int(g.user["customer_id"]):
                return jsonify({"status": "error", "message": "Cross-customer reassignment not allowed"}), 403

        # do main update
        if fields:
            sql, params = _build_update_sql_and_params(USER_QUERIES["update_by_email_base"], fields, email)
            if not sql:
                return jsonify({"status": "error", "message": "No valid fields to update"}), 422
            conn.execute(text(sql), params)

        # email change (optional)
        if body.get("new_email"):
            new_email = body["new_email"].strip().lower()
            # uniqueness
            exists_email = conn.execute(text(USER_QUERIES["email_exists"]), {"email": new_email}).first()
            if exists_email:
                return jsonify({"status": "error", "message": "new_email already exists"}), 409
            conn.execute(text(USER_QUERIES["update_by_email_base"].format(fields="email = :new_email")),
                         {"new_email": new_email, "email": email})
            email = new_email

    return jsonify({"status": "success", "message": "user updated", "data": {"email": email}}), 200

# ---------------------------
# DELETE
# ---------------------------
@user_bp.route("/delete/<path:email>", methods=["DELETE"])
@require_auth(roles=["admin", "config"])
def delete_user(email):
    """
    DIRECT delete: remove the row from `user` by email, scoped to caller's customer.
    TEMP: direct hard-delete only (removed soft-delete & ?hard). Delete this block when FE is wired.
    """
    email = (email or "").strip().lower()
    if not email:
        return jsonify({"status": "error", "message": "email required"}), 400

    with get_engine().begin() as conn:
        result = conn.execute(
            text(USER_QUERIES["hard_delete_by_email_scoped"]),
            {"email": email, "customer_id": int(g.user["customer_id"])}
        )
        # MySQL+SQLAlchemy returns the affected rows count here
        if result.rowcount == 0:
            return jsonify({"status": "error", "message": "Not found in your customer scope"}), 404

    # 200 with echo, or 204 if you prefer no body
    return jsonify({"status": "success", "message": "user deleted", "data": {"email": email}}), 200
# ---------------------------
# GET one
# ---------------------------
@user_bp.route("/<path:email>", methods=["GET"])
@require_auth()  # any logged in user
def get_user(email):
    email = email.strip().lower()
    with get_engine().begin() as conn:
        row = conn.execute(text(USER_QUERIES["get_by_email_scoped"]),
                           {"email": email, "customer_id": int(g.user["customer_id"])}).mappings().first()
        if not row:
            return jsonify({"status": "error", "message": "not found"}), 404

        row = dict(row)
        return jsonify({"status": "success", "data": row}), 200

# ---------------------------
# LIST
# ---------------------------
@user_bp.route("/list", methods=["GET"])
@require_auth()  # all roles can list (scoped)
def list_users():
    with get_engine().begin() as conn:
        data = conn.execute(text(USER_QUERIES["list_active_by_customer"]),
                            {"customer_id": int(g.user["customer_id"])}).mappings().all()
        return jsonify({"status": "success", "data": [dict(r) for r in data]}), 200

# ---------------------------
# SEARCH
# ---------------------------
@user_bp.route("/search", methods=["GET"])
@require_auth()  # all roles can search (scoped)
def search_users():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"status": "error", "message": "q is required"}), 400

    like = f"%{q}%"
    with get_engine().begin() as conn:
        rows = conn.execute(
            text(USER_QUERIES["search_by_customer"]),
            {"query": like, "customer_id": int(g.user["customer_id"])}
        ).mappings().all()

    if not rows:
        # Return a clear message when no rows were found
        # (If you prefer 200 instead of 404, change the status code below to 200)
        return jsonify({
            "status": "error",
            "message": f"No user found matching '{q}'. "
                       "Check the email, username, or name and try again."
        }), 404

    # Normal success case
    return jsonify({
        "status": "success",
        "total": len(rows),
        "data": [dict(r) for r in rows]
    }), 200

