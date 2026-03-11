from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email:EmailStr
    username:str
    password:str

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    username:str
    role:str
    created_at:datetime

    class Config:
        from_attributes = True