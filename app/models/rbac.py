from app.config.db import Base
from sqlalchemy import Column, Integer, String


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)   # "admin", "manager"
    description = Column(String(200))


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # "product:create"
    description = Column(String(200))


class UserRole(Base):
    """Which roles a user has"""
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role_id = Column(Integer, nullable=False, index=True)


class RolePermission(Base):
    """Which permissions a role carries"""
    __tablename__ = "role_permissions"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, nullable=False, index=True)
    permission_id = Column(Integer, nullable=False, index=True)
