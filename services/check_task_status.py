from http import HTTPStatus
from typing import Dict, Protocol, Tuple

from dtos import Task, responses
from dtos.tasks import PublicTaskInfo
from services import mixins


class GetTaskDAO(Protocol):
    def get_task(self, task_id: str) -> Task:
        ...


class CheckTaskStatusService(mixins.BuildNextMixin):
    def __init__(self, dao: GetTaskDAO):
        self.dao = dao

    def check_status(self, task_id: str) -> Tuple[Dict, int]:
        task = self.dao.get_task(task_id)

        response = responses.TaskAPIResponse(task=PublicTaskInfo.from_task(task), next=self.build_next(task))

        return response.dict(exclude_none=True), HTTPStatus.OK
