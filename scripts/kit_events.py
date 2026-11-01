#!/usr/bin/env python3
"""scripts/kit_events.py — Telemetria local estruturada e classes de falha (AC-4)
Grava JSONL compacto em .agents/runtime/events.jsonl. Limite estrito: <= 100 linhas.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def get_events_path() -> Path:
    env_dir = os.environ.get("KIT_RUNTIME_DIR")
    if env_dir:
        base = Path(env_dir).expanduser().resolve()
    else:
        try:
            from scripts.hooks.pre_tool_guard import get_runtime_dir
            base = get_runtime_dir()
        except Exception:
            base = Path(__file__).resolve().parent.parent / ".agents" / "runtime"
    base.mkdir(parents=True, exist_ok=True)
    return base / "events.jsonl"


def get_active_run_id() -> Optional[str]:
    try:
        from scripts.xp_contract import load_contract
        c = load_contract()
        return c.get("run_id") or c.get("task_id")
    except Exception:
        return None


def classify_failure(tool: str, error_text: str) -> Tuple[str, str]:
    first_line = error_text.strip().splitlines()[0] if error_text.strip() else "unknown error"
    norm_line = re.sub(r"\s+", " ", first_line.strip())
    raw_sig = f"{tool}:{norm_line}"
    sig = hashlib.sha1(raw_sig.encode("utf-8")).hexdigest()[:10]

    low = norm_line.lower()
    if any(k in low for k in ["timeout", "timed out", "deadline exceeded"]):
        cls_name = "timeout"
    elif any(k in low for k in ["unrecognized argument", "invalid argument", "usage:", "required argument"]):
        cls_name = "invalid_args"
    elif any(k in low for k in ["assertionerror", "failed", "fail:", "test failed"]):
        cls_name = "test_fail"
    elif any(k in low for k in ["permission denied", "eacces", "operation not permitted"]):
        cls_name = "permission"
    else:
        cls_name = "other"
    return cls_name, sig


def emit(kind: str, **fields: Any) -> Optional[Dict[str, Any]]:
    if os.environ.get("XP_EVENTS") == "0":
        return None

    path = get_events_path()
    if path.is_file() and path.stat().st_size >= 1024 * 1024:
        rot = path.with_name("events.1.jsonl")
        if rot.exists():
            rot.unlink()
        path.rename(rot)

    event: Dict[str, Any] = {"ts": int(time.time()), "kind": kind}
    if "run_id" not in fields:
        rid = get_active_run_id()
        if rid:
            event["run_id"] = rid

    for k, v in fields.items():
        if isinstance(v, str) and len(v) > 200:
            event[k] = v[:200]
        else:
            event[k] = v

    line = json.dumps(event, ensure_ascii=False)
    # Garante teto rígido de <= 300 B gerando JSON válido
    while len(line.encode("utf-8")) > 300:
        # Encontra o campo de string mais longo e encurta
        longest_k = max((k for k, v in event.items() if isinstance(v, str)), key=lambda k: len(event[k]), default=None)
        if longest_k and len(event[longest_k]) > 10:
            event[longest_k] = event[longest_k][:-15]
            line = json.dumps(event, ensure_ascii=False)
        else:
            break

    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return event
