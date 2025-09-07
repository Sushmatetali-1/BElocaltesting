# """
# db.py
# ------
# SQLAlchemy engine + a tiny query helper.
# """
#
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from api.config.config import DATABASE_URL
#
# # Tweak pooling for local dev; keep pre_ping on so dead connections are recycled
# engine = create_engine(
#     DATABASE_URL,
#     echo=False,
#     pool_pre_ping=True,
#     pool_recycle=1800,   # 30 min
# )
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# def execute_query(query, params=None, fetch_one=False, fetch_all=False):
#     """
#     Executes raw SQL safely with bound params.
#     - When neither fetch_* is set, it commits and returns rowcount.
#     - When fetching, returns the row(s) without committing (SELECT).
#     """
#     with engine.connect() as connection:
#         result = connection.execute(text(str(query)), params or {})
#         if fetch_one:
#             return result.fetchone()
#         if fetch_all:
#             return result.fetchall()
#         connection.commit()
#         return result.rowcount

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.config.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

def get_engine():
    return engine

def get_session():
    return SessionLocal()
