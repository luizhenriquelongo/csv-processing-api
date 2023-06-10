import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Find the absolute file path to the top level project directory
BASE_DIR = Path(__file__).resolve().parent


def get_sqlite_dabase_uri(db_name: str):
    return f"sqlite:///{BASE_DIR / db_name}.db"


class Config:
    """
    Base configuration class. Contains default configuration settings + configuration settings applicable
    to all environments.
    """

    FLASK_ENV = "development"
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY", uuid.uuid4().hex)

    CELERY = {
        "CELERY_BROKER_URL": os.getenv("CELERY_BROKER_URL"),
        "RESULT_BACKEND": os.getenv("RESULT_BACKEND"),
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_sqlite_dabase_uri("dev")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_sqlite_dabase_uri("test")


class ProductionConfig(Config):
    FLASK_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI", get_sqlite_dabase_uri("prod"))
