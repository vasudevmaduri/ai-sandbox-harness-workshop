# Engineering the AI Sandbox: Workshop Explainer and Command Reference

A concise, beginner-friendly reference guide for **Engineering the AI Sandbox: Context, Harnesses, and Execution Loops** using **Antigravity App** and **`agy` CLI**.

---

## 1. Prerequisites and Zero-to-Ready Installs

No API key, credit card, or cloud billing account is required to run the harness, lifecycle gates, tests, or visualizer locally.

If you are starting on a fresh machine, install these three tools first:

1. **Python 3.11 or higher** (check with `python --version` or `python3 --version`):
   - **Windows:** `winget install Python.Python.3.12` (or download from `https://www.python.org/downloads/` and check *"Add python.exe to PATH"*)
   - **macOS:** `brew install python@3.12`
   - **Ubuntu / Debian:** `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
2. **Git** (check with `git --version`):
   - **Windows:** `winget install Git.Git` (or `https://git-scm.com/downloads`)
   - **macOS:** `brew install git` (or `xcode-select --install`)
   - **Ubuntu / Debian:** `sudo apt install -y git`
3. **Antigravity App or `agy` CLI** (for interactive agent sessions):
   - Install Antigravity and sign in with your Google account. No separate `GEMINI_API_KEY` or `.env` file is needed for this workshop.
   - *(Optional)* You can still run every lifecycle hook test, `pytest`, and the offline visualizer (`docs/harness_visualizer.html`) with Python alone even before installing Antigravity.

---

## 2. How to Install and Set Up

Run these steps once to clone the repository, create an isolated Python environment, install dependencies, and confirm everything works:

### Step 1: Clone the Repository
```bash
git clone https://github.com/vasudevmaduri/ai-sandbox-harness-workshop.git
cd ai-sandbox-harness-workshop
```

### Step 2: Create and Activate a Virtual Environment
- **macOS / Linux / Git Bash:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

### Step 3: Install Required Packages
```bash
pip install pydantic pytest
```

### Step 4: Verify Your Installation
```bash
pytest -v
```
You should see all `demo_api/tests/test_api.py` tests pass (`3 passed`).

### Step 5: Open the Workspace
- **Antigravity App:** Open the `ai-sandbox-harness-workshop` folder directly. Antigravity automatically discovers `.agents/plugins/ai-sandbox-harness/`, `AGENTS.md`, and `hooks.json`.
- **`agy` CLI:** Run from the repository root:
  ```bash
  agy "Implement specs/task_api_spec.md using the ai-sandbox-harness"
  ```
- **Interactive Visual Map:** Open [docs/harness_visualizer.html](./docs/harness_visualizer.html) in your browser and click **LVL 0** through **LVL 4** to explore every actor, hook, threat vector, and 1:1 Skill / Sub-Agent pairing offline.

> **Shell Tip:** The `echo '{...}' | python ...` commands in Section 4 work as-is in **macOS, Linux, and Git Bash**. In **Windows PowerShell**, omit `echo` and pipe the single-quoted JSON directly (for example, `'{"cwd": "."}' | python ...`).

---

## 3. What Is an AI Engineering Harness?

An LLM is a fast code generator, not a self-governing engineer. A **Harness** wraps the model inside **4 deterministic engineering walls** so policy is enforced by code rather than polite prompting:

| Wall / Layer | Files in This Repo | What It Does |
| :--- | :--- | :--- |
| **Spec Entry Point** | `specs/task_api_spec.md` | Every task starts from an explicit specification instead of an ad-hoc chat prompt |
| **Wall 1: Context and Semantic Memory** | `AGENTS.md`, `.harness/memory/decisions.jsonl`, `learnings.jsonl` | `SessionStart` auto-detects the stack and injects rules, ADRs, and past learnings automatically |
| **Wall 2: Policy, Skills, and 1:1 Sub-Agents** | `.agents/plugins/ai-sandbox-harness/skills/` and `agents/` | `PreInvocation` enforces turn budgets; 8 progressive skills pair 1:1 with dedicated builders and read-only auditors |
| **Wall 3: Hard Sandbox and Observability** | `hooks.json` -> `sandbox_gate` (`PreToolUse`) and `quality_telemetry` (`PostToolUse`) | Blocks secret reads (`.env`), path escapes, and destructive commands (`rm -rf`, `terraform -auto-approve`); runs AST lints, snapshots checkpoints, and logs JSONL telemetry |
| **Wall 4: Verification Loop** | `hooks.json` -> `verification_stop` (`Stop`) | Independently runs `pytest` on exit and forces self-healing (`decision: "continue"`) until tests pass |

---

## 4. Step-by-Step Progressive Demo Commands (Levels 0 to 4)

### Level 0: Raw LLM (All Lifecycle Hooks Disabled)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 0
```
- **What it demonstrates:** Unconstrained model behavior with zero memory, zero hard gates, and zero exit verification.

### Level 1: Context and Semantic Memory (`SessionStart` Enabled)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 1
```
- **Test the `SessionStart` gate directly:**
  ```bash
  echo '{"cwd": "."}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py session_bootstrap
  ```
- **What it demonstrates:** Automatic stack detection (`python`, `fastapi`, `angular`, `terraform`, `deployment`) and dynamic injection of ADRs (`decisions.jsonl`) and learnings (`learnings.jsonl`).

### Level 2: Policy Budget, Progressive Skills, and 1:1 Sub-Agents (`+ PreInvocation`)
```bash
python .agents/plugins/ai-sandbox-harness/scripts/harness_toggle.py --level 2
```
- **Test the `PreInvocation` turn-budget gate:**
  ```bash
  echo '{"cwd": ".", "invocationNum": 3}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py policy_budget_gate
  echo '{"cwd": ".", "invocationNum": 30}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py policy_budget_gate
  ```
- **What it demonstrates:** Turn-budget enforcement and separation of duties across 8 1:1 pairs (`python-engineer`, `fastapi-engineer`, `angular-engineer`, `terraform-engineer`, `deployment-engineer`, `architecture-reviewer`, `security-auditor`, `verification-engineer`).

### Level 3: Hard Sandbox Controls and Observability (`+ PreToolUse` and `PostToolUse`)
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
- **Test `PostToolUse` AST lint, checkpoint snapshot, and telemetry:**
  ```bash
  echo '{"cwd": ".", "toolCall": {"name": "write_file", "args": {"Path": "demo_api/src/task_api/service.py"}}}' | python .agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py quality_telemetry
  ```

### Level 4: Loop Engineering and Self-Healing Verification (`+ Stop` Gate)
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

## 5. Adopting This Harness in Your Own Repository
1. Copy `.agents/plugins/ai-sandbox-harness/` into your repository root.
2. Customize `AGENTS.md` and `.harness/memory/decisions.jsonl` with your team's architectural contracts.
3. Add or extend rules in `.agents/plugins/ai-sandbox-harness/scripts/gates/run_gate.py` for your org's blocked commands and stack verifiers.
