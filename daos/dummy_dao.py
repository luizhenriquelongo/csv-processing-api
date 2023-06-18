"""
This module contains a DummyDAO class that is used for test purposes ONLY and serves as a placeholder
for not yet implemented DAOs.

IMPORTANT: DO NOT use this class in production environments under any circumstances. It is solely intended
for testing, debugging, or as a temporary placeholder until the actual DAO implementation is available.

The DummyDAO class provides basic functionality for creating, retrieving, and updating tasks. It does not
interact with a real data source and is only used to simulate the behavior of a DAO for testing purposes.

Usage example:
    dao = DummyDAO(input_file_path="/path/to/input/file.csv")
    task = dao.create_new_task(task_id="12345", input_file_path="/path/to/input/file.csv")
    retrieved_task = dao.get_task(task_id="12345")
    updated_task = dao.update_task(retrieved_task)

    Please note that the DummyDAO class is meant to be replaced with the actual DAO implementation once
    it becomes available.

Author: Luiz Henrique Longo
"""
import uuid
from pathlib import Path

import dtos
from logger import get_logger

logger = get_logger(__file__)


class DummyDAO:
    def __init__(self, input_dir: Path | str):
        self.input_dir = str(input_dir)

    def create_new_task(self, task_id: str, input_file_path: str) -> dtos.Task:
        task = dtos.Task(id=task_id, input_file_path=input_file_path)
        logger.debug("Creating fake task...")
        logger.debug(f"Task info: {task.dict()}")
        return task

    def get_task(self, task_id: str) -> dtos.Task:
        logger.debug("Getting fake task...")
        task = dtos.Task(id=task_id, input_file_path=f"{self.input_dir}/{str(uuid.uuid4())}.csv")
        logger.debug(f"Task info: {task.dict()}")
        return task

    def update_task(self, task: dtos.Task) -> dtos.Task:
        logger.debug("Fake updating a task...")
        logger.debug(f"Task info: {task.dict()}")
        return task
