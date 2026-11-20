#!/usr/bin/env sh
# Stop Gate: Runs stack verification suite and forces self-healing continuation on failure.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_gate.py" verification_stop
