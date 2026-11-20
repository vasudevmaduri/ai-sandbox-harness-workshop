#!/usr/bin/env sh
# PreToolUse Gate: Hard-blocks secret reads, path escapes, and destructive shell/deployment commands.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_gate.py" sandbox_gate
