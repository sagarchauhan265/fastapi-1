from app.models.user import User
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