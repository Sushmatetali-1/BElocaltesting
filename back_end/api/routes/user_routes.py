"""
user_routes.py
---------------
Handles all user-related API routes:
- Create, list, update, delete, and fetch user by ID.
- Validates input and returns consistent JSON responses.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import text
from api.utils.db import execute_query
from api.models.sql_queries import USER_QUERIES

user_bp = Blueprint('user', __name__)

def create_response(status, message, data=None, code=200):
    response = {"status": status, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), code


# ---------- Create User ----------
@user_bp.route("/create", methods=["GET", "POST"])
def create_user():
    if request.method == "GET":
        data = request.args
    else:
        data = request.get_json(force=True)

    required_fields = ["user_id", "user_type_id", "customer_id", "email", "username", "name"]
    for field in required_fields:
        if field not in data:
            return create_response("error", f"{field} required", None, 400)

    params = {
        "user_id": data["user_id"],
        "user_type_id": data["user_type_id"],
        "customer_id": data["customer_id"],
        "email": data["email"],
        "password_hash": data.get("password", ""),
        "username": data["username"],
        "department": data.get("department"),
        "name": data["name"],
        "contact_info": data.get("contact_info")
    }

    execute_query(USER_QUERIES["create"], params)
    created_row = execute_query(USER_QUERIES["get_by_id"], {"user_id": data["user_id"]}, fetch_one=True)
    return create_response("success", "User created", dict(created_row._mapping))


# ---------- List Users ----------
@user_bp.route("/list", methods=["GET"])
def list_users():
    rows = execute_query(USER_QUERIES["list_base"], fetch_all=True)
    return create_response("success", "User list", [dict(row._mapping) for row in rows])


# ---------- Update User ----------
@user_bp.route("/update/<int:user_id>", methods=["GET", "PUT", "PATCH"])
def update_user(user_id):
    # Handle GET: return only the column(s) that changed
    if request.method == "GET":
        # Get the record
        row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
        if not row:
            return create_response("error", f"User {user_id} not found", None, 404)

        user_data = dict(row._mapping)

        # Return only the columns that changed since last update
        # (this assumes that updated_at != created_at means data changed)
        updated_columns = {}

        # Only return the fields that can be updated by the user
        for col in ["department", "name", "email", "username", "contact_info"]:
            if user_data["updated_at"] != user_data["created_at"]:
                # Return ONLY the last updated column's current value
                updated_columns[col] = user_data[col]

        # If no updated columns
        if not updated_columns:
            return create_response("success", "No recently updated columns", {})

        # Return only the last updated column
        # This gets the last column in updated_columns (latest changed one)
        # If multiple columns changed at the same time, it will show all
        return create_response("success", "Recently updated column(s)", updated_columns)

    # PUT/PATCH = update logic
    if not request.is_json:
        return create_response("error", "Content-Type must be application/json", None, 415)

    data = request.get_json()

    current_row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
    if not current_row:
        return create_response("error", "User not found", None, 404)

    current_data = dict(current_row._mapping)
    fields = []
    params = {"user_id": user_id}
    for field in ["email", "username", "department", "name", "contact_info"]:
        if field in data:
            fields.append(f"{field} = :{field}")
            params[field] = data[field]

    if not fields:
        return create_response("error", "Nothing to update", None, 400)

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

    return create_response("success", "Updated column(s)", changes)

# ---------- Delete User ----------
@user_bp.route("/delete/<int:user_id>", methods=["GET", "DELETE"])
def delete_user(user_id):
    rows_deleted = execute_query(USER_QUERIES["delete"], {"user_id": user_id})
    if rows_deleted == 0:
        return create_response("error", f"User {user_id} not found", None, 404)

    return create_response("success", f"User {user_id} deleted", {"user_id": user_id})


# ---------- Get User by ID ----------
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    row = execute_query(USER_QUERIES["get_by_id"], {"user_id": user_id}, fetch_one=True)
    if not row:
        return create_response("error", f"User {user_id} not found or deleted", None, 404)

    return create_response("success", "User data", dict(row._mapping))
