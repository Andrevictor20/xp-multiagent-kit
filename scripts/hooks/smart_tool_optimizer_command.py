#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer_command.py
Otimização de run_command: reescrita semântica via RTK, sanitização de
comandos verbosos com agy-sanitize e preservação de exit code (pipefail).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Padrões de comandos verbosos que precisam de sanitização automática
VERBOSE_CMD_PATTERNS = [
    # Test runners
    r"^(?:python3?\s+-m\s+)?pytest(?:\s+|$)",
    r"^python3?\s+-m\s+unittest(?:\s+discover)?(?:\s+|$)",
    r"^(?:npm|pnpm|yarn|bun)\s+(?:test|run\s+test)(?:\s+|$)",
    r"^(?:npx\s+)?(?:jest|vitest|mocha|cypress|playwright)(?:\s+|$)",
    r"^cargo\s+test(?:\s+|$)",
    r"^go\s+test(?:\s+|$)",
    r"^(?:mvn|gradle)\s+(?:test|verify|check)(?:\s+|$)",
    r"^ctest(?:\s+|$)",
    # Linters, Type Checkers & Formatters
    r"^(?:mypy|flake8|ruff|pylint|black|isort)(?:\s+|$)",
    r"^(?:npm|pnpm|yarn|bun)\s+run\s+(?:lint|check|typecheck|format)(?:\s+|$)",
    r"^(?:npx\s+)?(?:eslint|prettier|biome|tsc)(?:\s+|$)",
    r"^cargo\s+(?:clippy|check|fmt)(?:\s+|$)",
    r"^golangci-lint(?:\s+|$)",
    # Builds & Compilers
    r"^(?:npm|pnpm|yarn|bun)\s+run\s+build(?:\s+|$)",
    r"^cargo\s+build(?:\s+|$)",
    r"^(?:make|cmake|ninja|gcc|g\+\+|clang|rustc)(?:\s+|$)",
    r"^(?:mvn|gradle)\s+(?:build|package|install|compile)(?:\s+|$)",
    # Package Managers
    r"^(?:npm|pnpm|yarn|bun)\s+(?:install|i|update|add)(?:\s+|$)",
    r"^(?:pip3?|poetry|pipenv)\s+(?:install|list|freeze|check)(?:\s+|$)",
    r"^cargo\s+(?:install|add|update)(?:\s+|$)",
    # Git dumps & inspection
    r"^git\s+log(?:\s+|$)",
    r"^git\s+diff(?:\s+|$)",
    r"^git\s+show(?:\s+|$)",
    r"^git\s+blame(?:\s+|$)",
    r"^git\s+status\s+-[a-zA-Z]*v(?:\s+|$)",
    r"^git\s+branch\s+-[a-zA]*(?:a|r)(?:\s+|$)",
    # File discovery & dumps
    r"^find(?:\s+|$)",
    r"^(?:grep|rg|ag|ack)\s+",
    r"^tree(?:\s+|$)",
    r"^ls\s+-[a-zA-Z]*R(?:\s+|$)",
    # Containers & Logs
    r"^(?:docker|podman)\s+(?:logs|ps|images|build|run|compose)(?:\s+|$)",
    r"^kubectl\s+(?:logs|get|describe)(?:\s+|$)",
    # System logs & processes
    r"^(?:journalctl|dmesg|ps\s+aux|top\s+-b)(?:\s+|$)",
    # Network / API / GitHub CLI tools
    r"^(?:curl|wget|http|gh\s+(?:api|issue|pr|run|workflow|release))(?:\s+|$)",
]

COMPILED_VERBOSE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in VERBOSE_CMD_PATTERNS]


def has_output_limiter(cmd: str) -> bool:
    """Verifica se o comando já possui pipes de corte, redirecionamentos ou flags restritivas."""
    # Redirecionamentos para arquivo ou /dev/null
    if re.search(r">\s*\S+", cmd):
        return True

    # Se já tem agy-sanitize ou agy-compact em qualquer ponto
    if "agy-sanitize" in cmd or "agy-compact" in cmd:
        return True

    # Se termina com pipe limitador explícito
    pipeline_parts = [p.strip() for p in cmd.split("|")]
    if len(pipeline_parts) > 1:
        last_part = pipeline_parts[-1]
        if re.search(r"^(?:head|tail|wc|less|more)\b", last_part):
            return True

    # Flags restritivas específicas para comandos git/gh/find
    if re.search(r"\bgit\s+log\b.*-(?:n\s*\d+|[0-9]+)\b", cmd):
        return True
    if re.search(r"\bgit\s+(?:diff|show)\b.*--(?:stat|name-only|name-status)\b", cmd):
        return True
    if re.search(r"\bgh\s+run\s+list\b.*-(?:L|l|-limit)\s*\d+\b", cmd):
        return True
    if re.search(r"\bfind\b.*-maxdepth\s+[12]\b.*\|\s*head", cmd):
        return True

    return False


def strip_env_vars(segment: str) -> str:
    """Remove atribuições de variáveis de ambiente no início do comando (ex: CI=1 FOO=bar cmd)."""
    s = segment.strip()
    while True:
        m = re.match(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+", s)
        if m:
            s = s[m.end():].strip()
        else:
            break
    return s


def is_segment_verbose(seg: str) -> bool:
    """Verifica se um segmento de comando corresponde a um padrão verboso."""
    clean = strip_env_vars(seg)
    if not clean:
        return False
    for pat in COMPILED_VERBOSE_PATTERNS:
        if pat.search(clean):
            return True
    return False


def is_command_verbose(cmd: str) -> bool:
    """
    Analisa se o comando ou qualquer parte encadeada (&&, ;, ||) é verbosa,
    ou se é um pipeline sem limitador final.
    """
    # Se possui pipes, verifica se termina sem limitador
    pipeline_parts = [p.strip() for p in cmd.split("|")]
    if len(pipeline_parts) > 1:
        last = pipeline_parts[-1]
        if not re.search(r"^(?:head|tail|wc|less|more|agy-sanitize)\b", last):
            return True

    # Divide por encadeamentos lógicos &&, ||, ;
    sub_commands = re.split(r"&&|\|\||;", cmd)
    for sub in sub_commands:
        if is_segment_verbose(sub):
            return True

    return False


def try_rtk_rewrite(cmd: str) -> Optional[str]:
    """
    Consulta o RTK (Rust Token Killer v0.49.0) para reescrita semântica de comandos via 'rtk hook antigravity'.
    Retorna o comando reescrito (ex: 'rtk git status') se o RTK possuir filtro nativo,
    ou None se for passthrough/não suportado.
    """
    if cmd.startswith("rtk ") or cmd == "rtk":
        return None

    rtk_bin = shutil.which("rtk")
    if not rtk_bin:
        cand = Path.home() / ".local" / "bin" / "rtk"
        if cand.is_file() and os.access(cand, os.X_OK):
            rtk_bin = str(cand)

    if not rtk_bin:
        return None

    try:
        payload = json.dumps({"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}})
        proc = subprocess.run(
            [rtk_bin, "hook", "antigravity"],
            input=payload,
            text=True,
            capture_output=True,
            timeout=2,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            rewritten = data.get("overwrite", {}).get("CommandLine")
            if rewritten and rewritten != cmd:
                return rewritten
    except Exception:
        pass
    return None


def optimize_run_command(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Analisa a linha de comando e otimiza a execução:
    1. Tenta reescrita semântica nativa de alta performance via RTK (Rust Token Killer).
    2. Se não houver filtro RTK, injeta sanitização com agy-sanitize se for comando verboso.
    """
    cmd = args.get("CommandLine", "").strip()
    if not cmd:
        return "allow", "", None

    # Se já possui pipe limitador ou redirecionamento para arquivo, respeita a intenção original
    if has_output_limiter(cmd):
        return "allow", "", None

    # Se já é um comando rtk, permite diretamente
    if cmd.startswith("rtk ") or cmd == "rtk":
        return "allow", "", None

    # 1. Tenta reescrita semântica nativa via RTK (corta até 90% preservando falhas de teste e erros)
    rtk_rewritten = try_rtk_rewrite(cmd)
    if rtk_rewritten:
        return (
            "allow",
            "Auto-rewritten by RTK for domain-specific semantic token compression.",
            {"CommandLine": rtk_rewritten},
        )

    # 2. Se o RTK não trata esse comando, verifica se é um comando ruidoso para agy-sanitize
    if not is_command_verbose(cmd):
        return "allow", "", None

    # Sanitização ativa com preservação de exit code via pipefail
    sanitizer_bin = "agy-sanitize"
    if re.search(r"&&|\|\||;", cmd):
        new_cmd = f"set -o pipefail; ({cmd}) | {sanitizer_bin}"
    else:
        new_cmd = f"set -o pipefail; {cmd} | {sanitizer_bin}"

    return (
        "allow",
        "Auto-sanitized verbose command with agy-sanitize to prevent context flood.",
        {"CommandLine": new_cmd},
    )
