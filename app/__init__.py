from typing import TYPE_CHECKING, Type

from flask import Flask

if TYPE_CHECKING:
    from config import Config


def create_app(config: Type["Config"] | str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    return app
