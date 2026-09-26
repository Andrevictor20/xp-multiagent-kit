#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer.py
PreToolUse Hook do Antigravity para Otimização Ativa e Fatiamento de Ferramentas.
Intercepta chamadas de 'view_file' e 'run_command' via argumento 'overwrite'
para economizar até 80% do consumo de tokens na janela de contexto (IDE e CLI).
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

MAX_VIEW_LINES = 60

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
    r"^git\s+branch\s+-[a-zA-Z]*(?:a|r)(?:\s+|$)",
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
    # Network / API tools
    r"^(?:curl|wget|http|gh\s+api|gh\s+issue|gh\s+pr)(?:\s+|$)",
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


def detect_contiguous_read(target_path: Path, start_line: Optional[int], end_line: Optional[int]) -> Optional[str]:
    """Detecta leituras sequenciais contíguas no mesmo arquivo para alertar contra fatiamento ineficiente."""
    if start_line is None:
        return None
    try:
        state_file = Path(tempfile.gettempdir()) / ".agy_last_view_state.json"
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

        curr_end = end_line if end_line is not None else (start_line + MAX_VIEW_LINES)

        is_contiguous = (
            path_str == last_file
            and (now - last_ts) < 45.0
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
                f" [Aviso: leitura contígua #{new_streak} em {target_path.name} - considere buscar o símbolo via grep_search]"
            )
    except Exception:
        pass
    return None


def optimize_view_file(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Analisa argumentos de view_file e aplica fatiamento cirúrgico de até MAX_VIEW_LINES linhas
    se o arquivo exceder o limite ou se o intervalo for desproporcional.
    """
    path_str = args.get("AbsolutePath")
    if not path_str:
        return "allow", "", None

    target_path = Path(path_str)
    start_line = args.get("StartLine")
    end_line = args.get("EndLine")
    hint = detect_contiguous_read(target_path, start_line, end_line) or ""

    # Caso 1: Nenhuma linha especificada (leitura do arquivo inteiro)
    if start_line is None and end_line is None:
        total_lines = count_file_lines(target_path, max_check=MAX_VIEW_LINES + 5)
        if total_lines > MAX_VIEW_LINES:
            return (
                "allow",
                f"Clamped view_file to {MAX_VIEW_LINES} lines (StartLine: 1, EndLine: {MAX_VIEW_LINES}) to prevent context flood.{hint}",
                {"StartLine": 1, "EndLine": MAX_VIEW_LINES},
            )
        return "allow", hint.strip(), None

    # Caso 2: Apenas StartLine especificado
    if start_line is not None and end_line is None:
        clamped_end = int(start_line) + MAX_VIEW_LINES
        return (
            "allow",
            f"Clamped view_file to {MAX_VIEW_LINES} lines window from StartLine {start_line}.{hint}",
            {"StartLine": int(start_line), "EndLine": clamped_end},
        )

    # Caso 3: Apenas EndLine especificado
    if start_line is None and end_line is not None:
        int_end = int(end_line)
        if int_end > MAX_VIEW_LINES:
            clamped_start = max(1, int_end - MAX_VIEW_LINES)
            return (
                "allow",
                f"Clamped view_file to {MAX_VIEW_LINES} lines window ending at EndLine {int_end}.{hint}",
                {"StartLine": clamped_start, "EndLine": int_end},
            )
        return "allow", hint.strip(), None

    # Caso 4: Ambos especificados, mas intervalo > MAX_VIEW_LINES
    if start_line is not None and end_line is not None:
        int_start = int(start_line)
        int_end = int(end_line)
        diff = int_end - int_start
        if diff > MAX_VIEW_LINES:
            clamped_end = int_start + MAX_VIEW_LINES
            return (
                "allow",
                f"Clamped view_file range from {diff} lines to {MAX_VIEW_LINES} lines.{hint}",
                {"StartLine": int_start, "EndLine": clamped_end},
            )

    return "allow", hint.strip(), None


def has_output_limiter(cmd: str) -> bool:
    """Verifica se o comando já possui pipes de corte, redirecionamentos ou flags restritivas."""
    # Redirecionamentos para arquivo ou /dev/null
    if re.search(r">\s*\S+", cmd):
        return True

    # Se já tem agy-sanitize em qualquer ponto
    if "agy-sanitize" in cmd:
        return True

    # Se termina com pipe limitador explícito
    pipeline_parts = [p.strip() for p in cmd.split("|")]
    if len(pipeline_parts) > 1:
        last_part = pipeline_parts[-1]
        if re.search(r"^(?:head|tail|wc|less|more)\b", last_part):
            return True

    # Flags restritivas específicas para comandos git/find
    if re.search(r"\bgit\s+log\b.*-(?:n\s*\d+|[0-9]+)\b", cmd):
        return True
    if re.search(r"\bgit\s+diff\b.*--stat\b", cmd):
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


def optimize_run_command(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Analisa a linha de comando e injeta sanitização com agy-sanitize se for
    um comando ruidoso sem limitadores já declarados.
    """
    cmd = args.get("CommandLine", "").strip()
    if not cmd:
        return "allow", "", None

    # Se já possui pipe limitador ou redirecionamento para arquivo, respeita a intenção original
    if has_output_limiter(cmd):
        return "allow", "", None

    # Verifica se é um comando ruidoso ou pipeline sem limitador
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
        f"Auto-sanitized verbose command with agy-sanitize to prevent context flood.",
        {"CommandLine": new_cmd},
    )


DEFAULT_LOOP_HISTORY_PATH = Path("/tmp/.agy_tool_history.json")

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


def check_tool_loop(
    tool_name: str,
    args: Dict[str, Any],
    history_file: Optional[Path] = None,
    max_repeats: int = 3,
) -> Tuple[bool, str]:
    """
    Rastreia chamadas repetitivas consecutivas. Se a mesma ferramenta for chamada
    max_repeats vezes consecutivas com os mesmos argumentos, retorna loop detectado.
    """
    history_path = history_file or DEFAULT_LOOP_HISTORY_PATH
    call_hash = get_tool_call_hash(tool_name, args)

    history: list[str] = []
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except Exception:
            history = []

    history.append(call_hash)
    history = history[-10:]

    try:
        history_path.write_text(json.dumps(history), encoding="utf-8")
    except Exception:
        pass

    if len(history) >= max_repeats and all(h == call_hash for h in history[-max_repeats:]):
        return (
            True,
            f"🚨 Loop de Ferramentas Detectado: você executou '{tool_name}' {max_repeats} vezes consecutivas com os mesmos argumentos. Pare e analise os dados já obtidos ou altere sua abordagem sem repetir a mesma chamada.",
        )

    return False, ""


def reset_tool_loop_history(history_file: Optional[Path] = None) -> None:
    """Limpa o histórico de detecção de loops."""
    history_path = history_file or DEFAULT_LOOP_HISTORY_PATH
    if history_path.exists():
        try:
            history_path.unlink()
        except Exception:
            pass


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
    Bloqueia write_to_file em arquivos existentes com mais de MAX_VIEW_LINES linhas,
    forçando o uso de replace_file_content com blocos atômicos para evitar consumo massivo de tokens.
    Permite criação de novos arquivos, arquivos pequenos ou artefatos.
    """
    if args.get("ArtifactMetadata"):
        return "allow", "", None

    target_file = args.get("TargetFile")
    if not target_file:
        return "allow", "", None

    target_path = Path(target_file)
    if not target_path.exists() or not target_path.is_file():
        return "allow", "", None

    line_count = count_file_lines(target_path, max_check=MAX_VIEW_LINES + 5)
    if line_count > MAX_VIEW_LINES:
        try:
            total = len(target_path.read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            total = line_count
        return (
            "deny",
            f"🚨 write_to_file bloqueado em arquivo existente com mais de {MAX_VIEW_LINES} linhas ({total} linhas). "
            f"Use 'replace_file_content' com blocos atômicos (< 20 linhas) para editar trechos específicos sem reenviar o arquivo inteiro, economizando milhares de tokens.",
            None,
        )

    return "allow", "", None


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
        decision, reason, overwrite = optimize_run_command(args)
    elif tool_name == "list_dir":
        decision, reason, overwrite = optimize_list_dir(args)
    elif tool_name == "grep_search":
        decision, reason, overwrite = optimize_grep_search(args)
    elif tool_name == "write_to_file":
        decision, reason, overwrite = optimize_write_to_file(args)

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
