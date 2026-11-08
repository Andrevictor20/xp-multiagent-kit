#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer_dir_grep_write.py
Otimizações de manage_task (polling), list_dir (raiz), grep_search (filtros de ruído)
e write_to_file (bloqueio de arquivos existentes grandes).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from scripts.kit_constants import (  # noqa: E402
    MAX_TASK_STATUS_POLLS,
    WRITE_TO_FILE_MAX_LINES,
    runtime_dir,
)

from scripts.hooks.smart_tool_optimizer_state import (  # noqa: E402
    check_atdd_discipline,
    count_file_lines,
    record_file_edit,
)


def optimize_manage_task(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Bloqueia polling em loop de manage_task com Action='status'.
    Permite 1 verificação, mas barra chamadas consecutivas para a mesma tarefa.
    """
    action = str(args.get("Action", "")).strip("'\"").lower()
    task_id = str(args.get("TaskId", "")).strip()

    if action != "status":
        return "allow", "", None

    try:
        state_file = runtime_dir() / "task_poll_state.json"
        state: Dict[str, Any] = {}
        if state_file.is_file():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        last_task = state.get("last_task", "")
        streak = state.get("streak", 0)

        if last_task == task_id:
            streak += 1
        else:
            streak = 1

        state["last_task"] = task_id
        state["streak"] = streak
        state["ts"] = time.time()
        state_file.write_text(json.dumps(state), encoding="utf-8")

        if streak > MAX_TASK_STATUS_POLLS:
            return (
                "deny",
                f"🚨 Polling de manage_task(status) bloqueado (streak #{streak}). "
                f"Não faça polling em loop: o Antigravity notificará automaticamente quando a tarefa '{task_id}' for concluída. "
                f"Encerre o turno ou prossiga com outras tarefas independentes.",
                None,
            )
    except Exception:
        pass

    return "allow", "", None


def optimize_list_dir(
    args: Dict[str, Any],
    workspace_root: Optional[str] = None,
) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Bloqueia list_dir descontrolado na raiz do workspace para forçar
    o uso de REPO_MAP.md ou de subdiretórios específicos.
    """
    dir_path = args.get("DirectoryPath", "").strip()
    if not dir_path:
        return "allow", "", None

    ws_root = workspace_root or os.environ.get("WORKSPACE_ROOT") or str(Path.cwd())
    try:
        target = Path(dir_path).resolve()
        ws = Path(ws_root).resolve()
        if target == ws:
            return (
                "deny",
                "🚨 list_dir bloqueado na raiz do workspace para evitar dump de milhares de tokens. Consulte '.agents/memory/REPO_MAP.md' ou liste subdiretórios específicos (ex: scripts/, tests/, src/).",
                None,
            )
    except Exception:
        pass

    return "allow", "", None


def optimize_grep_search(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Injeta filtros de exclusão de diretórios ruidosos (node_modules, .git, etc.)
    se o parâmetro Includes estiver vazio.
    """
    from scripts.hooks.smart_tool_optimizer_loop import DEFAULT_GREP_NOISE_FILTERS  # noqa: E402

    includes = args.get("Includes")
    if not includes or len(includes) == 0:
        return (
            "allow",
            "Injetados filtros automáticos de ruído (node_modules, .git, cache) em grep_search para economizar tokens.",
            {"Includes": DEFAULT_GREP_NOISE_FILTERS},
        )
    return "allow", "", None


def optimize_write_to_file(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Bloqueia write_to_file em arquivos existentes com mais de
    WRITE_TO_FILE_MAX_LINES linhas, forçando replace_file_content com blocos
    atômicos. Permite criação de novos arquivos, arquivos pequenos e artefatos.
    """
    if args.get("ArtifactMetadata"):
        return "allow", "", None

    target_file = args.get("TargetFile")
    if not target_file:
        return "allow", "", None

    target_path = Path(target_file)
    if not target_path.exists() or not target_path.is_file():
        return "allow", "", None

    line_count = count_file_lines(target_path, max_check=WRITE_TO_FILE_MAX_LINES + 5)
    if line_count > WRITE_TO_FILE_MAX_LINES:
        try:
            total = len(target_path.read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            total = line_count
        return (
            "deny",
            f"🚨 write_to_file bloqueado em arquivo existente com mais de {WRITE_TO_FILE_MAX_LINES} linhas ({total} linhas). "
            f"Use 'replace_file_content' com blocos atômicos (< 20 linhas) para editar trechos específicos sem reenviar o arquivo inteiro, economizando milhares de tokens.",
            None,
        )

    return "allow", "", None


def record_file_edit_with_atdd(target_file: str) -> str:
    """Registra edição de arquivo e retorna o lembrete de disciplina ATDD, se houver."""
    record_file_edit(target_file)
    return check_atdd_discipline(target_file)
