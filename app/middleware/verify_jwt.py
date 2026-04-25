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


def require_permission(permission: str):
    """
    Factory that returns a dependency checking for a specific permission.
    Usage: dependencies=[Depends(require_permission("product:create"))]
    """
    def checker(payload: dict = Depends(verify_jwt)):
        if permission not in payload.get("permissions", []):
            raise HTTPException(403, f"Permission '{permission}' required")
        return payload
    return checker


def require_role(role: str):
    """
    Factory that returns a dependency checking for a specific role.
    Usage: dependencies=[Depends(require_role("admin"))]
    """
    def checker(payload: dict = Depends(verify_jwt)):
        if role not in payload.get("roles", []):
            raise HTTPException(403, f"Role '{role}' required")
        return payload
    return checker