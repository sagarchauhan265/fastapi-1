from pydantic import BaseModel, Field, field_validator
import re

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
NAME_REGEX  = r"^[a-zA-Z\s]+$"


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be blank")
        if not re.match(NAME_REGEX, name):
            raise ValueError("Name must contain only letters and spaces")
        return name

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        email = email.strip().lower()
        if not email:
            raise ValueError("Email cannot be blank")
        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Invalid email format")
        return email

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not password.strip():
            raise ValueError("Password cannot be blank")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")
        return password


class UserLogin(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        email = email.strip().lower()
        if not email:
            raise ValueError("Email cannot be blank")
        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Invalid email format")
        return email

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not password.strip():
            raise ValueError("Password cannot be blank")
        return password


class UserResponse(UserBase):
    id: int
    name: str
    email: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
