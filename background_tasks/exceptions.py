from dtos.types import ErrorsDict


class ProcessingError(Exception):
    """This exception will be raised once any expected error happen while processing the file."""

    def __init__(self, errors: ErrorsDict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors
