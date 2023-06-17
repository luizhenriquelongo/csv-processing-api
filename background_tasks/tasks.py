from celery import shared_task
from flask import current_app

from background_tasks.csv_processor import CSVProcessor
from daos import TasksMongoDAO

from app.extensions import db


@shared_task(ignore_result=True)
def process_csv(task_id: str):
    dao = TasksMongoDAO(db=db)
    output_dir = current_app.config["DOWNLOAD_FOLDER"]
    with CSVProcessor(task_id, dao, output_dir=output_dir) as file_processor:
        file_processor.execute()
