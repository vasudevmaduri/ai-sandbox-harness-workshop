"""Thin HTTP-layer application factory with centralized domain-to-HTTP error mapping."""

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from task_api.errors import InvalidTaskError, TaskNotFoundError
from task_api.repository import InMemoryTaskRepository
from task_api.schemas import CreateTaskRequest
from task_api.service import TaskService


@dataclass(frozen=True)
class HTTPResponse:
    status_code: int
    body: dict[str, Any] | list[dict[str, Any]]


class TaskAPIApp:
    """Thin transport layer separating HTTP status mapping from TaskService."""

    def __init__(self, service: TaskService) -> None:
        self._service = service

    def handle(self, method: str, path: str, payload: dict[str, Any] | None = None) -> HTTPResponse:
        try:
            if method == "GET" and path == "/health":
                return HTTPResponse(200, {"status": "ok"})
            if method == "GET" and path == "/tasks":
                return HTTPResponse(200, [t.model_dump() for t in self._service.list_tasks()])
            if method == "POST" and path == "/tasks":
                req = CreateTaskRequest.model_validate(payload or {})
                created = self._service.create_task(req)
                return HTTPResponse(201, created.model_dump())
            if method == "GET" and path.startswith("/tasks/"):
                task_id = path.removeprefix("/tasks/")
                found = self._service.get_task(task_id)
                return HTTPResponse(200, found.model_dump())
            return HTTPResponse(404, {"error": "not_found", "detail": f"Route {method} {path} not found."})
        except ValidationError as exc:
            return HTTPResponse(422, {"error": "validation_error", "detail": exc.errors()})
        except InvalidTaskError as exc:
            return HTTPResponse(400, {"error": "domain_error", "detail": str(exc)})
        except TaskNotFoundError as exc:
            return HTTPResponse(404, {"error": "not_found", "detail": str(exc)})


def create_app() -> TaskAPIApp:
    """Factory creating an isolated app instance with fresh repository state."""
    repo = InMemoryTaskRepository()
    return TaskAPIApp(TaskService(repo))
