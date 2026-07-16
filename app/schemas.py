from pydantic import BaseModel
from enum import Enum
from datetime import datetime


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


class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
