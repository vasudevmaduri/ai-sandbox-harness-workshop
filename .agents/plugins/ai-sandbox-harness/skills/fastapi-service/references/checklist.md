# FastAPI Service Reference Checklist

## Standard Error Mapping Table
| Domain Condition | HTTP Status | Error Envelope |
| :--- | :--- | :--- |
| Resource not found | `404 Not Found` | `{"error": "not_found", "detail": "..."}` |
| Business rule / validation failure | `400 Bad Request` | `{"error": "domain_error", "detail": "..."}` |
| Duplicate / state conflict | `409 Conflict` | `{"error": "conflict", "detail": "..."}` |
| Schema validation error | `422 Unprocessable Entity` | FastAPI default structured validation list |

## Common LLM Pitfalls
1. Using Pydantic v1 `.dict()` or `@validator` instead of Pydantic v2 `.model_dump()` and `@field_validator`.
2. Raising `HTTPException` inside `service.py` (couples domain layer to HTTP transport).
3. Storing state in a module-level global dict without resetting it in `create_app()`, causing cross-test pollution.
