from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask import Response

from dtos import Task, TaskStatus
from services import DownloadTaskResultService

from app.api.exceptions import ResourceNotAvailableAPIException


@pytest.fixture
def download_task_dao():
    return MagicMock()


@pytest.fixture
def download_task_result_service(download_task_dao):
    return DownloadTaskResultService(download_task_dao)


def test_download_task_already_downloaded(download_task_result_service, download_task_dao):
    task_id = "123"
    task = Task(id=task_id, status=TaskStatus.DOWNLOADED)
    download_task_dao.get_task.return_value = task

    with pytest.raises(ResourceNotAvailableAPIException):
        download_task_result_service.download(task_id)


def test_download_task_completed(download_task_result_service, download_task_dao, mocker):
    task_id = "123"
    task = Task(id=task_id, status=TaskStatus.COMPLETED, output_file_path="mock_output_path")
    download_task_dao.get_task.return_value = task
    download_task_dao.update_task.return_value = task

    mock_send_file = mocker.patch("services.download_task_result.send_file")
    mock_send_file.return_value = Response()

    response = download_task_result_service.download(task_id)

    download_task_dao.update_task.assert_called_once_with(task)
    mock_send_file.assert_called_once_with(
        task.output_file_path, mimetype="text/csv", as_attachment=True, download_name="results.csv"
    )
    assert isinstance(response, Response)


def test_download_task_partial_content(download_task_result_service, download_task_dao, mocker):
    task_id = "123"
    task = Task(id=task_id, status=TaskStatus.IN_PROGRESS)
    download_task_dao.get_task.return_value = task

    mock_response_dict = mocker.patch("dtos.responses.TaskAPIResponse.dict")

    response = download_task_result_service.download(task_id)

    mock_response_dict.assert_called_once_with(exclude_none=True)
    download_task_dao.update_task.assert_not_called()
    assert response == (mock_response_dict.return_value, HTTPStatus.PARTIAL_CONTENT)
