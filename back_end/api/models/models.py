from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    apps = relationship("CustomerApps", back_populates="customer")
    users = relationship("User", back_populates="customer")

class CustomerApps(Base):
    __tablename__ = "customer_apps"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    object_storage_location = Column(Text)
    temp_storage_location = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="apps")

class UserType(Base):
    __tablename__ = "user_type"
    id = Column(Integer, primary_key=True)
    user_type_id = Column(Integer, nullable=False, unique=True)
    user_type = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="user_type_rel")

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    user_type_id = Column(Integer, ForeignKey("user_type.user_type_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)
    department = Column(String(100))
    name = Column(String(255), nullable=False)
    contact_info = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    customer = relationship("Customer", back_populates="users")
    user_type_rel = relationship("UserType", back_populates="users")
    access = relationship("UserAccess", back_populates="user")

class UserAccess(Base):
    __tablename__ = "user_access"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    app_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="access")
    customer = relationship("Customer")

class Config(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    app_id = Column(Integer, nullable=False)
    item = Column(String(100), nullable=False)
    value = Column(Text)
    faq_questions = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

class RoleTypes(Base):
    __tablename__ = "role_types"
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, nullable=False, unique=True)
    role_name = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("role_id", name="uq_role_id"),)
