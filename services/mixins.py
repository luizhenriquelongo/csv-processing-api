import dtos


class BuildNextMixin:
    @staticmethod
    def build_next(task) -> str | None:
        base_uri = "/api/v1/file-processing/tasks"
        next_map = {
            dtos.TaskStatus.QUEUED: f"/{task.id}/status",
            dtos.TaskStatus.IN_PROGRESS: f"/{task.id}/status",
            dtos.TaskStatus.COMPLETED: f"/{task.id}/download",
            dtos.TaskStatus.DOWNLOADED: None,
            dtos.TaskStatus.FAILED: None,
        }

        endpoint = next_map.get(task.status)
        if endpoint is None:
            return None

        return f"{base_uri}{endpoint}"
