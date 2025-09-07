"""
config.py
----------
App and DB configuration.
"""
import os

# --------------------------------------------------------------------
# Database
# --------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+mysqlconnector://root:root@localhost:3306/ai_chatbot"
)

# --------------------------------------------------------------------
# Flask / JWT
# --------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")        # CHANGE in prod
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Optional: mount point (ensure app registers blueprints with this)
API_PREFIX = os.getenv("API_PREFIX", "/db/v1/api")

# --------------------------------------------------------------------
# Okta (optional; used later if you switch to OIDC access tokens)
# --------------------------------------------------------------------
# OKTA_ISSUER = os.getenv("OKTA_ISSUER")          # e.g. https://dev-xxxx.okta.com/oauth2/default
# OKTA_AUDIENCE = os.getenv("OKTA_AUDIENCE", "api://default")
# OKTA_JWKS_URL = f"{OKTA_ISSUER}/v1/keys" if OKTA_ISSUER else None
