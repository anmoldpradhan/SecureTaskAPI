import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__="users"

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True,nullable=False)
    username=Column(String,unique=True,index=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    role=Column(String,default="user")
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    tasks=relationship("Task",back_populates="owner")

class TaskStatus(str,enum.Enum):
    todo="todo"
    in_progress="in_progress"
    done="done"

class Task(Base):
    __tablename__="tasks"

    id=Column(Integer,primary_key=True,index=True)
    title=Column(Text,nullable=False)
    description=Column(Text,nullable=True)
    status=Column(Enum(TaskStatus),default=TaskStatus.todo)
    priority=Column(Integer,default=1)
    owner_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())

    owner=relationship("User",back_populates="tasks")