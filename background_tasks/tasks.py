from celery import shared_task
from flask import current_app

import helpers.files
from background_tasks.csv_processor import CSVProcessor
from daos import TasksMongoDAO
from dtos import Task

from app.extensions import db


@shared_task(ignore_result=True)
def process_csv(task_id: str):
    dao = TasksMongoDAO(db=db)
    output_dir = current_app.config["DOWNLOAD_FOLDER"]
    with CSVProcessor(task_id, dao, output_dir=output_dir) as file_processor:
        file_processor.execute()


@shared_task(ignore_result=True)
def cleanup_files():
    """
    This task will remove any files related to a task that has completed their worflow or has the status 'FAILED'.
    At the end of this process, the task would still be inside the database but with
    input_file_path=None and output_file_path=None.
    """
    dao = TasksMongoDAO(db=db)
    tasks = dao.get_tasks_with_their_workflow_done()
    for task in tasks:
        helpers.files.delete_files(task.input_file_path, task.output_file_path)
        task.mark_as_finished()
        dao.update_task(task)
