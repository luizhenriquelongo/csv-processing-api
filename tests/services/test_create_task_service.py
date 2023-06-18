from http import HTTPStatus
from io import BytesIO

import pytest
from flask import Request
from werkzeug.datastructures import FileStorage

import dtos
from daos.dummy_dao import DummyDAO
from services import CreateTaskService

from app.api import exceptions


@pytest.fixture
def request_with_file(mocker):
    file_storage = FileStorage(stream=BytesIO(b"file content"), filename="test.csv")
    request = mocker.MagicMock(spec=Request)
    request.files = {"file": file_storage}
    return request


@pytest.fixture
def create_task_dao(upload_folder):
    return DummyDAO(input_dir=upload_folder)


@pytest.fixture
def upload_folder(tmp_path):
    return tmp_path / "uploads"


@pytest.fixture
def download_folder(tmp_path):
    return tmp_path / "downloads"


def test_create_task(request_with_file, create_task_dao, upload_folder, download_folder, mocker):
    service = CreateTaskService(
        request=request_with_file, dao=create_task_dao, upload_folder=upload_folder, download_folder=download_folder
    )
    mocked_get_file_from_request = mocker.patch("services.create_task.CreateTaskService.get_file_from_request")
    mocked_get_file_from_request.save = mocker.Mock()

    mocked_process_csv = mocker.patch("services.create_task.process_csv")
    mocked_process_csv.delay = mocker.Mock()

    expected_task_id = service.task_id
    expected_response = {
        "task": {
            "id": expected_task_id,
            "status": dtos.TaskStatus.QUEUED,
        },
        "next": f"/api/v1/file-processing/tasks/{service.task_id}/status",
    }
    expected_status = HTTPStatus.ACCEPTED

    response, status = service.create_task()

    assert response == expected_response
    assert status == expected_status
    mocked_process_csv.delay.assert_called_once_with(expected_task_id)


def test_create_task_missing_file(request_with_file, create_task_dao, upload_folder, download_folder):
    request_with_file.files = {}
    service = CreateTaskService(
        request=request_with_file, dao=create_task_dao, upload_folder=upload_folder, download_folder=download_folder
    )

    with pytest.raises(exceptions.BadRequestAPIException) as exc_info:
        service.create_task()

        assert exc_info.value.details == [{"field": "file", "message": "No file part in the request"}]


def test_create_task_no_file_selected(request_with_file, create_task_dao, upload_folder, download_folder):
    request_with_file.files["file"].filename = ""
    service = CreateTaskService(
        request=request_with_file, dao=create_task_dao, upload_folder=upload_folder, download_folder=download_folder
    )

    with pytest.raises(exceptions.BadRequestAPIException) as exc_info:
        service.create_task()

        assert exc_info.value.details == [{"field": "file", "message": "No file selected"}]


def test_create_task_invalid_file_extension(request_with_file, create_task_dao, upload_folder, download_folder):
    request_with_file.files["file"].filename = "test.txt"
    service = CreateTaskService(
        request=request_with_file, dao=create_task_dao, upload_folder=upload_folder, download_folder=download_folder
    )

    with pytest.raises(exceptions.BadRequestAPIException) as exc_info:
        service.create_task()

        assert exc_info.value.details == [{"field": "file", "message": "File extension 'txt' not supported."}]
