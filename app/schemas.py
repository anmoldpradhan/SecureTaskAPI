from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional
from app.models import TaskStatus

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

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[int]=None
    role:Optional[str]=None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: int = 1

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True