import os
import shutil
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from background_tasks.csv_processor import CSVProcessor
from background_tasks.exceptions import ProcessingError
from daos.mongo_db import MongoDAO, TasksMongoDAO
from dtos import Task, TaskStatus

TASK_ID = "8bd7481e-1eb3-47e4-9b1f-a32b761b72eb"


@pytest.fixture
def tmp_dir(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.fixture
def task_dao(mocker: MockerFixture, task):
    mock = mocker.Mock(spec=TasksMongoDAO)
    mock.get_task.return_value = task
    return mock


@pytest.fixture
def csv_file(tmp_dir):
    csv_path = tmp_dir / "test.csv"
    csv_data = "Song,Date,Number of Plays\nSong 1,2022-01-01,10\nSong 2,2022-01-02,20\nSong 1,2022-01-02,15\n"
    csv_path.write_text(csv_data)
    yield csv_path


@pytest.fixture
def task(csv_file):
    return Task(
        id=TASK_ID,
        status=TaskStatus.QUEUED,
        input_file_path=str(csv_file),
        output_file_path=None,
        errors=None,
    )


def test_execute(task_dao, mocker: MockerFixture, task, tmp_dir):
    fake_file_path = Path("/fake/path/to/final/file.csv")
    mocked_update_task = mocker.patch("background_tasks.csv_processor.CSVProcessor.update_task")
    mocked_validate_task = mocker.patch("background_tasks.csv_processor.CSVProcessor.validate_task")
    mocked_process_task = mocker.patch("background_tasks.csv_processor.CSVProcessor.process_task")
    mocked_process_task.return_value = fake_file_path

    with CSVProcessor(task_id=TASK_ID, dao=task_dao, output_dir=tmp_dir) as file_processor:  # type: ignore
        file_processor.execute()

    mocked_update_task.assert_has_calls(
        [
            mocker.call(status=TaskStatus.IN_PROGRESS),
            mocker.call(status=TaskStatus.COMPLETED, output_file_path=fake_file_path),
        ]
    )
    mocked_validate_task.assert_called_once()
    mocked_process_task.assert_called_once()


def test_validate_task_with_not_input_file_path(task_dao, tmp_dir, task):
    task.input_file_path = None
    task_dao.get_task.return_value = task

    with pytest.raises(ProcessingError) as exception:
        file_processor = CSVProcessor(task_id=TASK_ID, dao=task_dao, output_dir=tmp_dir)  # type: ignore
        file_processor.validate_task()

        assert exception.value.errors == {"input_file": "Cannot process a csv without the input file."}


def test_validate_task_with_different_input_file_format(task_dao, tmp_dir, task):
    task.input_file_path = "/fake/path/to/file.pdf"
    task_dao.get_task.return_value = task

    with pytest.raises(ProcessingError) as exception:
        file_processor = CSVProcessor(task_id=TASK_ID, dao=task_dao, output_dir=tmp_dir)  # type: ignore
        file_processor.validate_task()

        assert exception.value.errors == {"input_file": "File format not supported."}


def test_validate_task(task_dao, tmp_dir):
    with CSVProcessor(task_id=TASK_ID, dao=task_dao, output_dir=tmp_dir) as file_processor:  # type: ignore
        file_processor.validate_task()


def test_process_task(task_dao, mocker: MockerFixture, tmp_dir):
    fake_file_path = Path("fake/file/path.csv")
    mocked_split_file_into_multiple_tmp_files_by_name = mocker.patch(
        "background_tasks.csv_processor.CSVProcessor.split_file_into_multiple_tmp_files_by_name"
    )
    mocked_process_and_generate_result_file = mocker.patch(
        "background_tasks.csv_processor.CSVProcessor.process_and_generate_result_file"
    )
    mocked_process_and_generate_result_file.return_value = fake_file_path

    with CSVProcessor(task_id=TASK_ID, dao=task_dao, output_dir=tmp_dir) as file_processor:  # type: ignore
        file_path = file_processor.process_task()

    assert file_path == fake_file_path
    mocked_split_file_into_multiple_tmp_files_by_name.assert_called_once()
    mocked_process_and_generate_result_file.assert_called_once()
