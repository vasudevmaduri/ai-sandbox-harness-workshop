"""Domain exceptions for the dry-run Task API."""


class TaskDomainError(Exception):
    """Base error for task domain violations."""


class TaskNotFoundError(TaskDomainError):
    """Raised when a task ID does not exist."""


class InvalidTaskError(TaskDomainError):
    """Raised when a task payload violates a domain invariant."""
