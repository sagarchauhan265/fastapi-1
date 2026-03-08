from fastapi import APIRouter, Form, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.services.auth_service import auth_signup_service, auth_login_service
from app.schema.userschema import UserCreate, UserLogin
from app.config.db import SessionLocal, get_db

auth_router = APIRouter()




@auth_router.post("/signup")
async def auth_signup(user:UserCreate,db:Session = Depends(get_db)):
    result =  auth_signup_service(user,db)
    return result









# @auth_router.post("/signup")
# def auth_signup(
#     q:str,
#     name:str = Form(...),
#     # email:str = Form(...),
#     # image:File = File(...),
#     ):

#     return {
#         "status":"ok signup",
#         "name":name,
#         "search":q

#     }

@auth_router.post("/login")
def auth_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = UserLogin(email=email, password=password)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    return auth_login_service(data.email, data.password, db)