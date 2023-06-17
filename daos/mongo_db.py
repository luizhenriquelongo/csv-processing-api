from typing import List

from flask_pymongo.wrappers import Collection, Database

from dtos import Task


class MongoDAO:
    def __init__(self, db: Database):
        self._db = db


class TasksMongoDAO(MongoDAO):
    def __init__(self, db: Database):
        super().__init__(db)
        self.collection: Collection = self._db.tasks

    def get_task(self, task_id: str) -> Task:
        task = self.collection.find_one_or_404({"id": task_id})
        return Task(**task)

    def update_task(self, task: Task) -> Task:
        task_data = task.dict(exclude={"id"})
        self.collection.update_one({"id": task.id}, {"$set": task_data})
        return task

    def create_new_task(self, task_id: str, input_file_path: str) -> Task:
        task = Task(id=task_id, input_file_path=input_file_path)
        self.collection.insert_one(task.dict())
        return task

    def get_tasks_with_their_workflow_done(self) -> List[Task]:
        query = {
            "$and": [
                {"$or": [{"status": "DOWNLOADED"}, {"status": "FAILED"}]},
                {"input_file_path": {"$ne": None}},
                {"output_file_path": {"$ne": None}},
            ]
        }

        # Fetch the tasks
        tasks = self.collection.find(query)
        return [Task(**task) for task in tasks]
