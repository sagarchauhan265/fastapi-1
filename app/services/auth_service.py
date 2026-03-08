from app.models.user import User
from passlib.context import CryptContext
from fastapi import HTTPException
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def auth_signup_service(user, db):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise ValueError("EMAIL_ALREADY_EXISTS")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "status": "success",
        "data": new_user
    }


def auth_login_service(email: str, password: str, db):

    db_user = db.query(User).filter(User.email == email.strip()).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "status": "success",
        "data": db_user
    }
