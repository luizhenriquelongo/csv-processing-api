import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_sqlite_dabase_uri(base_dir: Path, db_name: str):
    return f"sqlite:///{base_dir / db_name}.db"


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
    }

    MONGO_URI = os.getenv("MONGO_URI")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_sqlite_dabase_uri(Config.BASE_DIR, "dev")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_sqlite_dabase_uri(Config.BASE_DIR, "test")


class ProductionConfig(Config):
    FLASK_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI", get_sqlite_dabase_uri(Config.BASE_DIR, "prod"))
