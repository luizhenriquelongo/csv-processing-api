from typing import Dict, Tuple

from app.api.exceptions import BaseAPIException


def handle_api_exceptions(exception: BaseAPIException) -> Tuple[Dict, int]:
    return exception.to_flask_response()
