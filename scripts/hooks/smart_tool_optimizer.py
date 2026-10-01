#!/usr/bin/env python3
"""
scripts/hooks/smart_tool_optimizer.py
PreToolUse Hook para Otimização Ativa de Ferramentas.
Intercepta 'view_file', 'run_command', 'list_dir', 'grep_search' e
'write_to_file' via 'overwrite'/'deny'.

Diretriz de custo (B1): o gasto dominante de um loop de agente é o NÚMERO de
turnos, porque cada turno reenvia system prompt + histórico completo. Um clamp
pequeno força fatiamento (N chamadas) e custa mais do que economiza: arquivos
até WHOLE_FILE_READ_MAX_LINES são lidos inteiros em UMA chamada.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

kit_dir = Path(__file__).resolve().parent.parent.parent
if str(kit_dir) not in sys.path:
    sys.path.insert(0, str(kit_dir))
if not os.environ.get("KIT_ROOT"):
    os.environ["KIT_ROOT"] = str(kit_dir)

from scripts.kit_constants import (  # noqa: E402
    CONTIGUOUS_READ_TTL_SECONDS,
    LOOP_HISTORY_SIZE,
    LOOP_MAX_REPEATS,
    LOOP_STATE_FILE,
    MAX_TASK_STATUS_POLLS,
    POST_EDIT_REREAD_TTL_SECONDS,
    SECTION_READ_MAX_LINES,
    WHOLE_FILE_READ_MAX_LINES,
    WRITE_TO_FILE_MAX_LINES,
    runtime_dir,
)

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
    # Network / API / GitHub CLI tools
    r"^(?:curl|wget|http|gh\s+(?:api|issue|pr|run|workflow|release))(?:\s+|$)",
]

COMPILED_VERBOSE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in VERBOSE_CMD_PATTERNS]


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
    """Registra que um arquivo foi editado recentemente."""
    try:
        state_file = runtime_dir() / "edit_reread_state.json"
        now = time.time()
        path_str = str(Path(target_file).resolve())
        state = {"last_edited": path_str, "edit_ts": now, "tested": False}
        state_file.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


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


def optimize_view_file(args: Dict[str, Any]) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Libera leitura integral em UMA chamada para arquivos até
    WHOLE_FILE_READ_MAX_LINES. Só acima disso aplica janela de
    SECTION_READ_MAX_LINES, evitando o fatiamento em N turnos.
    """
    path_str = args.get("AbsolutePath")
    if not path_str:
        return "allow", "", None

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
                f"Intervalo de {diff} linhas reduzido para {SECTION_READ_MAX_LINES}.{hint}",
                {"StartLine": int_start, "EndLine": int_start + SECTION_READ_MAX_LINES},
            )

    return "allow", hint.strip(), None


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
