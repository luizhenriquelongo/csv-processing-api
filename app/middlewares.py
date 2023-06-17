from typing import Dict, Tuple

from app.api import exceptions


def handle_api_exceptions(exception: exceptions.BaseAPIException) -> Tuple[Dict, int]:
    return exception.to_flask_response()


def handle_bare_excpetions(exception: Exception):
    raise exceptions.InternalServerErrorAPIException(details=["Something went wrong."])


def handle_404(error):
    raise exceptions.NotFoundAPIException(details=["Resource not found."])
