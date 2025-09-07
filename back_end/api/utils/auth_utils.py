import hashlib
import datetime as dt
from functools import wraps
from flask import request, jsonify, g
import jwt

from api.config.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

# ---- Password helpers ----
def hash_password(plain: str) -> str:
    if plain is None:
        return None
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

# ---- Token helpers ----
def generate_token(*, email, user_id, customer_id, user_type_id, role: str):
    exp = dt.datetime.utcnow() + dt.timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": email,
        "uid": user_id,
        "cid": customer_id,
        "utid": user_type_id,
        "role": role,  # 'admin' | 'config' | 'general'
        "exp": exp
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def _get_token_from_request():
    # Standard: Authorization: Bearer <token>
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()

    # DEMO-ONLY: allow token in query string so you can show it in the browser.
    # Remove this block when FE is connected.
    token = request.args.get("token")
    if token:
        return token
    return None

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

def require_auth(roles=None):
    """
    Usage:
        @require_auth()                     -> any authenticated user
        @require_auth(roles=['admin'])      -> only admin
        @require_auth(roles=['admin','config'])
    """
    roles = set(roles or [])

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _get_token_from_request()
            if not token:
                return jsonify({"status": "error", "message": "Unauthorized - authentication required"}), 401
            try:
                claims = decode_token(token)
            except Exception:
                return jsonify({"status": "error", "message": "Invalid or expired token"}), 401

            g.user = {
                "email": claims.get("sub"),
                "user_id": claims.get("uid"),
                "customer_id": claims.get("cid"),
                "user_type_id": claims.get("utid"),
                "role": claims.get("role"),
            }

            if roles and g.user["role"] not in roles:
                return jsonify({"status": "error", "message": "Forbidden - insufficient role"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_self_or_roles(self_email_kw: str, allowed_roles=None):
    """
    Allow if the path/email in kwargs matches current user email,
    otherwise require one of allowed_roles.
    """
    allowed_roles = set(allowed_roles or [])
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _get_token_from_request()
            if not token:
                return jsonify({"status": "error", "message": "Unauthorized - authentication required"}), 401
            try:
                claims = decode_token(token)
            except Exception:
                return jsonify({"status": "error", "message": "Invalid or expired token"}), 401

            g.user = {
                "email": claims.get("sub"),
                "user_id": claims.get("uid"),
                "customer_id": claims.get("cid"),
                "user_type_id": claims.get("utid"),
                "role": claims.get("role"),
            }

            target_email = kwargs.get(self_email_kw)
            if target_email and target_email.lower() == g.user["email"].lower():
                return fn(*args, **kwargs)

            if allowed_roles and g.user["role"] not in allowed_roles:
                return jsonify({"status": "error", "message": "Forbidden - insufficient role"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
