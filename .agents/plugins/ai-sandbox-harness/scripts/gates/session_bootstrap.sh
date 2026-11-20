#!/usr/bin/env sh
# SessionStart Gate: Injects detected stacks, repo map, and semantic memory ADRs.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_gate.py" session_bootstrap
