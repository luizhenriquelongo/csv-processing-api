import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Dict, Literal, Protocol, Tuple

from flask import Request
from werkzeug.datastructures import FileStorage

import dtos
from background_tasks.tasks import process_csv
from services.mixins import BuildNextMixin

from app.api import exceptions


class CreateTaskDAO(Protocol):
    def create_new_task(self, task_id: str, input_file_path: str) -> dtos.Task:
        ...


class CreateTaskService(BuildNextMixin):
    ALLOWED_EXTENSIONS: Tuple[Literal["csv"]] = ("csv",)

    def __init__(self, request: Request, dao: CreateTaskDAO, *, upload_folder: Path, download_folder: Path):
        self.request = request
        self.dao = dao
        self.upload_folder = upload_folder
        self.download_folder = download_folder
        self.task_id = str(uuid.uuid4())

    def create_task(self) -> Tuple[Dict, int]:
        csv_file = self.get_file_from_request()

        input_file_path = self.upload_folder / f"{self.task_id}.csv"

        csv_file.save(input_file_path)

        task = self.dao.create_new_task(task_id=self.task_id, input_file_path=str(input_file_path))

        process_csv.delay(task.id)
        response = dtos.TaskAPIResponse(
            task=dtos.PublicTaskInfo.from_task(task), next=f"/api/v1/file-processing/tasks/{task.id}/status"
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
