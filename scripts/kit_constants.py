#!/usr/bin/env python3
"""
scripts/kit_constants.py
Fonte única de verdade para limites, orçamentos e padrões do XP Multi-Agent Kit.

Todo módulo do kit (hooks, sanitizadores, arquivadores, telemetria) DEVE importar
deste arquivo. Nenhuma constante de orçamento pode ser duplicada em prosa
(AGENTS.md, README.md) ou em outro script: divergência entre regras derruba a
aderência do modelo e invalida a medição.
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolução de caminhos (C2: nada de caminho absoluto de usuário)
# ---------------------------------------------------------------------------

def kit_root() -> Path:
    """Raiz do kit, resolvida por env var ou pela localização deste arquivo."""
    env_root = os.environ.get("KIT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def runtime_dir() -> Path:
    """Diretório de estado volátil (loop detection, turnos, evidências)."""
    env_dir = os.environ.get("KIT_RUNTIME_DIR")
    if env_dir:
        path = Path(env_dir).expanduser()
    else:
        path = kit_root() / ".agents" / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Leituras de arquivo (B1)
# ---------------------------------------------------------------------------
# O custo dominante de um loop de agente é o NÚMERO de turnos, não o tamanho de
# cada saída: cada turno reenvia system prompt + histórico completo. Um clamp
# pequeno demais força fatiamento (N chamadas) e custa mais do que resolve.

WHOLE_FILE_READ_MAX_LINES = 800
"""Arquivos até este tamanho são lidos inteiros em UMA chamada."""

SECTION_READ_MAX_LINES = 400
"""Janela de fatiamento por seção semântica quando o arquivo excede o teto."""

CONTIGUOUS_READ_TTL_SECONDS = 45.0
"""Janela temporal para considerar leituras consecutivas no mesmo arquivo."""

# ---------------------------------------------------------------------------
# Escritas e saídas de ferramentas
# ---------------------------------------------------------------------------

WRITE_TO_FILE_MAX_LINES = 60
"""Acima disso, write_to_file é bloqueado em arquivo existente (usar replace)."""

TOOL_OUTPUT_MAX_CHARS = 2500
TOOL_OUTPUT_MAX_LINES = 50
SANITIZE_HEAD_LINES = 10
SANITIZE_TAIL_LINES = 20

# ---------------------------------------------------------------------------
# Orçamento de turnos por nível de risco (B2)
# ---------------------------------------------------------------------------

TURN_BUDGET = {
    "L0": 3,
    "L1": 8,
    "L2": 20,
    "L3": None,  # sem teto, mas exige checkpoint atômico
}

BATCHING_REQUIRED = True
"""Chamadas de ferramenta independentes DEVEM ir no mesmo turno."""

# ---------------------------------------------------------------------------
# Loop detection (C4)
# ---------------------------------------------------------------------------

LOOP_MAX_REPEATS = 3
LOOP_HISTORY_SIZE = 10
LOOP_STATE_FILE = "tool_history.json"
MAX_TASK_STATUS_POLLS = 1
"""Máximo de chamadas consecutivas de manage_task com Action='status' antes de bloqueio."""

POST_EDIT_REREAD_TTL_SECONDS = 30.0
"""Janela temporal em que a releitura de arquivo recém-editado é considerada redundante."""

# ---------------------------------------------------------------------------
# Memória (A3)
# ---------------------------------------------------------------------------

MEMORY_INDEX_MAX_BYTES = 8192
"""Teto duro do PROJECT_MEMORY.md lido no Passo 0 (Fast Bootstrap)."""

MEMORY_INDEX_MAX_TOKENS = 2000
MEMORY_DETAILS_DIR = "details"

# ---------------------------------------------------------------------------
# Orçamento dos artefatos de contexto base (A1/A2)
# ---------------------------------------------------------------------------

AGENTS_MD_MAX_BYTES = 6000
SKILL_INDEX_LINE_MAX_CHARS = 110
SKILL_BODY_MAX_BYTES = 6000
"""Acima disso a skill deve ser fatiada em índice + seções carregáveis (E4)."""

CONTEXT_BASE_ALERT_BYTES = 30000

# ---------------------------------------------------------------------------
# Telemetria (D)
# ---------------------------------------------------------------------------

CHARS_PER_TOKEN = 4
TURN_LOG_FILE = "turn_log.jsonl"
PREFLIGHT_CONTEXT_PCT = 70.0
PREFLIGHT_QUOTA_PCT = 80.0
MIN_TURNS_FOR_RESEND_ALERT = 3
"""Amostra mínima antes de alertar sobre share de reenvio (evita falso positivo em sessão curta)."""
RESEND_SHARE_ALERT_PCT = 60.0

# ---------------------------------------------------------------------------
# Ruído de shell (B4)
# ---------------------------------------------------------------------------
# Banners de MOTD, fastfetch/neofetch e decoração de prompt custam centenas de
# tokens POR chamada de ferramenta e ficam abaixo do limiar do tool-size-guard.

BOX_DRAWING_CHARS = "╭╮╰╯│─├┤┬┴┼▀▄█▌▐░▒▓"
BLOCK_BAR_CHARS = "▰▱"

SHELL_NOISE_LINE_PATTERNS = (
    r"^[\s'.,;:c]*(?:[\\/:;,.'\"()\[\]{}|+=*_#~^<>-]{4,})[\s]*$",
    r"^.*[" + BOX_DRAWING_CHARS + r"].*$",
    r"^\s*(?:user|hname|uptime|distro|kernel|term|shell|cpu|disk|memory|network|colors|gpu|wm|de|packages)\s*[│|]?\s*\S*\s*$",
    r"^[\s]*[●○◐◑]+\s*$",
    r"^(?:Last login|There (?:are|is) \d+ zombie|System information as of)\b.*$",
    r"^\s*(?:Welcome to|Authorized uses only)\b.*$",
)

SHELL_NOISE_MIN_CONSECUTIVE = 3
"""Só remove blocos decorativos com pelo menos N linhas consecutivas de ruído."""

ASCII_ART_LETTER_DOMINANCE = 0.6
"""Fração mínima de letras repetidas para classificar uma linha como ASCII art."""

SHELL_COMPAT_WRAPPERS = {
    "fish": "bash",
    "csh": "bash",
    "tcsh": "bash",
}
"""Shells cuja sintaxe divergente causa retry caro; comandos POSIX rodam via bash."""


def user_shell() -> str:
    """Shell do usuário, sem caminho e em minúsculas."""
    return Path(os.environ.get("SHELL", "/bin/bash")).name.lower()


def needs_posix_wrapper() -> bool:
    """True quando o shell do usuário não é compatível com sintaxe POSIX/bash."""
    return user_shell() in SHELL_COMPAT_WRAPPERS


def posix_wrapper() -> str:
    """Interpretador usado para executar comandos POSIX com segurança."""
    return os.environ.get("AGY_POSIX_SHELL", "/bin/bash")
