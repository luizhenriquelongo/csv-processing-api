from typing import Dict, List

from pydantic import BaseModel, Field

from dtos.tasks import PublicTaskInfo


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: List[Dict]


class BaseWorkflowResponse(BaseModel):
    next: str | None = Field(
        None,
        title="Endpoint to call next to continue the workflow.",
        description="Use this field to automate the workflow, it will always return the next endpoint to call.",
    )


class TaskAPIResponse(BaseWorkflowResponse):
    task: PublicTaskInfo

    class Config:
        schema_extra = {
            "example": {
                "next": "/api/v1/file-processing/task/aa5322dd-d3fc-405a-b79d-c24c87ba201e/status",
                "task": {"id": "aa5322dd-d3fc-405a-b79d-c24c87ba201e", "status": "IN_PROGRESS"},
            }
        }
