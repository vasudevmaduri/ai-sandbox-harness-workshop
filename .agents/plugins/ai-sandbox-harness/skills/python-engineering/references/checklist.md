# Python Engineering Reference Checklist

## Layer Dependency Direction
`CLI / API Layer -> Service Layer -> Domain Models & Errors`
`Service Layer -> Repository Protocol <- Infrastructure Adapter`

- Domain models MUST NOT import `fastapi`, `requests`, `sqlite3`, `subprocess`, or `os`.
- Repositories MUST implement a `typing.Protocol` so tests can inject deterministic in-memory fakes without monkeypatching.

## Common LLM Failure Modes Caught by Harness Gates
1. **Binary Float Drift**: Writing `Decimal(0.1)` instead of `Decimal("0.1")` introduces `0.10000000000000000555...`.
2. **Exception Leakage**: Catching bare `except Exception:` and swallowing errors or returning `None` silently.
3. **Mutable Default Arguments**: Using `items: list[str] = []` instead of `tuple[str, ...] = field(default_factory=tuple)`.
4. **Test Coupling**: Sharing one repository fixture across tests causing order-dependent failures.
