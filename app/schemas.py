from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "inprogress"
    completed = "completed"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority


class TaskCreate(TaskBase):
    pass


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    id: int
    owner: UserResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
