from flask import Blueprint, current_app, request
from flask_pydantic_spec import MultipartFormRequest, Response

from daos import TasksMongoDAO
from dtos import responses
from services import CreateTaskService

from app.extensions import db, spec

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/api/v1/file-processing/tasks")


@tasks_bp.route("/", methods=["POST"])
@spec.validate(
    body=MultipartFormRequest(),
    resp=Response(HTTP_202=responses.TaskCreatedResponse, HTTP_400=responses.ErrorResponse, HTTP_422=None),
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
    service = CreateTaskService(
        request=request,
        dao=dao,
        upload_folder=current_app.config["UPLOAD_FOLDER"],
        download_folder=current_app.config["DOWNLOAD_FOLDER"],
    )
    return service.create_task()
