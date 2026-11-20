---
name: security-sandbox
description: Generic guidelines for enforcing PreToolUse sandbox boundaries, secret hygiene, command allowlists, and real-time audit telemetry across any repo.
---

# Security Sandbox Skill

Use this skill when auditing or enforcing tool and environment boundaries:

1. **Workspace Confinement**: Ensure all file reads/writes stay strictly within the active workspace root (block `../` traversal and external absolute paths).
2. **Secret Protection**: Block access to `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa`, and credential stores.
3. **Command & Deployment Guardrails**: Deny destructive commands (`rm -rf`, `del /f`, `git push --force`, `curl | sh`, `terraform apply -auto-approve`, `terraform destroy -auto-approve`).
4. **Auditability**: Inspect `.harness/telemetry/events.jsonl` to confirm every allow/deny decision is recorded.
