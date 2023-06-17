from enum import Enum

from pydantic import BaseModel

from dtos.types import ErrorsDict


class TaskStatus(Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"


class Task(BaseModel):
    id: str
    status: TaskStatus = TaskStatus.QUEUED
    input_file_path: str | None
    output_file_path: str | None
    errors: ErrorsDict | None
