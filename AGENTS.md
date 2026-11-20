# Engineering the AI Sandbox — Root Engineering Contract

These generic workspace rules apply across all stacks (Python, FastAPI, Angular, Terraform, and CI/CD deployments) in both **Antigravity App** and **`agy` CLI**, enforced by the `ai-sandbox-harness` plugin.

## 1. Spec-Driven Entry Point
- Every feature or workshop exercise starts from a specification document (e.g., `specs/task_api_spec.md`).
- Consult directory-scoped `GEMINI.md` contracts and `.harness/memory/decisions.jsonl` + `learnings.jsonl` before modifying files.

## 2. Security & Sandbox Boundaries (`PreToolUse`)
- Never read, print, or modify `.env`, private keys (`*.pem`, `*.key`, `id_rsa`), `terraform.tfstate`, or files outside the active workspace.
- Never execute destructive shell or deployment commands (`rm -rf`, `del /f`, `git push --force`, `curl | sh`, `terraform apply -auto-approve`, `terraform destroy -auto-approve`).

## 3. Multi-Stack Delegation & Progressive Disclosure
- Delegate stack-specific implementation and independent audits to the matching 1:1 sub-agent (`python-engineer`, `fastapi-engineer`, `angular-engineer`, `terraform-engineer`, `deployment-engineer`, `architecture-reviewer`, `security-auditor`, `verification-engineer`).
- Load deep `references/checklist.md` files only when needed for the active stack.

## 4. Verification, Observability & State Recovery (`PostToolUse` + `Stop`)
- Every file edit triggers stack-aware static checks, emits telemetry to `.harness/telemetry/events.jsonl`, and captures a recovery checkpoint in `.harness/checkpoints/`.
- Never claim a task is complete until the independent `Stop` verification gate passes.
