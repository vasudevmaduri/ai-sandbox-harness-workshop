"""Deterministic unit & contract tests for the dry-run Task API."""

from task_api.app import create_app


def test_health_endpoint() -> None:
    app = create_app()
    res = app.handle("GET", "/health")
    assert res.status_code == 200
    assert res.body == {"status": "ok"}


def test_create_and_fetch_task() -> None:
    app = create_app()
    created = app.handle("POST", "/tasks", {"title": "Wire Stop verification gate", "priority": "high"})
    assert created.status_code == 201
    assert isinstance(created.body, dict)
    task_id = created.body["task_id"]

    fetched = app.handle("GET", f"/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.body == {
        "task_id": task_id,
        "title": "Wire Stop verification gate",
        "priority": "high",
        "completed": False,
    }


def test_domain_and_schema_error_mapping() -> None:
    app = create_app()
    bad_priority = app.handle("POST", "/tasks", {"title": "Test", "priority": "urgent"})
    assert bad_priority.status_code == 400

    empty_title = app.handle("POST", "/tasks", {"title": ""})
    assert empty_title.status_code == 422

    missing = app.handle("GET", "/tasks/task-999")
    assert missing.status_code == 404
