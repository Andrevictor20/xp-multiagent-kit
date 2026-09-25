#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer.py
PreToolUse Hook do Antigravity para Otimização Ativa e Fatiamento de Ferramentas.
Intercepta chamadas de 'view_file' e 'run_command' via argumento 'overwrite'
para economizar até 80% do consumo de tokens na janela de contexto (IDE e CLI).
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

MAX_VIEW_LINES = 40

# Padrões de comandos verbosos que precisam de sanitização automática
VERBOSE_CMD_PATTERNS = [
    # Test runners
    r"^(?:python3?\s+-m\s+)?pytest(?:\s+|$)",
    r"^python3?\s+-m\s+unittest(?:\s+discover)?(?:\s+|$)",
    r"^(?:npm|pnpm|yarn|bun)\s+(?:test|run\s+test)(?:\s+|$)",
    r"^(?:npx\s+)?(?:jest|vitest)(?:\s+|$)",
    r"^cargo\s+test(?:\s+|$)",
    r"^go\s+test(?:\s+|$)",
    r"^mvn\s+(?:test|verify)(?:\s+|$)",
    # Git dumps
    r"^git\s+log(?:\s+|$)",
    r"^git\s+diff(?:\s+|$)",
    r"^git\s+show(?:\s+|$)",
    # File discovery
    r"^find\s+\.(?:\s+|$)",
    r"^(?:grep|rg)\s+(?:-r|-R)(?:\s+|$)",
    # Containers & Logs
    r"^docker\s+(?:logs|ps\s+-a|images)(?:\s+|$)",
    r"^kubectl\s+logs(?:\s+|$)",
    # Builds
    r"^(?:npm|pnpm|yarn|bun)\s+run\s+build(?:\s+|$)",
    r"^cargo\s+build(?:\s+|$)",
    r"^make(?:\s+|$)",
]

COMPILED_VERBOSE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in VERBOSE_CMD_PATTERNS]


def count_file_lines(file_path: Path, max_check: int = 50) -> int:
    """Conta as linhas de um arquivo de texto de forma eficiente sem carregar o arquivo inteiro."""
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


def optimize_view_file(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Analisa argumentos de view_file e aplica fatiamento cirúrgico de até 40 linhas
    se o arquivo exceder o limite ou se o intervalo for desproporcional.
    """
    path_str = args.get("AbsolutePath")
    if not path_str:
        return "allow", "", None

    target_path = Path(path_str)
    start_line = args.get("StartLine")
    end_line = args.get("EndLine")

    # Caso 1: Nenhuma linha especificada (leitura do arquivo inteiro)
    if start_line is None and end_line is None:
        total_lines = count_file_lines(target_path, max_check=MAX_VIEW_LINES + 5)
        if total_lines > MAX_VIEW_LINES:
            return (
                "allow",
                f"Clamped view_file to 40 lines (StartLine: 1, EndLine: {MAX_VIEW_LINES}) to prevent context flood.",
                {"StartLine": 1, "EndLine": MAX_VIEW_LINES},
            )
        return "allow", "", None

    # Caso 2: Apenas StartLine especificado
    if start_line is not None and end_line is None:
        clamped_end = int(start_line) + MAX_VIEW_LINES
        return (
            "allow",
            f"Clamped view_file to 40 lines window from StartLine {start_line}.",
            {"StartLine": int(start_line), "EndLine": clamped_end},
        )

    # Caso 3: Apenas EndLine especificado
    if start_line is None and end_line is not None:
        int_end = int(end_line)
        if int_end > MAX_VIEW_LINES:
            clamped_start = max(1, int_end - MAX_VIEW_LINES)
            return (
                "allow",
                f"Clamped view_file to 40 lines window ending at EndLine {int_end}.",
                {"StartLine": clamped_start, "EndLine": int_end},
            )
        return "allow", "", None

    # Caso 4: Ambos especificados, mas intervalo > 40 linhas
    if start_line is not None and end_line is not None:
        int_start = int(start_line)
        int_end = int(end_line)
        diff = int_end - int_start
        if diff > MAX_VIEW_LINES:
            clamped_end = int_start + MAX_VIEW_LINES
            return (
                "allow",
                f"Clamped view_file range from {diff} lines to {MAX_VIEW_LINES} lines.",
                {"StartLine": int_start, "EndLine": clamped_end},
            )

    return "allow", "", None


def has_output_limiter(cmd: str) -> bool:
    """Verifica se o comando já possui pipes de corte, redirecionamentos ou flags restritivas."""
    # Redirecionamentos para arquivo ou /dev/null
    if re.search(r">\s*\S+", cmd):
        return True

    # Pipes limitadores já presentes
    if re.search(r"\|\s*(?:head|tail|grep|rg|less|more|agy-sanitize)\b", cmd):
        return True

    # Flags restritivas específicas para comandos git/find
    if re.search(r"\bgit\s+log\b.*-(?:n\s*\d+|[0-9]+)\b", cmd):
        return True
    if re.search(r"\bgit\s+diff\b.*--stat\b", cmd):
        return True
    if re.search(r"\bfind\b.*-maxdepth\s+[12]\b.*\|\s*head", cmd):
        return True

    return False


def optimize_run_command(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Analisa a linha de comando e injeta sanitização com agy-sanitize se for
    um comando ruidoso sem limitadores já declarados.
    """
    cmd = args.get("CommandLine", "").strip()
    if not cmd:
        return "allow", "", None

    # Se já possui pipe ou redirecionamento para arquivo, respeita a intenção original
    if has_output_limiter(cmd):
        return "allow", "", None

    # Se o comando for encadeado ou composto por subshells complexas com pipe interno
    if "|" in cmd:
        return "allow", "", None

    # Verifica se é um comando ruidoso
    is_verbose = False
    for pat in COMPILED_VERBOSE_PATTERNS:
        if pat.search(cmd):
            is_verbose = True
            break

    if not is_verbose:
        return "allow", "", None

    # Sanitização ativa
    sanitizer_bin = "agy-sanitize"
    new_cmd = f"{cmd} | {sanitizer_bin}"

    return (
        "allow",
        f"Auto-sanitized verbose command with agy-sanitize to prevent context flood.",
        {"CommandLine": new_cmd},
    )


def optimize_tool_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ponto de entrada para processamento do payload PreToolUse."""
    tool_call = payload.get("toolCall")
    if not isinstance(tool_call, dict):
        return {"decision": "allow"}

    tool_name = tool_call.get("name", "")
    args = tool_call.get("args")
    if not isinstance(args, dict):
        return {"decision": "allow"}

    decision = "allow"
    reason = ""
    overwrite = None

    if tool_name == "view_file":
        decision, reason, overwrite = optimize_view_file(args)
    elif tool_name == "run_command":
        decision, reason, overwrite = optimize_run_command(args)

    result: Dict[str, Any] = {"decision": decision}
    if reason:
        result["reason"] = reason
    if overwrite is not None:
        result["overwrite"] = overwrite

    return result


def main() -> int:
    """Execução principal do hook PreToolUse."""
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
