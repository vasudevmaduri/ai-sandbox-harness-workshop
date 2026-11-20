---
name: python-engineering
description: Production workflow for building, refactoring, and testing modular Python 3.11+ services with strict typing, domain isolation, exact numeric precision, and deterministic pytest suites.
---

# Python Engineering Skill

Use this skill for any Python service, library, or CLI implementation. For deep pattern tables and anti-pattern examples, consult [references/checklist.md](./references/checklist.md).

## 1. Pre-Edit Discovery
1. Read root `AGENTS.md`, any directory-scoped `GEMINI.md`, and `ARCHITECTURE.md` before writing code.
2. Query `.harness/memory/decisions.jsonl` and `.harness/memory/learnings.jsonl` for recorded Python pitfalls.
3. Map module boundaries: keep `models/` (pure data), `errors/` (domain exceptions), `repositories/` (protocols/adapters), and `services/` (orchestration) cleanly separated.

## 2. Non-Negotiable Engineering Rules
- **Strict Typing (Python 3.11+)**: Annotate all public function parameters and return types (`list[str]`, `X | None`, `Protocol`, `dataclass(frozen=True)`). Avoid untyped `dict[str, Any]` for core domain entities.
- **Exact Precision**: Use `decimal.Decimal("0.05")` with explicit `ROUND_HALF_UP` quantization for financial/monetary values. Never use `float` literals or `float()` in monetary paths.
- **Domain Exception Taxonomy**: Raise explicit domain exceptions inheriting from a service base error. Never raise raw `ValueError`, `RuntimeError`, or `Exception` for business-rule violations.
- **Dependency Injection**: Accept repositories, HTTP clients, and clocks via `__init__`; never mutate module-level global state.
- **Zero Side-Effects on Import**: Modules must not open files, network sockets, or database connections at import time.

## 3. Anti-Patterns to Reject
- `price * 0.15` (float literal) -> Use `quantize_money(price * Decimal("0.15"))`.
- `raise ValueError("invalid")` -> Use a domain exception (e.g. `InvalidInputError`).
- `global _DB; _DB = {}` -> Inject a `Protocol`-backed repository instance.

## 4. Verification Protocol
1. Add deterministic `pytest` unit tests covering:
   - Happy path with exact assertions (never `pytest.approx` on `Decimal`),
   - Boundary inputs (zero, empty collections, threshold edges),
   - Negative paths (`pytest.raises(DomainError)`).
2. Run `pytest -q` and ensure zero AST lint violations before completing the turn.
