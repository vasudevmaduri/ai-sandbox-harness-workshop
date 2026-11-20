---
name: fastapi-service
description: Production workflow for designing, implementing, and testing FastAPI services with Pydantic v2 contracts, dependency injection, domain-to-HTTP error mapping, and isolated TestClient suites.
---

# FastAPI Service Skill

Use this skill when creating or modifying FastAPI applications, routers, schemas, or middleware. For request/response patterns and HTTP mapping tables, consult [references/checklist.md](./references/checklist.md).

## 1. Architecture & Layering
- **Thin Routers**: Route handlers only parse inputs, invoke an injected service (`Depends(get_service)`), and return a typed Pydantic v2 response model. Zero business logic or raw storage access in routers.
- **Explicit Schemas (`schemas.py`)**: Separate API DTOs (`CreateItemRequest`, `ItemResponse`) from internal domain models. Set `response_model=...` and explicit `status_code=status.HTTP_201_CREATED` (etc.) on every route.
- **Centralized Error Mapping**: Register `@app.exception_handler(DomainError)` handlers that translate domain exceptions to deterministic HTTP status codes (`400`, `404`, `409`, `422`) with a consistent JSON error envelope (`{"error": ..., "detail": ...}`). Keep `HTTPException` out of domain services.
- **App Factory (`create_app()`)**: Construct the FastAPI app inside a factory function so tests can instantiate isolated apps with fresh dependency overrides.

## 2. Security & Reliability Guardrails
- Never log raw `Authorization` headers, API keys, or `.env` values.
- Never run blocking I/O (`time.sleep`, sync `requests.get`) inside `async def` routes; use `def` routes or async clients (`httpx.AsyncClient`).
- Expose a deterministic `GET /health` endpoint returning `{"status": "ok"}`.

## 3. Verification Protocol
1. Write `TestClient(create_app())` tests in `tests/test_api.py` covering:
   - `GET /health` returns `200`,
   - `POST` creation returns `201` with validated response schema,
   - `GET` existing resource returns `200` and missing resource returns `404`,
   - Invalid payload returns `422` and domain rule violation returns `400`/`409`.
2. Run `pytest -q` and confirm zero architectural or security lint violations.
