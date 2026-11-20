"""Pydantic v2 request and response schemas."""

from pydantic import BaseModel, Field


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    priority: str = Field(default="medium")


class TaskResponse(BaseModel):
    task_id: str
    title: str
    priority: str
    completed: bool = False
