#!/usr/bin/env python3
"""Workshop Level Switcher (Levels 0-4) & Real-Time Telemetry Inspector.

Allows presenters to progressively toggle Antigravity lifecycle hooks live during
a 60-minute conference workshop without manually editing hooks.json.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent
HOOKS_FILE = PLUGIN_DIR / "hooks.json"
REPO_ROOT = PLUGIN_DIR.parent.parent.parent
TELEMETRY_FILE = REPO_ROOT / ".harness" / "telemetry" / "events.jsonl"
CHECKPOINTS_DIR = REPO_ROOT / ".harness" / "checkpoints"

LEVEL_PRESETS: dict[int, tuple[str, dict[str, bool]]] = {
    0: (
        "Level 0 — Raw LLM (All Lifecycle Hooks Disabled)",
        {
            "session-context-bootstrap": False,
            "invocation-policy-gate": False,
            "sandbox-tool-boundary": False,
            "post-edit-quality-telemetry": False,
            "stop-verification-loop": False,
        },
    ),
    1: (
        "Level 1 — Context & Semantic Memory (SessionStart Enabled)",
        {
            "session-context-bootstrap": True,
            "invocation-policy-gate": False,
            "sandbox-tool-boundary": False,
            "post-edit-quality-telemetry": False,
            "stop-verification-loop": False,
        },
    ),
    2: (
        "Level 2 — Policy Guardrails + Skills/Sub-Agents (+ PreInvocation)",
        {
            "session-context-bootstrap": True,
            "invocation-policy-gate": True,
            "sandbox-tool-boundary": False,
            "post-edit-quality-telemetry": False,
            "stop-verification-loop": False,
        },
    ),
    3: (
        "Level 3 — Hard Controls & Observability (+ PreToolUse + PostToolUse)",
        {
            "session-context-bootstrap": True,
            "invocation-policy-gate": True,
            "sandbox-tool-boundary": True,
            "post-edit-quality-telemetry": True,
            "stop-verification-loop": False,
        },
    ),
    4: (
        "Level 4 — Full Loop Engineering (+ Stop Verification Gate)",
        {
            "session-context-bootstrap": True,
            "invocation-policy-gate": True,
            "sandbox-tool-boundary": True,
            "post-edit-quality-telemetry": True,
            "stop-verification-loop": True,
        },
    ),
}


def apply_level(level: int) -> None:
    label, flags = LEVEL_PRESETS[level]
    data = json.loads(HOOKS_FILE.read_text(encoding="utf-8"))
    for hook_name, enabled in flags.items():
        if hook_name in data:
            data[hook_name]["enabled"] = enabled
    HOOKS_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Switched harness to: {label}")
    for hook_name, enabled in flags.items():
        state = "ON " if enabled else "OFF"
        print(f"  [{state}] {hook_name}")


def show_metrics() -> None:
    if not TELEMETRY_FILE.is_file():
        print("No telemetry events recorded yet (.harness/telemetry/events.jsonl).")
        return
    events = [
        json.loads(line)
        for line in TELEMETRY_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_event = Counter(e.get("event", "unknown") for e in events)
    denies = [e for e in events if e.get("decision") == "deny"]
    continues = [e for e in events if e.get("decision") == "continue"]
    violations = sum(len(e.get("violations") or []) for e in events)
    checkpoints = len(list(CHECKPOINTS_DIR.glob("*"))) if CHECKPOINTS_DIR.is_dir() else 0

    print("=== AI Sandbox Harness — Real-Time Telemetry Summary ===")
    print(f"Total Hook Events : {len(events)}")
    for k, v in sorted(by_event.items()):
        print(f"  - {k:<15}: {v}")
    print(f"PreToolUse Denies : {len(denies)}")
    print(f"PostToolUse Lint  : {violations} violation(s)")
    print(f"Stop Continuations: {len(continues)}")
    print(f"Saved Checkpoints : {checkpoints}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Toggle Antigravity harness workshop levels or inspect telemetry.")
    parser.add_argument("--level", type=int, choices=[0, 1, 2, 3, 4], help="Set progressive workshop level (0-4).")
    parser.add_argument("--metrics", action="store_true", help="Print real-time telemetry summary.")
    args = parser.parse_args()

    if args.level is not None:
        apply_level(args.level)
    if args.metrics or args.level is None:
        show_metrics()


if __name__ == "__main__":
    main()
