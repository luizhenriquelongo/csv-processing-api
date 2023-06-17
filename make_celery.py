import os

from app import create_app

flask_app = create_app(os.getenv("CONFIG_CLASS", "config.ProductionConfig"))
celery_app = flask_app.extensions["celery"]
