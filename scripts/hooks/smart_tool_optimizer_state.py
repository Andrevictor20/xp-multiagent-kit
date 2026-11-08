#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer_state.py
Funções de gestão de estado do Smart Tool Optimizer (contagem de linhas,
leituras contíguas, edições, comandos executados e releitura pós-edição).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from scripts.kit_constants import (  # noqa: E402
    CONTIGUOUS_READ_TTL_SECONDS,
    POST_EDIT_REREAD_TTL_SECONDS,
    runtime_dir,
    SECTION_READ_MAX_LINES,
    WHOLE_FILE_READ_MAX_LINES,
)


def count_file_lines(file_path: Path, max_check: int = WHOLE_FILE_READ_MAX_LINES + 1) -> int:
    """Conta as linhas de um arquivo de texto sem carregar o arquivo inteiro."""
    if not file_path.is_file():
        return 0
    try:
        count = 0
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            for _ in f:
                count += 1
                if count >= max_check:
                    break
        return count
    except Exception:
        return 0


def detect_contiguous_read(target_path: Path, start_line: Optional[int], end_line: Optional[int]) -> Optional[str]:
    """Detecta leituras sequenciais contíguas no mesmo arquivo (fatiamento cego)."""
    if start_line is None:
        return None
    try:
        state_file = runtime_dir() / "last_view_state.json"
        now = time.time()
        prev_data: Dict[str, Any] = {}
        if state_file.is_file():
            try:
                prev_data = json.loads(state_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        path_str = str(target_path.resolve())
        last_file = prev_data.get("file", "")
        last_end = prev_data.get("end_line", 0)
        last_ts = prev_data.get("ts", 0.0)
        streak = prev_data.get("streak", 0)

        curr_end = end_line if end_line is not None else (start_line + SECTION_READ_MAX_LINES)

        is_contiguous = (
            path_str == last_file
            and (now - last_ts) < CONTIGUOUS_READ_TTL_SECONDS
            and abs(start_line - last_end) <= 2
        )

        new_streak = (streak + 1) if is_contiguous else 1
        state_file.write_text(json.dumps({
            "file": path_str,
            "end_line": curr_end,
            "ts": now,
            "streak": new_streak,
        }), encoding="utf-8")

        if is_contiguous and new_streak >= 2:
            return (
                f" [Aviso: leitura contígua #{new_streak} em {target_path.name} - "
                f"o arquivo cabe em uma única leitura; peça o intervalo completo]"
            )
    except Exception:
        pass
    return None


def record_file_edit(target_file: str) -> None:
    """Registra que um arquivo foi editado recentemente e marca código como não-testado."""
    try:
        state_file = runtime_dir() / "edit_reread_state.json"
        now = time.time()
        path_str = str(Path(target_file).resolve())
        state = {"last_edited": path_str, "edit_ts": now, "tested": False}
        state_file.write_text(json.dumps(state), encoding="utf-8")

        turn_state_file = runtime_dir() / "turn_state.json"
        t_state = json.loads(turn_state_file.read_text(encoding="utf-8")) if turn_state_file.is_file() else {}
        edited = set(t_state.get("edited_files", []))
        edited.add(path_str)
        t_state["edited_files"] = sorted(edited)
        t_state["dirty_code_untested"] = True
        t_state["updated_at"] = now
        turn_state_file.write_text(json.dumps(t_state), encoding="utf-8")
    except Exception:
        pass


def check_atdd_discipline(target_file: str) -> str:
    """Informa lembrete de disciplina ATDD/BDD ao editar código de produção sem validação de testes."""
    try:
        p = Path(target_file)
        if "test" in p.name.lower() or p.suffix in (".md", ".json", ".yaml", ".yml", ".txt"):
            return ""
        if any(part in p.parts for part in ("tests", ".agents", ".gemini", "specs", "memory")):
            return ""
        turn_state_file = runtime_dir() / "turn_state.json"
        if turn_state_file.is_file():
            t_state = json.loads(turn_state_file.read_text(encoding="utf-8"))
            if t_state.get("dirty_code_untested", False):
                return "💡 [ATDD Discipline] Código de produção editado. Certifique-se de manter os testes RED correspondentes ou validar via teste antes de concluir o turno."
    except Exception:
        pass
    return ""


def record_command_run(cmd: str) -> None:
    """Registra execução de comando; reseta o flag tested se for comando de validação/teste."""
    try:
        state_file = runtime_dir() / "edit_reread_state.json"
        if state_file.is_file():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
            except Exception:
                state = {}
            state["tested"] = True
            state_file.write_text(json.dumps(state), encoding="utf-8")

        if any(k in cmd.lower() for k in ("test", "pytest", "unittest", "vitest", "jest", "cargo", "go test", "lint", "check")):
            turn_state_file = runtime_dir() / "turn_state.json"
            if turn_state_file.is_file():
                t_state = json.loads(turn_state_file.read_text(encoding="utf-8"))
                t_state["dirty_code_untested"] = False
                t_state["errors_pending"] = False
                turn_state_file.write_text(json.dumps(t_state), encoding="utf-8")
    except Exception:
        pass


def check_post_edit_reread(target_path: Path) -> Tuple[bool, str]:
    """Verifica se o arquivo recém-editado está sendo relido sem validação prévia."""
    try:
        state_file = runtime_dir() / "edit_reread_state.json"
        if not state_file.is_file():
            return False, ""
        state = json.loads(state_file.read_text(encoding="utf-8"))
        last_edited = state.get("last_edited", "")
        edit_ts = state.get("edit_ts", 0.0)
        tested = state.get("tested", False)
        now = time.time()

        if (
            str(target_path.resolve()) == last_edited
            and not tested
            and (now - edit_ts) < POST_EDIT_REREAD_TTL_SECONDS
        ):
            return True, (
                "🚨 Releitura desnecessária: o arquivo foi recém-editado com sucesso. "
                "Prossiga diretamente para a validação via teste ou próxima alteração em vez de reler o arquivo inteiro."
            )
    except Exception:
        pass
    return False, ""
