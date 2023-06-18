from http import HTTPStatus
from typing import Dict, Protocol, Tuple

import dtos
from services.mixins import BuildNextMixin


class GetTaskDAO(Protocol):
    def get_task(self, task_id: str) -> dtos.Task:
        ...


class CheckTaskStatusService(BuildNextMixin):
    def __init__(self, dao: GetTaskDAO):
        self.dao = dao

    def check_status(self, task_id: str) -> Tuple[Dict, int]:
        task = self.dao.get_task(task_id)

        response = dtos.TaskAPIResponse(task=dtos.PublicTaskInfo.from_task(task), next=self.build_next(task))

        return response.dict(exclude_none=True), HTTPStatus.OK
