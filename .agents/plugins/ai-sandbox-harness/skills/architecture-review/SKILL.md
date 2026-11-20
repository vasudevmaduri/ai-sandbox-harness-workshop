---
name: architecture-review
description: Stack-agnostic procedure for auditing module boundaries, dependency direction, static invariants, and contract preservation against AGENTS.md and GEMINI.md.
---

# Architecture Review Skill

Use this skill for independent read-only architectural reviews across any stack:

1. **Load Contracts**: Read root `AGENTS.md`, scoped `GEMINI.md`, and `.harness/memory/decisions.jsonl`.
2. **Audit Boundaries**: Check that transport/UI layers do not bypass service layers, domain models stay pure, and infrastructure imports do not leak into domain modules.
3. **Check Static Invariants**: Verify type safety, error taxonomy, precision rules, and public API backwards compatibility.
4. **Produce Actionable Verdict**: Return `APPROVED` or `REJECTED` with exact file paths, line numbers, and concrete remediation steps.
