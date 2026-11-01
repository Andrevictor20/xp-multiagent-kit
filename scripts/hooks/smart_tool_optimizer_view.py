#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer_view.py
Otimização de view_file: leitura integral em UMA chamada para arquivos até
WHOLE_FILE_READ_MAX_LINES; janela de seção acima disso.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from scripts.kit_constants import (  # noqa: E402
    SECTION_READ_MAX_LINES,
    WHOLE_FILE_READ_MAX_LINES,
    runtime_dir,
)

from scripts.hooks.smart_tool_optimizer_state import (  # noqa: E402
    check_post_edit_reread,
    count_file_lines,
    detect_contiguous_read,
)

# Padrão para telemetria de uso de componentes via leitura de .agents/**
_COMPONENT_RE = re.compile(r"\.agents/(?:skills|agents|policies)/([^/]+)")
_COMPONENT_RE2 = re.compile(r"\.agents/([^/]+)")


def optimize_view_file(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Libera leitura integral em UMA chamada para arquivos até
    WHOLE_FILE_READ_MAX_LINES. Só acima disso aplica janela de
    SECTION_READ_MAX_LINES, evitando o fatiamento em N turnos.
    """
    path_str = args.get("AbsolutePath") or args.get("Path") or args.get("path")
    if not path_str:
        return "allow", "", None

    # B15: Telemetria de uso de componentes via leitura de .agents/**
    if ".agents" in path_str:
        try:
            m = _COMPONENT_RE.search(path_str)
            cid = m.group(1).replace(".md", "") if m else None
            if not cid:
                m2 = _COMPONENT_RE2.search(path_str)
                cid = m2.group(1).replace(".yaml", "").replace(".json", "") if m2 else None
            if cid:
                from scripts.kit_events import emit  # noqa: E402

                emit("usage", component=cid)
        except Exception:
            pass

    target_path = Path(path_str)

    # Bloqueio de releitura cega pós-edição
    reread_blocked, reread_msg = check_post_edit_reread(target_path)
    if reread_blocked:
        return "deny", reread_msg, None

    start_line = args.get("StartLine")
    end_line = args.get("EndLine")
    hint = detect_contiguous_read(target_path, start_line, end_line) or ""

    # Caso 1: leitura do arquivo inteiro - permitida até o teto de leitura única
    if start_line is None and end_line is None:
        total_lines = count_file_lines(target_path)
        if total_lines > WHOLE_FILE_READ_MAX_LINES:
            return (
                "allow",
                f"Arquivo com {total_lines}+ linhas excede o teto de leitura única "
                f"({WHOLE_FILE_READ_MAX_LINES}). Janela de {SECTION_READ_MAX_LINES} linhas "
                f"aplicada; localize o símbolo via grep_search e peça o intervalo exato.{hint}",
                {"StartLine": 1, "EndLine": SECTION_READ_MAX_LINES},
            )
        return "allow", hint.strip(), None

    # Caso 2: apenas StartLine -> completa a janela de seção
    if start_line is not None and end_line is None:
        return (
            "allow",
            f"Janela de {SECTION_READ_MAX_LINES} linhas a partir de StartLine {start_line}.{hint}",
            {"StartLine": int(start_line), "EndLine": int(start_line) + SECTION_READ_MAX_LINES},
        )

    # Caso 3: apenas EndLine -> ancora a janela terminando nele
    if start_line is None and end_line is not None:
        int_end = int(end_line)
        if int_end > SECTION_READ_MAX_LINES:
            return (
                "allow",
                f"Janela de {SECTION_READ_MAX_LINES} linhas terminando em EndLine {int_end}.{hint}",
                {"StartLine": max(1, int_end - SECTION_READ_MAX_LINES), "EndLine": int_end},
            )
        return "allow", hint.strip(), None

    # Caso 4: intervalo explícito maior que a janela de seção
    if start_line is not None and end_line is not None:
        int_start = int(start_line)
        int_end = int(end_line)
        diff = int_end - int_start
        if diff > SECTION_READ_MAX_LINES:
            return (
                "allow",
                f"Intervalo de {diff} linhas reduzido para a janela de {SECTION_READ_MAX_LINES} linhas.{hint}",
                {"StartLine": int_start, "EndLine": int_start + SECTION_READ_MAX_LINES},
            )

    return "allow", hint.strip(), None
