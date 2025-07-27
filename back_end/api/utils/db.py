"""
db.py
------
Database utility file:
- Initializes SQLAlchemy engine and session factory.
- Provides execute_query() helper to run SQL statements safely.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.config.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    with engine.connect() as connection:
        result = connection.execute(text(str(query)), params or {})
        if fetch_one:
            return result.fetchone()
        elif fetch_all:
            return result.fetchall()
        else:
            connection.commit()
            return result.rowcount
