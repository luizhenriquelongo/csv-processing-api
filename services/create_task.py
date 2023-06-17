import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Dict, Literal, Protocol, Tuple

from flask import Request
from werkzeug.datastructures import FileStorage

from background_tasks import process_csv
from dtos import Task, responses
from dtos.tasks import PublicTaskInfo
from services import mixins

from app.api import exceptions


class CreateTaskDAO(Protocol):
    def create_new_task(self, task_id: str, input_file_path: str) -> Task:
        ...


class CreateTaskService(mixins.BuildNextMixin):
    ALLOWED_EXTENSIONS: Tuple[Literal["csv"]] = ("csv",)

    def __init__(self, request: Request, dao: CreateTaskDAO, *, upload_folder: Path, download_folder: Path):
        self.request = request
        self.dao = dao
        self.upload_folder = upload_folder
        self.download_folder = download_folder

    def create_task(self) -> Tuple[Dict, int]:
        csv_file = self.get_file_from_request()
        task_id = str(uuid.uuid4())

        input_file_path = self.upload_folder / f"{task_id}.csv"

        csv_file.save(input_file_path)

        task = self.dao.create_new_task(task_id=task_id, input_file_path=str(input_file_path))

        process_csv.delay(task.id)
        response = responses.TaskAPIResponse(
            task=PublicTaskInfo.from_task(task), next=f"/api/v1/file-processing/tasks/{task.id}/status"
        )

        return response.dict(exclude_none=True), HTTPStatus.ACCEPTED

    def get_file_from_request(self) -> FileStorage:
        if "file" not in self.request.files:
            raise exceptions.BadRequestAPIException(
                details=[{"field": "file", "message": "No file part in the request"}]
            )

        file = self.request.files["file"]
        if file.filename == "":
            raise exceptions.BadRequestAPIException(details=[{"field": "file", "message": "No file selected"}])

        if file and (file_extension := file.filename.rsplit(".", 1)[1].lower()) not in self.ALLOWED_EXTENSIONS:
            raise exceptions.BadRequestAPIException(
                details=[{"field": "file", "message": f"File extension '{file_extension}' not supported."}]
            )

        return file
