---
name: verification-loop
description: Systematic self-healing workflow for triaging PostToolUse static checks, Stop-gate test failures, telemetry metrics, and automated checkpoint rollbacks.
---

# Verification Loop Skill

Use this skill whenever `PostToolUse` or the `Stop` verification gate rejects workspace changes:

1. **Read Telemetry & Gate Output**: Inspect the exact stack verifier failure (`pytest`, `ng test`, `terraform validate`, or AST/static lint output).
2. **Triage in Order**: Fix syntax/import errors first, then architectural/static policy violations, then failing assertions.
3. **Use Checkpoints Safely**: If an edit introduces unrecoverable regressions or exhausts retries, restore the last known-good snapshot from `.harness/checkpoints/`.
4. **Record Lessons**: When a recurring pitfall is discovered, record a concise ADR in `.harness/memory/decisions.jsonl`.
