# Specification: Minimal Task REST API (Dry-Run Entry Point)

> **Entry Point:** Pass this spec directly in **Antigravity App** or **`agy` CLI** (e.g., `agy "Implement specs/task_api_spec.md using the ai-sandbox-harness"`).

## Objective
Build a clean, modular, dependency-injected Task REST API under `demo_api/` obeying the active `ai-sandbox-harness` rules and skills (`python-engineering`, `fastapi-service`, `architecture-review`, `verification-loop`).

## Functional Requirements
1. `GET /health` → `200 OK` with `{"status": "ok"}`.
2. `POST /tasks` with `{"title": str (1..120 chars), "priority": "low" | "medium" | "high"}` → `201 Created` returning `{"task_id", "title", "priority", "completed": false}`.
3. `GET /tasks` → `200 OK` returning list of all tasks.
4. `GET /tasks/{task_id}` → `200 OK` if found, `404 Not Found` if missing.

## Non-Functional & Architectural Invariants
- **Layering:** Thin transport layer (`app.py`), pure service (`service.py`), `Protocol`-backed repository (`repository.py`), Pydantic v2 schemas (`schemas.py`), and domain exceptions (`errors.py`).
- **Error Mapping:** `ValidationError -> 422`, `InvalidTaskError -> 400`, `TaskNotFoundError -> 404`.
- **Verification:** Deterministic `pytest` suite in `demo_api/tests/test_api.py` covering `200`, `201`, `400`, `404`, and `422`.
