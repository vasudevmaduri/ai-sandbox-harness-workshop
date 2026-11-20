"""Repository protocol and in-memory adapter."""

from typing import Protocol

from task_api.errors import TaskNotFoundError
from task_api.schemas import TaskResponse


class TaskRepository(Protocol):
    def save(self, task: TaskResponse) -> None: ...
    def get(self, task_id: str) -> TaskResponse: ...
    def list_all(self) -> list[TaskResponse]: ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._store: dict[str, TaskResponse] = {}

    def save(self, task: TaskResponse) -> None:
        self._store[task.task_id] = task

    def get(self, task_id: str) -> TaskResponse:
        if task_id not in self._store:
            raise TaskNotFoundError(f"Task '{task_id}' not found.")
        return self._store[task_id]

    def list_all(self) -> list[TaskResponse]:
        return list(self._store.values())
