from app.models.user import User
from app.models.rbac import UserRole, RolePermission, Permission, Role
from passlib.context import CryptContext
from fastapi import HTTPException
import re
from datetime import datetime, timedelta
from fastapi import HTTPException,status
from app.config.redis import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def auth_signup_service(user, db):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="EMAIL_ALREADY_EXISTS")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def auth_login_service(user, db):

    db_user = db.query(User).filter(User.email == user.email.strip()).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return db_user

def get_user_roles_and_permissions(user_id: int, db) -> tuple:
    """Returns (role_names, permission_names) for a user."""
    user_role_rows = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    role_ids = [ur.role_id for ur in user_role_rows]

    if not role_ids:
        return [], []

    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    role_names = [r.name for r in roles]

    rp_rows = db.query(RolePermission).filter(RolePermission.role_id.in_(role_ids)).all()
    permission_ids = list({rp.permission_id for rp in rp_rows})

    if not permission_ids:
        return role_names, []

    permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    permission_names = [p.name for p in permissions]

    return role_names, permission_names


def blacklist_token(db,payload: dict):
    # Placeholder for any server-side logout operations if needed
    # Store the token in Redis to invalidate it
    print(payload)
    exp = payload.get("exp")
    if exp is None:
        return False
    current_time = int(datetime.utcnow().timestamp())
    ttl = exp - current_time
    redis_client.setex(payload["token"], ttl, "blacklisted")  # Set token as blacklisted for 1 hour
    return True