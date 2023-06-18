from http import HTTPStatus

from daos.dummy_dao import DummyDAO
from dtos.tasks import PublicTaskInfo, Task
from services.check_task_status import CheckTaskStatusService


def test_check_task_status():
    service = CheckTaskStatusService(dao=DummyDAO(input_dir="./"))

    task_id = "task_id"
    expected_task = Task(id=task_id)
    expected_response = {
        "task": PublicTaskInfo.from_task(expected_task).dict(exclude_none=True),
        "next": f"/api/v1/file-processing/tasks/{task_id}/status",
    }

    expected_status = HTTPStatus.OK

    response, status = service.check_status(task_id)

    assert response == expected_response
    assert status == expected_status
