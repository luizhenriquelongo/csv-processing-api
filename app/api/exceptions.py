from http import HTTPStatus
from typing import Dict, List, Tuple

from pydantic import BaseModel

from dtos.responses import ErrorResponse


class BaseAPIException(Exception):
    http_status: HTTPStatus
    message: str
    response: ErrorResponse

    def __init__(self, details: List[Dict | BaseModel | str]):
        assert hasattr(
            self, "http_status"
        ), f"All classes inheriting from {BaseAPIException.__name__} must declare 'http_status'."

        if not isinstance(self.http_status, HTTPStatus):
            raise TypeError(
                f"'{self.__class__}.https_status' must be an object of HTTPStatus, got {type(self.http_status)}"
            )
        assert isinstance(self.http_status, HTTPStatus), "http_status"

        self.status_code = self.http_status.value
        self.code = self.http_status.phrase

        if not hasattr(self, "message"):
            self.message = self.http_status.description

        self.response = ErrorResponse(code=self.code, message=self.message, details=details)

    def to_flask_response(self) -> Tuple[Dict, int]:
        return self.response.dict(exclude_none=True), self.status_code


class BadRequestAPIException(BaseAPIException):
    http_status = HTTPStatus.BAD_REQUEST
    message = "The request is invalid or missing required data."


class ResourceNotAvailableAPIException(BaseAPIException):
    http_status = HTTPStatus.NOT_FOUND
    message = "Resouce not available."


class NotFoundAPIException(BaseAPIException):
    http_status = HTTPStatus.NOT_FOUND


class InternalServerErrorAPIException(BaseAPIException):
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
