#!/usr/bin/env python3
"""Cross-platform lifecycle gate engine for the ai-sandbox-harness Antigravity plugin.

Reads Antigravity camelCase JSON hook payloads from stdin and writes contract-compliant
JSON decisions to stdout. Uses only the Python standard library so it works across
Windows, macOS, and Linux without requiring an activated virtual environment.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SENSITIVE_PATTERNS = (
    ".env",
    ".env.local",
    ".env.prod",
    ".env.production",
    "secrets.json",
    "id_rsa",
    "terraform.tfstate",
)
SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx")

DESTRUCTIVE_CMD_PATTERNS = (
    r"\brm\s+-rf\b",
    r"\bdel\s+/[fq]\b",
    r"\brmdir\s+/s\b",
    r"\bgit\s+push\s+.*--force\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bcurl\b.*\|\s*(sh|bash)\b",
    r"\bterraform\s+(apply|destroy)\b.*-auto-approve\b",
    r"\bkubectl\s+delete\s+namespace\b",
)

SECRET_CONTENT_REGEX = re.compile(
    r"""(?i)(api_key|secret_key|password|access_token)\s*=\s*['"][A-Za-z0-9_\-]{12,}['"]"""
)
FORBIDDEN_DOMAIN_EXCEPTIONS = {"ValueError", "RuntimeError", "Exception"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_workspace(payload: dict[str, Any]) -> Path:
    cwd = payload.get("cwd")
    if cwd:
        return Path(cwd).resolve()
    workspaces = payload.get("workspacePaths") or []
    if workspaces:
        return Path(workspaces[0]).resolve()
    return Path.cwd().resolve()


def _log_telemetry(workspace: Path, event: dict[str, Any]) -> None:
    try:
        telemetry_dir = workspace / ".harness" / "telemetry"
        telemetry_dir.mkdir(parents=True, exist_ok=True)
        record = {"timestamp": _now_iso(), **event}
        with (telemetry_dir / "events.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass


def detect_stacks(workspace: Path) -> list[str]:
    """Auto-detect technology stacks present in the workspace."""
    stacks: list[str] = []
    if (workspace / "pyproject.toml").exists() or list(workspace.glob("**/pyproject.toml")):
        stacks.append("python")
    if any(
        "fastapi" in p.read_text(encoding="utf-8", errors="ignore").lower()
        for p in list(workspace.glob("**/pyproject.toml"))[:5]
    ):
        stacks.append("fastapi")
    if (workspace / "angular.json").exists() or list(workspace.glob("**/angular.json")):
        stacks.append("angular")
    if list(workspace.glob("**/*.tf")):
        stacks.append("terraform")
    if (workspace / "Dockerfile").exists() or list(workspace.glob("**/Dockerfile")):
        stacks.append("deployment")
    return stacks or ["generic"]


def _load_jsonl(path: Path, limit: int = 5) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def handle_session_bootstrap(payload: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    workspace = _resolve_workspace(payload)
    stacks = detect_stacks(workspace)
    adrs = _load_jsonl(workspace / ".harness" / "memory" / "decisions.jsonl", limit=5)
    learnings = _load_jsonl(workspace / ".harness" / "memory" / "learnings.jsonl", limit=3)

    lines = [
        "[ai-sandbox-harness | SessionStart]",
        f"Detected stacks: {', '.join(stacks)}",
        "Active semantic memory (ADRs):",
    ]
    for adr in adrs:
        lines.append(f"- {adr.get('id', 'ADR')}: {adr.get('title', '')} -> {adr.get('decision', '')}")
    if learnings:
        lines.append("Recent operational learnings:")
        for lrn in learnings:
            lines.append(f"- {lrn.get('id', 'LRN')}: {lrn.get('learning', '')}")

    _log_telemetry(
        workspace,
        {
            "event": "SessionStart",
            "decision": "inject",
            "stacks": stacks,
            "adrs_injected": len(adrs),
            "learnings_injected": len(learnings),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        },
    )
    return {
        "injectSteps": [
            {"systemMessage": {"systemMessage": "\n".join(lines)}}
        ]
    }


def handle_policy_budget_gate(payload: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    workspace = _resolve_workspace(payload)
    invocation_num = int(payload.get("invocationNum", 1) or 1)
    max_invocations = int(os.getenv("HARNESS_MAX_INVOCATIONS", "25"))

    if invocation_num > max_invocations:
        _log_telemetry(
            workspace,
            {
                "event": "PreInvocation",
                "decision": "terminate",
                "invocationNum": invocation_num,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
            },
        )
        return {
            "injectSteps": [
                {
                    "errorMessage": {
                        "userMessage": f"Harness budget gate halted execution at invocation {invocation_num} (limit={max_invocations})."
                    }
                }
            ],
            "terminationBehavior": "terminate",
        }

    _log_telemetry(
        workspace,
        {
            "event": "PreInvocation",
            "decision": "allow",
            "invocationNum": invocation_num,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        },
    )
    return {"injectSteps": [], "terminationBehavior": ""}


def _extract_path_arg(args: dict[str, Any]) -> str | None:
    for key in ("Path", "path", "TargetFile", "file_path", "AbsolutePath"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _extract_cmd_arg(args: dict[str, Any]) -> str | None:
    for key in ("CommandLine", "command", "cmd"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _is_within(candidate: Path, allowed_roots: list[Path]) -> bool:
    for root in allowed_roots:
        try:
            resolved_root = root.resolve()
            if candidate == resolved_root or resolved_root in candidate.parents:
                return True
        except OSError:
            continue
    return False


def handle_sandbox_gate(payload: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    workspace = _resolve_workspace(payload)
    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name", ""))
    args = tool_call.get("args") or {}

    allowed_roots = [workspace]
    for wp in payload.get("workspacePaths") or []:
        allowed_roots.append(Path(wp))
    if payload.get("artifactDirectoryPath"):
        allowed_roots.append(Path(payload["artifactDirectoryPath"]))

    # 1. File path confinement & secret guard
    raw_path = _extract_path_arg(args)
    if raw_path:
        path_obj = Path(raw_path)
        candidate = path_obj.resolve() if path_obj.is_absolute() else (workspace / path_obj).resolve()
        name_lower = candidate.name.lower()

        if name_lower in SENSITIVE_PATTERNS or any(name_lower.endswith(s) for s in SENSITIVE_SUFFIXES):
            reason = f"PreToolUse sandbox_gate denied access to sensitive file '{candidate.name}'."
            _log_telemetry(workspace, {"event": "PreToolUse", "tool": tool_name, "decision": "deny", "reason": reason, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
            return {"decision": "deny", "reason": reason}

        if not _is_within(candidate, allowed_roots):
            reason = f"PreToolUse sandbox_gate blocked path escape outside workspace: '{raw_path}'."
            _log_telemetry(workspace, {"event": "PreToolUse", "tool": tool_name, "decision": "deny", "reason": reason, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
            return {"decision": "deny", "reason": reason}

    # 2. Shell / deployment command guard
    cmd = _extract_cmd_arg(args)
    if cmd:
        for pattern in DESTRUCTIVE_CMD_PATTERNS:
            if re.search(pattern, cmd, flags=re.IGNORECASE):
                reason = f"PreToolUse sandbox_gate blocked destructive/unapproved command matching `{pattern}`."
                _log_telemetry(workspace, {"event": "PreToolUse", "tool": tool_name, "decision": "deny", "reason": reason, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
                return {"decision": "deny", "reason": reason}

    _log_telemetry(workspace, {"event": "PreToolUse", "tool": tool_name, "decision": "allow", "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
    return {"decision": "allow"}


def _lint_file(path: Path) -> list[str]:
    violations: list[str] = []
    if not path.is_file():
        return violations
    text = path.read_text(encoding="utf-8", errors="ignore")

    if SECRET_CONTENT_REGEX.search(text):
        violations.append(f"{path.name}: Possible hardcoded secret detected.")

    if path.suffix == ".py":
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            return [f"{path.name}:{exc.lineno}: SyntaxError: {exc.msg}"]
        uses_decimal = "Decimal" in text
        is_src_module = "src" in path.parts
        for node in ast.walk(tree):
            if uses_decimal and is_src_module:
                if isinstance(node, ast.Constant) and isinstance(node.value, float):
                    violations.append(f"{path.name}:{node.lineno}: Float literal `{node.value}` in Decimal module.")
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float":
                    violations.append(f"{path.name}:{node.lineno}: `float()` call in Decimal module.")
            if is_src_module and isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                if isinstance(node.exc.func, ast.Name) and node.exc.func.id in FORBIDDEN_DOMAIN_EXCEPTIONS:
                    violations.append(f"{path.name}:{node.lineno}: Generic `{node.exc.func.id}` raised in src module.")
    elif path.suffix == ".ts":
        if re.search(r":\s*any\b", text):
            violations.append(f"{path.name}: Explicit `any` type violates strict TypeScript policy.")
    return violations


def _capture_checkpoint(workspace: Path, edited_file: Path) -> str | None:
    if not edited_file.is_file():
        return None
    try:
        ckpt_dir = workspace / ".harness" / "checkpoints"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = ckpt_dir / f"{stamp}_{edited_file.name}"
        shutil.copy2(edited_file, dest)
        return dest.name
    except OSError:
        return None


def handle_quality_telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    workspace = _resolve_workspace(payload)
    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name", ""))
    args = tool_call.get("args") or {}
    raw_path = _extract_path_arg(args)

    violations: list[str] = []
    checkpoint: str | None = None
    if raw_path:
        p = Path(raw_path)
        target = p.resolve() if p.is_absolute() else (workspace / p).resolve()
        if _is_within(target, [workspace]):
            violations = _lint_file(target)
            checkpoint = _capture_checkpoint(workspace, target)

    _log_telemetry(
        workspace,
        {
            "event": "PostToolUse",
            "tool": tool_name,
            "file": raw_path,
            "checkpoint": checkpoint,
            "violations": violations,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        },
    )
    return {}


def handle_verification_stop(payload: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    workspace = _resolve_workspace(payload)
    reason = str(payload.get("terminationReason", "NO_TOOL_CALL"))
    continuation_active = bool(payload.get("continuationActive", False))
    execution_num = int(payload.get("executionNum", 0) or 0)
    max_retries = int(os.getenv("HARNESS_MAX_STOP_RETRIES", "2"))

    # Never loop on user cancel, errors, or after max retries
    if reason != "NO_TOOL_CALL" or (continuation_active and execution_num >= max_retries):
        _log_telemetry(workspace, {"event": "Stop", "decision": "allow", "terminationReason": reason, "executionNum": execution_num, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
        return {"decision": "allow"}

    stacks = detect_stacks(workspace)
    failures: list[str] = []

    if "python" in stacks or "fastapi" in stacks:
        venv_pytest = workspace / ".venv" / "Scripts" / "pytest.exe"
        cmd = [str(venv_pytest), "-q"] if venv_pytest.exists() else [sys.executable, "-m", "pytest", "-q"]
        try:
            proc = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True, timeout=25)
            if proc.returncode != 0:
                failures.append(f"pytest failed (exit {proc.returncode}):\n{(proc.stdout + proc.stderr).strip()[:600]}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            failures.append(f"pytest execution error: {exc}")

    if failures:
        feedback = "Stop verification gate rejected exit. Fix the following before completing:\n" + "\n".join(failures)
        _log_telemetry(workspace, {"event": "Stop", "decision": "continue", "stacks": stacks, "failures": len(failures), "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
        return {"decision": "continue", "reason": feedback}

    _log_telemetry(workspace, {"event": "Stop", "decision": "allow", "stacks": stacks, "failures": 0, "latency_ms": round((time.perf_counter() - t0) * 1000, 2)})
    return {"decision": "allow"}


HANDLERS = {
    "session_bootstrap": handle_session_bootstrap,
    "policy_budget_gate": handle_policy_budget_gate,
    "sandbox_gate": handle_sandbox_gate,
    "quality_telemetry": handle_quality_telemetry,
    "verification_stop": handle_verification_stop,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in HANDLERS:
        print(json.dumps({"error": f"Usage: run_gate.py <{'|'.join(HANDLERS)}>"}))
        raise SystemExit(2)

    raw = sys.stdin.read().strip()
    payload = json.loads(raw) if raw else {}
    result = HANDLERS[sys.argv[1]](payload)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
