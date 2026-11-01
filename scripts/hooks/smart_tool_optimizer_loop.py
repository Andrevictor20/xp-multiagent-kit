#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer_loop.py
Detecção de loops de ferramenta e cálculo de hash determinístico de chamadas.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.kit_constants import (  # noqa: E402
    CONTIGUOUS_READ_TTL_SECONDS,
    LOOP_HISTORY_SIZE,
    LOOP_MAX_REPEATS,
    LOOP_STATE_FILE,
    runtime_dir,
)

DEFAULT_GREP_NOISE_FILTERS = [
    "!**/node_modules/**",
    "!**/.git/**",
    "!**/__pycache__/**",
    "!**/dist/**",
    "!**/build/**",
    "!**/.next/**",
    "!**/.venv/**",
    "!**/coverage/**",
]


def get_tool_call_hash(tool_name: str, args: Dict[str, Any]) -> str:
    """Calcula um hash sha256 determinístico dos argumentos da ferramenta."""
    try:
        clean_args = json.dumps(args, sort_keys=True, ensure_ascii=False)
    except Exception:
        clean_args = str(sorted(args.items()))
    return hashlib.sha256(f"{tool_name}:{clean_args}".encode("utf-8")).hexdigest()


def _load_loop_history(history_path: Path, ttl_seconds: float) -> List[Dict[str, Any]]:
    """Carrega o histórico descartando entradas expiradas (C4: estado com TTL)."""
    if not history_path.exists():
        return []
    try:
        raw = json.loads(history_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    now = time.time()
    entries = []
    for item in raw:
        if isinstance(item, dict) and (now - float(item.get("ts", 0.0))) <= ttl_seconds:
            entries.append(item)
    return entries


def check_tool_loop(
    tool_name: str,
    args: Dict[str, Any],
    history_file: Optional[Path] = None,
    max_repeats: int = LOOP_MAX_REPEATS,
    ttl_seconds: float = CONTIGUOUS_READ_TTL_SECONDS,
) -> Tuple[bool, str]:
    """
    Rastreia chamadas repetitivas consecutivas. Se a mesma ferramenta for chamada
    max_repeats vezes dentro da janela de TTL com os mesmos argumentos, bloqueia.
    O estado vive em .agents/runtime (não em /tmp) e expira sozinho.
    """
    history_path = history_file or (runtime_dir() / LOOP_STATE_FILE)
    call_hash = get_tool_call_hash(tool_name, args)
    now = time.time()

    history = _load_loop_history(history_path, ttl_seconds)
    history.append({"hash": call_hash, "tool": tool_name, "ts": now})
    history = history[-LOOP_HISTORY_SIZE:]

    try:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(json.dumps(history), encoding="utf-8")
    except Exception:
        pass

    recent = [entry["hash"] for entry in history[-max_repeats:]]
    if len(recent) >= max_repeats and all(h == call_hash for h in recent):
        return (
            True,
            f"🚨 Loop de Ferramentas Detectado: você executou '{tool_name}' {max_repeats} vezes "
            f"consecutivas com os mesmos argumentos. Pare e analise os dados já obtidos ou "
            f"altere sua abordagem sem repetir a mesma chamada.",
        )

    return False, ""


def reset_tool_loop_history(history_file: Optional[Path] = None) -> None:
    """Limpa o histórico de detecção de loops."""
    history_path = history_file or (runtime_dir() / LOOP_STATE_FILE)
    if history_path.exists():
        try:
            history_path.unlink()
        except Exception:
            pass
