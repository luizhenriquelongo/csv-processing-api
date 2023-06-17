from typing import TYPE_CHECKING, Type

from flask import Flask

from helpers.files import enforce_directory_creation

from app import middlewares
from app.api.exceptions import BaseAPIException
from app.api.routes import tasks_bp
from app.extensions import spec
from app.extensions.celery import celery_init_app

if TYPE_CHECKING:
    from config import Config


def create_app(config: Type["Config"] | str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    # Setting up folders for input and output files
    app.config["UPLOAD_FOLDER"] = app.config["BASE_DIR"] / app.config["CSV_INPUT_DIR"]
    app.config["DOWNLOAD_FOLDER"] = app.config["BASE_DIR"] / app.config["CSV_OUTPUT_DIR"]
    enforce_directory_creation(app.config["UPLOAD_FOLDER"], app.config["DOWNLOAD_FOLDER"])

    app.register_blueprint(tasks_bp)
    spec.register(app)

    app.config.from_prefixed_env()
    celery_init_app(app)

    app.register_error_handler(400, middlewares.handle_404)
    app.register_error_handler(Exception, middlewares.handle_bare_excpetions)
    app.register_error_handler(BaseAPIException, middlewares.handle_api_exceptions)
    return app
