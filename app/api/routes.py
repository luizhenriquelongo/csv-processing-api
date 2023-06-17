from flask import Blueprint, current_app, request
from flask_pydantic_spec import MultipartFormRequest, Response

import services
from daos import TasksMongoDAO
from dtos import responses

from app.extensions import db, spec

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/api/v1/file-processing/tasks")


@tasks_bp.route("/", methods=["POST"])
@spec.validate(
    body=MultipartFormRequest(),
    resp=Response(HTTP_202=responses.TaskAPIResponse, HTTP_400=responses.ErrorResponse),
    tags=["Tasks"],
)
def create_task():
    """
    Create a new task by uploading a CSV file.

    This endpoint allows users to create a new task by uploading a CSV file.
    The uploaded file will be processed asynchronously in the background.
    Upon successful submission, the API will return a response with HTTP status 202 Accepted,
    indicating that the task has been created and will be processed.
    """
    dao = TasksMongoDAO(db=db)
    service = services.CreateTaskService(
        request=request,
        dao=dao,
        upload_folder=current_app.config["UPLOAD_FOLDER"],
        download_folder=current_app.config["DOWNLOAD_FOLDER"],
    )
    return service.create_task()


@tasks_bp.route("/<task_id>/status", methods=["GET"])
@spec.validate(
    resp=Response(HTTP_200=responses.TaskAPIResponse, HTTP_400=responses.ErrorResponse),
    tags=["Tasks"],
)
def check_task_status(task_id: str):
    dao = TasksMongoDAO(db=db)
    service = services.CheckTaskStatusService(dao=dao)
    return service.check_status(task_id=task_id)
