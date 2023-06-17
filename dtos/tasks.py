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

    def mark_as_finished(self):
        self.input_file_path = None
        self.output_file_path = None


class PublicTaskInfo(BaseModel):
    id: str
    status: TaskStatus
    errors: ErrorsDict | None

    @classmethod
    def from_task(cls, task: Task):
        visible_fields = ("id", "status", "errors")
        return cls(**{field: getattr(task, field) for field in visible_fields})
