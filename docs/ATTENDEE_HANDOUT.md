# Engineering the AI Sandbox — Workshop Explainer & Command Reference

A concise reference guide for **Engineering the AI Sandbox: Context, Harnesses, and Execution Loops** using **Antigravity App** and **`agy` CLI**.

---

## 1. What Is an AI Engineering Harness?

An LLM is a fast code generator, not a self-governing engineer. A **Harness** wraps the model inside **4 deterministic engineering walls** so policy is enforced by code rather than polite prompting:

| Wall / Layer | Files in This Repo | What It Does |
| :--- | :--- | :--- |
| **Spec Entry Point** | `specs/task_api_spec.md` | Every task starts from an explicit specification instead of an ad-hoc chat prompt |
| **Wall 1: Context & Semantic Memory** | `AGENTS.md`, `.harness/memory/decisions.jsonl`, `learnings.jsonl` | `SessionStart` auto-detects the stack and injects rules, ADRs, and past learnings automatically |
| **Wall 2: Policy, Skills & 1:1 Sub-Agents** | `.agents/plugins/ai-sandbox-harness/skills/` & `agents/` | `PreInvocation` enforces turn budgets; 8 progressive skills pair 1:1 with dedicated builders and read-only auditors |
| **Wall 3: Hard Sandbox & Observability** | `hooks.json` → `sandbox_gate` (`PreToolUse`) & `quality_telemetry` (`PostToolUse`) | Blocks secret reads (`.env`), path escapes, and destructive commands (`rm -rf`, `terraform -auto-approve`); runs AST lints, snapshots checkpoints, and logs JSONL telemetry |
| **Wall 4: Verification Loop** | `hooks.json` → `verification_stop` (`Stop`) | Independently runs `pytest` on exit and forces self-healing (`decision: "continue"`) until tests pass |

> **Visual Map:** Open [docs/harness_visualizer.html](./docs/harness_visualizer.html) in any browser and click **LVL 0 → LVL 4** to inspect every actor, hook, threat vector, and 1:1 Skill ↔ Sub-Agent relationship offline.

---

## 2. Quick Setup Commands

```bash
# 1. Clone and enter the workshop repo
git clone <repo-url>
cd <repo-folder>

# 2. Verify Python & pytest baseline (demo_api)
pytest -v

# 3. Open the folder in Antigravity App, or run interactively with agy CLI:
agy "Implement specs/task_api_spec.md using the ai-sandbox-harness"
```

---

## 3. Step-by-Step Progressive Demo Commands (Levels 0 → 4)

### Level 0 — Raw LLM (All Lifecycle Hooks Disabled)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 0
```
- **What it demonstrates:** Unconstrained model behavior with zero memory, zero hard gates, and zero exit verification.

### Level 1 — Context & Semantic Memory (`SessionStart` Enabled)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 1
```
- **Test the `SessionStart` gate directly:**
  ```bash
  echo '{"cwd": "."}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py session_bootstrap
  ```
- **What it demonstrates:** Automatic stack detection (`python`, `fastapi`, `angular`, `terraform`, `deployment`) and dynamic injection of ADRs (`decisions.jsonl`) and learnings (`learnings.jsonl`).

### Level 2 — Policy Budget, Progressive Skills & 1:1 Sub-Agents (`+ PreInvocation`)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 2
```
- **Test the `PreInvocation` turn-budget gate:**
  ```bash
  echo '{"cwd": ".", "invocationNum": 3}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py policy_budget_gate
  echo '{"cwd": ".", "invocationNum": 30}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py policy_budget_gate
  ```
- **What it demonstrates:** Turn-budget enforcement + separation of duties across 8 1:1 pairs (`python-engineer`, `fastapi-engineer`, `angular-engineer`, `terraform-engineer`, `deployment-engineer`, `architecture-reviewer`, `security-auditor`, `verification-engineer`).

### Level 3 — Hard Sandbox Controls & Observability (`+ PreToolUse` & `PostToolUse`)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 3
```
- **Test `PreToolUse` hard denials directly:**
  ```bash
  # Block secret read (.env)
  echo '{"cwd": ".", "toolCall": {"name": "read_file", "args": {"Path": ".env"}}}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py sandbox_gate

  # Block destructive infra mutation
  echo '{"cwd": ".", "toolCall": {"name": "run_command", "args": {"CommandLine": "terraform apply -auto-approve"}}}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py sandbox_gate

  # Block destructive shell deletion
  echo '{"cwd": ".", "toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf demo_api"}}}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py sandbox_gate
  ```
- **Test `PostToolUse` AST lint, checkpoint snapshot & telemetry:**
  ```bash
  echo '{"cwd": ".", "toolCall": {"name": "write_file", "args": {"Path": "demo_api/src/task_api/service.py"}}}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py quality_telemetry
  ```

### Level 4 — Loop Engineering & Self-Healing Verification (`+ Stop` Gate)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 4
```
- **Test the `Stop` verification gate on `demo_api`:**
  ```bash
  echo '{"cwd": "demo_api", "terminationReason": "NO_TOOL_CALL"}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py verification_stop
  ```
- **Inspect the real-time telemetry scorecard:**
  ```bash
  python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --metrics
  ```

---

## 4. Adopting This Harness in Your Own Repository
1. Copy `.agents/plugins/ai-sandbox-harness/` into your repository root.
2. Customize `AGENTS.md` and `.harness/memory/decisions.jsonl` with your team's architectural contracts.
3. Add or extend rules in `.agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py` for your org's blocked commands and stack verifiers.
