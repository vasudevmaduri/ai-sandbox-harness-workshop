#!/usr/bin/env sh
# PreInvocation Gate: Enforces invocation turn budgets and policy guardrails.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_gate.py" policy_budget_gate
