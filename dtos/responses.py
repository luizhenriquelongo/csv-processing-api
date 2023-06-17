from typing import Dict, List

from pydantic import BaseModel, Field

from dtos import TaskStatus


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: List[Dict]


class BaseWorkflowResponse(BaseModel):
    next: str | None = Field(
        None,
        title="Endpoint to call next to continue the workflow.",
        description="e.g. {..., 'next': '/api/v1/task/aa5322dd-d3fc-405a-b79d-c24c87ba201e/status'}",
    )


class TaskCreatedResponse(BaseWorkflowResponse):
    task_id: str
    status: TaskStatus
