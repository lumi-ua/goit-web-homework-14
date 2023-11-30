from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class ContactModel(BaseModel):
    first_name: str = Field(min_length=2, max_length=20)
    last_name: str = Field(min_length=2, max_length=20)
    email: EmailStr
    phone_number: str = Field(min_length=5, max_length=25)
    birthday: date


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    
    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: str
    password: str = Field(min_length=4, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


