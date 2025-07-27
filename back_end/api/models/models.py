"""
models.py
----------
Defines database schema using SQLAlchemy ORM:
- User, UserType, and UserAccess tables with relationships.
- Each class represents a table structure and constraints.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# User table
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    user_type_id = Column(Integer, ForeignKey("user_type.user_type_id"), nullable=False)
    customer_id = Column(Integer, nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255))
    username = Column(String(100), nullable=False)
    department = Column(String(100))
    name = Column(String(255), nullable=False)
    contact_info = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user_type = relationship("UserType")
    access = relationship("UserAccess", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


# UserType table
class UserType(Base):
    __tablename__ = "user_type"

    id = Column(Integer, primary_key=True, index=True)
    user_type_id = Column(Integer, unique=True, nullable=False)
    user_type = Column(String(50), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserType(user_type_id={self.user_type_id}, user_type={self.user_type})>"


# UserAccess table
class UserAccess(Base):
    __tablename__ = "user_access"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    access_level = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="access")

    def __repr__(self):
        return f"<UserAccess(user_id={self.user_id}, access_level={self.access_level})>"
