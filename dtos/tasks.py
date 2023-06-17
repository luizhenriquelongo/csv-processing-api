from enum import Enum

from pydantic import BaseModel

from dtos.types import ErrorsDict


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    DOWNLOADED = "DOWNLOADED"


class Task(BaseModel):
    id: str
    status: TaskStatus = TaskStatus.QUEUED
    input_file_path: str | None
    output_file_path: str | None
    errors: ErrorsDict | None
