"""
config.py
----------
Defines application configuration variables:
- Database connection URL.
- Flask app settings (debug mode, secret key, host, and port).
"""

import os

# Database URL for SQLAlchemy
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+mysqlconnector://root:root@localhost:3306/ai_chatbot"
)

SECRET_KEY = 'dev-secret-key'
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000
