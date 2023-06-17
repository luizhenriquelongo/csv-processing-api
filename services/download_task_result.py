from http import HTTPStatus
from typing import Dict, Protocol, Tuple

from flask import Response, send_file

from dtos import Task, responses
from dtos.tasks import PublicTaskInfo, TaskStatus
from services import mixins

from app.api.exceptions import ResourceNotAvailableAPIException


class DownloadTaskDAO(Protocol):
    def get_task(self, task_id: str) -> Task:
        ...

    def update_task(self, task: Task) -> Task:
        ...


class DownloadTaskResultService(mixins.BuildNextMixin):
    def __init__(self, dao: DownloadTaskDAO):
        self.dao = dao

    def download(self, task_id: str) -> Tuple[Dict, int] | Response:
        task = self.dao.get_task(task_id)

        if task.status == TaskStatus.DOWNLOADED:
            raise ResourceNotAvailableAPIException(details=[{"file": "File already downloaded."}])

        if task.status == TaskStatus.COMPLETED:
            task.status = TaskStatus.DOWNLOADED
            self.dao.update_task(task)
            return send_file(
                task.output_file_path, mimetype="text/csv", as_attachment=True, download_name="results.csv"
            )

        response = responses.TaskAPIResponse(task=PublicTaskInfo.from_task(task), next=self.build_next(task))
        return response.dict(exclude_none=True), HTTPStatus.PARTIAL_CONTENT
