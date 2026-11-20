# AI Sandbox Harness — Generic 4-Layer Plugin Policy

This plugin provides a stack-agnostic engineering harness for autonomous coding agents:

1. **Layer 1 — Context & Semantic Memory (`SessionStart`)**:
   - Auto-detects repository stacks (`python`, `fastapi`, `angular`, `terraform`, `docker/ci`), builds a concise workspace map, and injects relevant Architectural Decision Records (ADRs) from `.harness/memory/decisions.jsonl`.
2. **Layer 2 — Policy & Scope Guardrails (`PreInvocation`)**:
   - Enforces invocation turn budgets and reminds the agent of active stack contracts and sub-agent delegation rules before each model turn.
3. **Layer 3 — Hard Sandbox Controls & Observability (`PreToolUse` + `PostToolUse`)**:
   - `PreToolUse` hard-denies secret access, path traversal, and destructive shell/deployment commands.
   - `PostToolUse` runs stack-aware static checks, appends structured metrics to `.harness/telemetry/events.jsonl`, and snapshots workspace checkpoints to `.harness/checkpoints/`.
4. **Layer 4 — Verification Loop & State Recovery (`Stop`)**:
   - Intercepts agent termination, executes the detected stack's verification suite (`pytest`, `ng test`, `terraform validate`, AST/policy checks), and forces self-healing continuation (`decision: "continue"`) until green or safe rollback.
