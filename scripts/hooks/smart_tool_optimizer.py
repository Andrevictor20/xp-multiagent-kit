#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer.py
PreToolUse Hook para Otimização Ativa de Ferramentas.
Intercepta 'view_file', 'run_command', 'list_dir', 'grep_search' e
'write_to_file' via 'overwrite'/'deny'.

Este módulo é um ponto de entrada que re-exporta as funções implementadas em
submódulos (state, view, command, loop, dir_grep_write) para preservar a API
pública usada por testes e pelo registro de hooks em .agents/hooks.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Permite execução direta como script (subprocesso do hook) adicionando a raiz
# do kit ao sys.path para resolver os pacotes `scripts.*`.
kit_dir = Path(__file__).resolve().parent.parent.parent
if str(kit_dir) not in sys.path:
    sys.path.insert(0, str(kit_dir))
if not os.environ.get("KIT_ROOT"):
    os.environ["KIT_ROOT"] = str(kit_dir)

from scripts.hooks.smart_tool_optimizer_state import (  # noqa: E402
    check_atdd_discipline,
    check_post_edit_reread,
    count_file_lines,
    detect_contiguous_read,
    record_command_run,
    record_file_edit,
)
from scripts.hooks.smart_tool_optimizer_view import (  # noqa: E402
    optimize_view_file,
)
from scripts.hooks.smart_tool_optimizer_command import (  # noqa: E402
    COMPILED_VERBOSE_PATTERNS,
    VERBOSE_CMD_PATTERNS,
    has_output_limiter,
    is_command_verbose,
    is_segment_verbose,
    optimize_run_command,
    strip_env_vars,
    try_rtk_rewrite,
)
from scripts.hooks.smart_tool_optimizer_loop import (  # noqa: E402
    DEFAULT_GREP_NOISE_FILTERS,
    check_tool_loop,
    get_tool_call_hash,
    reset_tool_loop_history,
)
from scripts.hooks.smart_tool_optimizer_dir_grep_write import (  # noqa: E402
    optimize_grep_search,
    optimize_list_dir,
    optimize_manage_task,
    optimize_write_to_file,
    record_file_edit_with_atdd,
)

# Re-exportação dos símbolos de nível de módulo usados por testes e hooks.
__all__ = [
    "optimize_tool_call",
    "optimize_view_file",
    "optimize_run_command",
    "optimize_list_dir",
    "optimize_grep_search",
    "optimize_write_to_file",
    "optimize_manage_task",
    "record_file_edit",
    "record_command_run",
    "check_tool_loop",
    "reset_tool_loop_history",
    "check_atdd_discipline",
    "count_file_lines",
    "VERBOSE_CMD_PATTERNS",
    "COMPILED_VERBOSE_PATTERNS",
    "DEFAULT_GREP_NOISE_FILTERS",
    "auto_heal_plugin_directories",
    "main",
]


def optimize_tool_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ponto de entrada para processamento do payload PreToolUse."""
    tool_call = payload.get("toolCall")
    if not isinstance(tool_call, dict):
        return {"decision": "allow"}

    tool_name = tool_call.get("name", "")
    args = tool_call.get("args")
    if not isinstance(args, dict):
        return {"decision": "allow"}

    # 1. Verificação de Loop Detection
    is_loop, loop_msg = check_tool_loop(tool_name, args)
    if is_loop:
        return {"decision": "deny", "reason": loop_msg}

    # 2. Roteamento e Otimização Específica por Ferramenta
    decision = "allow"
    reason = ""
    overwrite = None

    if tool_name == "view_file":
        decision, reason, overwrite = optimize_view_file(args)
    elif tool_name == "run_command":
        record_command_run(args.get("CommandLine", ""))
        decision, reason, overwrite = optimize_run_command(args)
    elif tool_name == "manage_task":
        decision, reason, overwrite = optimize_manage_task(args)
    elif tool_name in ("replace_file_content", "multi_replace_file_content"):
        target_f = args.get("TargetFile")
        if target_f:
            record_file_edit(target_f)
            reason = check_atdd_discipline(target_f)
    elif tool_name == "list_dir":
        decision, reason, overwrite = optimize_list_dir(args)
    elif tool_name == "grep_search":
        decision, reason, overwrite = optimize_grep_search(args)
    elif tool_name == "write_to_file":
        decision, reason, overwrite = optimize_write_to_file(args)
        if decision == "allow":
            target_f = args.get("TargetFile")
            if target_f:
                record_file_edit(target_f)
                if not reason:
                    reason = check_atdd_discipline(target_f)

    result: Dict[str, Any] = {"decision": decision}
    if reason:
        result["reason"] = reason
    if overwrite is not None:
        result["overwrite"] = overwrite

    return result


def auto_heal_plugin_directories() -> None:
    """Garante que diretórios estruturais exigidos por plugins internos existam para evitar falhas em hooks."""
    try:
        target = Path.home() / ".gemini" / "config" / "plugins" / "googlecloudtools.datacloud_telemetry"
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def main() -> int:
    """Execução principal do hook PreToolUse."""
    auto_heal_plugin_directories()
    try:
        raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw_input.strip():
            payload = json.loads(raw_input)
            result = optimize_tool_call(payload)
        else:
            result = {"decision": "allow"}
    except Exception:
        result = {"decision": "allow"}

    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
