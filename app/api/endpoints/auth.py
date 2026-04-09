from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.schema.response import ApiResponse
from app.services.auth_service import auth_signup_service, auth_login_service
from app.schema.userschema import UserCreate, UserLogin, UserResponse
from app.config.db import SessionLocal, get_db
from fastapi import Request
from datetime import datetime, timedelta
from jose import jwt

auth_router = APIRouter()

@auth_router.post("/signup",response_model=ApiResponse[UserResponse])
async def auth_signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db:Session = Depends(get_db)
    ):
     
    try:
         user = UserCreate(
            name=name,
            email=email,
            password=password
            )
    except Exception as e:
        errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
        raise HTTPException(
            status_code=400,
            detail=ApiResponse(
                success=False,
                message="Validation Error",
                error=errors
            ).model_dump(exclude={"data"})
        )
 
    result =  auth_signup_service(user,db)
    return JSONResponse(
        status_code=201,
        content=ApiResponse(
            success=True,
            message="User created successfully",
            data=UserResponse(
                id=result.id,
                name=result.name,
                email=result.email,
                created_at=str(result.created_at),
                updated_at=str(result.updated_at),
            )
        ).model_dump()
    )



@auth_router.post("/login",response_model=ApiResponse[UserResponse])
def auth_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = UserLogin(email=email, password=password)
    except ValidationError as e:
        errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
        raise HTTPException(status_code=422, detail=errors)
    result =  auth_login_service(data, db)
    payload = {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }

    print("SECRET_KEY:", settings.SECRET_KEY)
    print("ALGORITHM:", settings.ALGORITHM)
    token =  jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Login successful",
            data=UserResponse(
                id=result.id,
                name=result.name,
                email=result.email,
                 token=token,
                created_at=str(result.created_at),
                updated_at=str(result.updated_at)
            )
        ).model_dump()
    )

       