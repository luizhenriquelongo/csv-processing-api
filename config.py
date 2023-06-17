import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Base configuration class. Contains default configuration settings + configuration settings applicable
    to all environments.
    """

    FLASK_ENV = "development"
    DEBUG = False
    TESTING = False

    # Find the absolute file path to the top level project directory
    BASE_DIR = Path(__file__).resolve().parent
    CSV_OUTPUT_DIR = os.getenv("CSV_OUTPUT_DIR", "static/output")
    CSV_INPUT_DIR = os.getenv("CSV_INPUT_DIR", "static/input")

    SECRET_KEY = os.getenv("SECRET_KEY", uuid.uuid4().hex)

    CELERY = {
        "broker_url": os.getenv("CELERY_BROKER_URL"),
        "result_backend": os.getenv("RESULT_BACKEND"),
        "task_ignore_result": True,
        # Scheduling a task to clean up files related to a task that has completed their workflow.
        "beat_schedule": {
            "cleanup-files-every-90-seconds": {
                "task": "background_tasks.tasks.cleanup_files",
                "schedule": 90.0,
                "options": {"expires": 15.0},
            }
        },
    }

    MONGO_URI = os.getenv("MONGO_URI")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    FLASK_ENV = "production"
