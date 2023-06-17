from celery import shared_task

from background_tasks.csv_processor import CSVProcessor
from daos.dummy_dao import DummyDAO


@shared_task(ignore_result=True)
def process_csv(task_id: str, input_dir: str, output_dir: str):
    dao = DummyDAO(input_dir)
    with CSVProcessor(task_id, dao, output_dir=output_dir) as file_processor:
        file_processor.execute()
