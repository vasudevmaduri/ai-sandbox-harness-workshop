"""Pure domain service with dependency-injected repository."""

from task_api.errors import InvalidTaskError
from task_api.repository import TaskRepository
from task_api.schemas import CreateTaskRequest, TaskResponse

VALID_PRIORITIES = {"low", "medium", "high"}


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository
        self._counter = 0

    def create_task(self, request: CreateTaskRequest) -> TaskResponse:
        if request.priority not in VALID_PRIORITIES:
            raise InvalidTaskError(f"Priority must be one of {sorted(VALID_PRIORITIES)}.")
        self._counter += 1
        task = TaskResponse(
            task_id=f"task-{self._counter}",
            title=request.title.strip(),
            priority=request.priority,
            completed=False,
        )
        self._repo.save(task)
        return task

    def get_task(self, task_id: str) -> TaskResponse:
        return self._repo.get(task_id)

    def list_tasks(self) -> list[TaskResponse]:
        return self._repo.list_all()
