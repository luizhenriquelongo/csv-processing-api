from flask import current_app, g
from flask_pymongo import PyMongo
from flask_pymongo.wrappers import Database
from werkzeug.local import LocalProxy


def get_db() -> Database:
    """
    Configuration method to return db instance
    """
    db_instance = getattr(g, "_database", None)

    if db_instance is None:
        db_instance = g._database = PyMongo(current_app).db

    return db_instance


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)
