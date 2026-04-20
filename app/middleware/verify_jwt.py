from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config.settings import settings
from app.config.redis import redis_client
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

_bearer = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    print("credentials", credentials)
    if not credentials:
        raise HTTPException(401, "Token missing")

    token = credentials.credentials
    print("credentials", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["token"] = token 
        is_blacklisted = redis_client.get(token)
        if is_blacklisted:
            raise HTTPException(401, "Token has been blacklisted")
        return payload
    except JWTError:
        print("JWTError", JWTError)
        raise HTTPException(401, "Invalid or expired token")