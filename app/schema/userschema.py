from fastapi import Form
from pydantic import BaseModel, Field, field_validator
import re

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
NAME_REGEX  = r"^[a-zA-Z\s]+$"


class UserBase(BaseModel):
    name: str = Field(...)
    email: str = Field(...)


class UserCreate(UserBase):
    password:str=Field(...)
    @field_validator("password")
    def validate_password(cls,password):
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            raise ValueError("Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.")
        return password
    @field_validator("email")
    def validate_email(cls,email):
        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Invalid email format")
        return email
    
    @field_validator("name")
    def validate_name(cls,name):
        if not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", name):
            raise ValueError("Name should be alpabhetic and maximum size should be 50")
        return name


class UserLogin(BaseModel):
    email: str = Form(...)
    password: str = Form(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls,email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")
        return email

    @field_validator("password")
    def validate_password(cls,password):
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            raise ValueError("Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.")
        return password


    
class UserResponse(BaseModel):
    # id:int
    name:str
    # email:str
    token: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    model_config = {"from_attributes": True,"exclude_none":True}
 
