from flask_pydantic_spec import FlaskPydanticSpec

spec = FlaskPydanticSpec(
    "flask",
    title="CSV Processing API",
    version="v1.0",
    path="api/v1/docs",
    ui="swagger",
)
spec.config.update(validation_error_code=400)
