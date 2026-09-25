#!/usr/bin/env python3
"""
scripts/token_tracker.py - Telemetria de Tokens para Antigravity IDE & CLI
XP Multi-Agent Kit v2

Diferencia 3 camadas essenciais de limites com exibição de <usado> / <total>:
1. Janela de Contexto por Mensagem/Sessão (Context Window)
2. Limite Móvel de 5 Horas (Rolling 5-Hour Rate Limit)
3. Limite Semanal / Ciclo de Quota (7-Day Weekly Quota)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
import ssl
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MODEL_LIMITS: Dict[str, Dict[str, int]] = {
    # Modelos Google
    "gemini-3.8-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-3.8-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-3.7-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-3.7-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-3.6-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-3.1-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-2.5-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-2.5-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-2.0-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-2.0-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-1.5-flash": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-1.5-pro": {"context_window": 2_097_152, "max_output": 65_536},
    # Modelos Anthropic
    "claude-sonnet-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-opus-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-haiku-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-7-sonnet": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-5-sonnet": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-5-haiku": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-opus": {"context_window": 200_000, "max_output": 8_192},
    # Modelos OpenAI
    "gpt-4o-mini": {"context_window": 128_000, "max_output": 16_384},
    "gpt-4o": {"context_window": 128_000, "max_output": 16_384},
    "gpt-4-turbo": {"context_window": 128_000, "max_output": 4_096},
    "o1-mini": {"context_window": 128_000, "max_output": 65_536},
    "o1": {"context_window": 200_000, "max_output": 100_000},
    "o3-mini": {"context_window": 200_000, "max_output": 100_000},
    # Modelos DeepSeek
    "deepseek-chat": {"context_window": 128_000, "max_output": 8_192},
    "deepseek-reasoner": {"context_window": 128_000, "max_output": 8_192},
    "deepseek-v3": {"context_window": 128_000, "max_output": 8_192},
    "deepseek-r1": {"context_window": 128_000, "max_output": 8_192},
    "default": {"context_window": 1_000_000, "max_output": 8_192},
}

MODEL_DISPLAY_NAMES: Dict[str, str] = {
    "gemini-3.8-flash": "Gemini 3.8 Flash",
    "gemini-3.8-pro": "Gemini 3.8 Pro",
    "gemini-3.7-flash": "Gemini 3.7 Flash",
    "gemini-3.7-pro": "Gemini 3.7 Pro",
    "gemini-3.6-flash": "Gemini 3.6 Flash",
    "gemini-3.1-pro": "Gemini 3.1 Pro",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "gemini-2.0-flash": "Gemini 2.0 Flash",
    "gemini-2.0-pro": "Gemini 2.0 Pro",
    "gemini-1.5-flash": "Gemini 1.5 Flash",
    "gemini-1.5-pro": "Gemini 1.5 Pro",
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "claude-opus-4-6": "Claude Opus 4.6",
    "claude-haiku-4-6": "Claude Haiku 4.6",
    "claude-3-7-sonnet": "Claude 3.7 Sonnet",
    "claude-3-5-sonnet": "Claude 3.5 Sonnet",
    "claude-3-5-haiku": "Claude 3.5 Haiku",
    "claude-3-opus": "Claude 3 Opus",
    "gpt-4o-mini": "GPT-4o Mini",
    "gpt-4o": "GPT-4o",
    "gpt-4-turbo": "GPT-4 Turbo",
    "o1-mini": "o1-mini",
    "o1": "o1",
    "o3-mini": "o3-mini",
    "deepseek-chat": "DeepSeek V3",
    "deepseek-reasoner": "DeepSeek R1",
    "deepseek-v3": "DeepSeek V3",
    "deepseek-r1": "DeepSeek R1",
}


def get_model_display_name(model_name: Optional[str]) -> str:
    """Retorna uma representação amigável e legível do modelo."""
    if not model_name:
        return "Unknown Model"
    clean_name = model_name.lower().strip()
    for key, display in MODEL_DISPLAY_NAMES.items():
        if key in clean_name:
            if "(high)" in clean_name:
                return f"{display} (High)"
            elif "(low)" in clean_name:
                return f"{display} (Low)"
            elif "(medium)" in clean_name:
                return f"{display} (Medium)"
            return display
    return model_name

DEFAULT_SYSTEM_PROMPT_BYTES = 85_000
DEFAULT_LIMIT_5H = 500_000        # Teto padrão de rate limit para janela de 5 horas
DEFAULT_LIMIT_WEEKLY = 10_000_000  # Teto padrão de cota semanal da conta

# Chars/token por tipo de conteúdo (BPE empirico)
_CHARS_PER_TOKEN_PROSE = 4.0   # Texto corrido: mensagens de usuário
_CHARS_PER_TOKEN_CODE = 3.2    # JSON / código / saídas de ferramentas
_CHARS_PER_TOKEN_MIXED = 3.5   # Misto: respostas do modelo (texto + código)
_CHARS_PER_TOKEN_CONFIG = 3.3  # Regras / schemas / markdown de configuração


def parse_token_limit(val: Any, default: int = 500_000) -> int:
    """Converte valores com sufixos k, M para inteiros (ex: '500k' -> 500000, '10M' -> 10000000)."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)

    s = str(val).strip().upper()
    if not s:
        return default

    multiplier = 1
    if s.endswith("K"):
        multiplier = 1_000
        s = s[:-1]
    elif s.endswith("M"):
        multiplier = 1_000_000
        s = s[:-1]
    elif s.endswith("B"):
        multiplier = 1_000_000_000
        s = s[:-1]

    try:
        return int(float(s) * multiplier)
    except ValueError:
        return default


@dataclass
class LiveQuotaBucket:
    bucket_id: str = ""
    display_name: str = ""
    description: str = ""
    window: str = ""
    remaining_fraction: float = 1.0
    reset_time: str = ""


@dataclass
class LiveServerQuota:
    is_live: bool = False
    plan_name: str = "Google AI Pro"
    gemini_5h: Optional[LiveQuotaBucket] = None
    gemini_weekly: Optional[LiveQuotaBucket] = None
    claude_5h: Optional[LiveQuotaBucket] = None
    claude_weekly: Optional[LiveQuotaBucket] = None
    description: str = ""
    error: Optional[str] = None


_LIVE_QUOTA_CACHE: Dict[str, Any] = {"timestamp": 0.0, "data": None}


def clean_refresh_text(desc: Optional[str]) -> str:
    """Converte frases longas como 'it will fully refresh in 4 hours, 49 minutes.' para formato conciso."""
    if not desc:
        return ""
    m = re.search(r"refresh in\s+([0-9]+\s+[a-z]+(?:,\s+[0-9]+\s+[a-z]+)?)", desc, re.I)
    if m:
        t = (
            m.group(1)
            .replace("days", "d")
            .replace("day", "d")
            .replace("hours", "h")
            .replace("hour", "h")
            .replace("minutes", "m")
            .replace("minute", "m")
            .replace("seconds", "s")
            .replace("second", "s")
        )
        return "renova em " + re.sub(r"\s+", " ", t).replace(" ,", ",")
    return desc


def fetch_live_antigravity_quota(force_refresh: bool = False) -> LiveServerQuota:
    """Consulta em tempo real a API oficial de cotas do Language Server do Antigravity IDE."""
    global _LIVE_QUOTA_CACHE
    now = time.time()
    if not force_refresh and _LIVE_QUOTA_CACHE["data"] is not None and (now - _LIVE_QUOTA_CACHE["timestamp"] < 10.0):
        return _LIVE_QUOTA_CACHE["data"]

    log_dirs = glob.glob(os.path.expanduser("~/.config/Antigravity IDE/logs/*/ls-main.log"))
    if not log_dirs:
        quota = LiveServerQuota(is_live=False, error="Nenhum log do Language Server encontrado")
        _LIVE_QUOTA_CACHE = {"timestamp": now, "data": quota}
        return quota

    latest_log = max(log_dirs, key=os.path.getmtime)
    csrf_token = None
    http_port = None
    https_port = None

    try:
        with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "--csrf_token" in line and not csrf_token:
                    m = re.search(r"--csrf_token\s+([a-f0-9\-]+)", line)
                    if m:
                        csrf_token = m.group(1)
                if "listening on random port at" in line:
                    m_http = re.search(r"listening on random port at (\d+) for HTTP\b", line)
                    if m_http:
                        http_port = int(m_http.group(1))
                    m_https = re.search(r"listening on random port at (\d+) for HTTPS", line)
                    if m_https:
                        https_port = int(m_https.group(1))
                if "LS started on port" in line:
                    m_start = re.search(r"LS started on port (\d+)", line)
                    if m_start:
                        https_port = int(m_start.group(1))
    except Exception as e:
        quota = LiveServerQuota(is_live=False, error=f"Erro ao ler log do LS: {e}")
        _LIVE_QUOTA_CACHE = {"timestamp": now, "data": quota}
        return quota

    if not csrf_token:
        try:
            for pid_dir in glob.glob("/proc/[0-9]*/cmdline"):
                try:
                    with open(pid_dir, "rb") as pf:
                        cmd = pf.read().replace(b"\x00", b" ").decode(errors="ignore")
                        if "language_server" in cmd and "--csrf_token" in cmd:
                            m = re.search(r"--csrf_token\s+([a-f0-9\-]+)", cmd)
                            if m:
                                csrf_token = m.group(1)
                                break
                except Exception:
                    continue
        except Exception:
            pass

    if not csrf_token:
        quota = LiveServerQuota(is_live=False, error="CSRF token do Language Server não encontrado")
        _LIVE_QUOTA_CACHE = {"timestamp": now, "data": quota}
        return quota

    ports_to_try = [p for p in [http_port, https_port] if p]
    if not ports_to_try:
        ports_to_try = [44351, 39831]

    raw_data = None
    for port in ports_to_try:
        scheme = "http" if port == http_port else "https"
        url = f"{scheme}://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary"
        ctx = ssl._create_unverified_context() if scheme == "https" else None
        req = urllib.request.Request(
            url,
            data=b"{}",
            headers={
                "Content-Type": "application/json",
                "x-codeium-csrf-token": csrf_token,
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
                raw_data = json.loads(resp.read().decode("utf-8"))
                if raw_data:
                    break
        except Exception:
            continue

    if not raw_data or "response" not in raw_data:
        quota = LiveServerQuota(is_live=False, error="Falha ao consultar RetrieveUserQuotaSummary via RPC")
        _LIVE_QUOTA_CACHE = {"timestamp": now, "data": quota}
        return quota

    res = raw_data.get("response", {})
    gem_5h = None
    gem_week = None
    claude_5h = None
    claude_week = None

    for grp in res.get("groups", []):
        grp_name = grp.get("displayName", "")
        buckets = grp.get("buckets", [])
        if "Gemini" in grp_name:
            for b in buckets:
                bid = b.get("bucketId", "")
                win = b.get("window", "")
                bucket_obj = LiveQuotaBucket(
                    bucket_id=bid,
                    display_name=b.get("displayName", ""),
                    description=b.get("description", ""),
                    window=win,
                    remaining_fraction=float(b.get("remainingFraction", 1.0)),
                    reset_time=b.get("resetTime", ""),
                )
                if win == "5h" or "5h" in bid:
                    gem_5h = bucket_obj
                elif win == "weekly" or "weekly" in bid:
                    gem_week = bucket_obj
        elif "Claude" in grp_name or "GPT" in grp_name:
            for b in buckets:
                bid = b.get("bucketId", "")
                win = b.get("window", "")
                bucket_obj = LiveQuotaBucket(
                    bucket_id=bid,
                    display_name=b.get("displayName", ""),
                    description=b.get("description", ""),
                    window=win,
                    remaining_fraction=float(b.get("remainingFraction", 1.0)),
                    reset_time=b.get("resetTime", ""),
                )
                if win == "5h" or "5h" in bid:
                    claude_5h = bucket_obj
                elif win == "weekly" or "weekly" in bid:
                    claude_week = bucket_obj

    quota = LiveServerQuota(
        is_live=True,
        plan_name="Google AI Pro",
        gemini_5h=gem_5h,
        gemini_weekly=gem_week,
        claude_5h=claude_5h,
        claude_weekly=claude_week,
        description=res.get("description", ""),
        error=None,
    )
    _LIVE_QUOTA_CACHE = {"timestamp": now, "data": quota}
    return quota


@dataclass
class RollingWindowStats:
    tokens_5h: int = 0
    conversations_5h: int = 0
    limit_5h: int = DEFAULT_LIMIT_5H
    tokens_7d: int = 0
    conversations_7d: int = 0
    limit_7d: int = DEFAULT_LIMIT_WEEKLY

    @property
    def percent_5h(self) -> float:
        return (self.tokens_5h / self.limit_5h * 100.0) if self.limit_5h else 0.0

    @property
    def remaining_5h(self) -> int:
        return max(0, self.limit_5h - self.tokens_5h)

    @property
    def percent_7d(self) -> float:
        return (self.tokens_7d / self.limit_7d * 100.0) if self.limit_7d else 0.0

    @property
    def remaining_7d(self) -> int:
        return max(0, self.limit_7d - self.tokens_7d)


@dataclass
class TokenStats:
    conversation_id: str
    model_name: str
    context_window: int
    max_output: int
    system_prompt_tokens: int
    system_prompt_bytes: int
    user_input_tokens: int
    user_input_bytes: int
    tool_tokens: int
    tool_bytes: int
    model_output_tokens: int
    model_output_bytes: int
    total_tokens: int
    remaining_tokens: int
    percent_used: float
    effort: Optional[str] = None
    rolling: RollingWindowStats = field(default_factory=RollingWindowStats)
    live_quota: LiveServerQuota = field(default_factory=LiveServerQuota)
    top_tools: Dict[str, Dict[str, int]] = field(default_factory=dict)
    steps_count: int = 0


@dataclass
class TurnStats:
    user_input_tokens: int = 0
    tool_tokens: int = 0
    model_output_tokens: int = 0
    total_tokens: int = 0


def estimate_tokens(text: Optional[str]) -> int:
    """Estima tokens para texto arbitrário via heurística BPE/SentencePiece."""
    if not text:
        return 0
    char_len = len(text)
    if char_len == 0:
        return 0
    code_chars = len(re.findall(r'[{}\[\]()<>=;:\'"`_\\\/\-\+\*&\|\$@#]', text))
    code_ratio = code_chars / char_len
    chars_per_token = 3.2 if code_ratio > 0.15 else 3.8
    return max(1, int(char_len / chars_per_token))


def _tokens_from_bytes(byte_count: int, chars_per_token: float) -> int:
    """Converte contagem de bytes para tokens usando ratio específico ao tipo de conteúdo."""
    return max(0, int(byte_count / chars_per_token))


def calculate_turn_stats(steps: List[Dict[str, Any]]) -> TurnStats:
    """Calcula os tokens consumidos exclusivamente no último turno / mensagem.

    Identifica o último USER_INPUT e mede:
    - Entrada do usuário (input)
    - Ferramentas executadas nesta resposta (tools)
    - Resposta e thinking do modelo (output)
    """
    if not steps:
        return TurnStats()

    # Localiza o índice do último USER_INPUT
    last_user_idx = -1
    for i in range(len(steps) - 1, -1, -1):
        if steps[i].get("type") == "USER_INPUT":
            last_user_idx = i
            break

    if last_user_idx == -1:
        last_user_idx = 0

    turn_steps = steps[last_user_idx:]
    user_bytes = 0
    tool_bytes = 0
    model_bytes = 0

    for step in turn_steps:
        stype = step.get("type", "UNKNOWN")
        content = step.get("content", "")
        if not isinstance(content, str):
            content = json.dumps(content) if content else ""
        step_len = len(content)

        if stype == "USER_INPUT":
            user_bytes += step_len
        elif stype == "PLANNER_RESPONSE":
            thinking = step.get("thinking", "")
            if isinstance(thinking, str):
                step_len += len(thinking)
            model_bytes += step_len
        else:
            tool_bytes += step_len

    user_tokens = _tokens_from_bytes(user_bytes, _CHARS_PER_TOKEN_PROSE)
    tool_tokens = _tokens_from_bytes(tool_bytes, _CHARS_PER_TOKEN_CODE)
    model_tokens = _tokens_from_bytes(model_bytes, _CHARS_PER_TOKEN_MIXED)
    total_tokens = user_tokens + tool_tokens + model_tokens

    return TurnStats(
        user_input_tokens=user_tokens,
        tool_tokens=tool_tokens,
        model_output_tokens=model_tokens,
        total_tokens=total_tokens,
    )


def detect_model_name_from_steps(steps: List[Dict[str, Any]]) -> Optional[str]:
    """Detecta se houve alteração ou indicação de modelo nas mensagens mais recentes do transcript."""
    if not steps:
        return None

    for step in reversed(steps):
        if step.get("type") not in ("USER_INPUT", "PLANNER_RESPONSE"):
            continue
        content = step.get("content", "")
        if not isinstance(content, str):
            content = json.dumps(content) if content else ""

        if "Model Selection" in content:
            m = re.search(
                r"Model Selection.*?\bto\s+([A-Za-z0-9\.\-\s]+?)(?:\s*\(|\.\s+[A-Z]|\n|$)",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            model_str = m.group(1).strip().lower() if m else content.lower()

            # Normalização de modelos Google
            if "gemini" in model_str:
                if "3.8" in model_str:
                    return "gemini-3.8-pro" if "pro" in model_str else "gemini-3.8-flash"
                if "3.7" in model_str:
                    return "gemini-3.7-pro" if "pro" in model_str else "gemini-3.7-flash"
                if "3.6" in model_str:
                    return "gemini-3.6-flash"
                if "3.1" in model_str:
                    return "gemini-3.1-pro"
                if "2.5" in model_str:
                    return "gemini-2.5-pro" if "pro" in model_str else "gemini-2.5-flash"
                if "2.0" in model_str:
                    return "gemini-2.0-pro" if "pro" in model_str else "gemini-2.0-flash"
                if "1.5" in model_str:
                    return "gemini-1.5-pro" if "pro" in model_str else "gemini-1.5-flash"
                return "gemini-3.8-flash"

            # Normalização de modelos Anthropic Claude
            if "claude" in model_str or "sonnet" in model_str or "opus" in model_str or "haiku" in model_str:
                if "4" in model_str or "4.6" in model_str:
                    if "opus" in model_str:
                        return "claude-opus-4-6"
                    if "haiku" in model_str:
                        return "claude-haiku-4-6"
                    return "claude-sonnet-4-6"
                if "3.7" in model_str:
                    return "claude-3-7-sonnet"
                if "3.5" in model_str:
                    if "haiku" in model_str:
                        return "claude-3-5-haiku"
                    return "claude-3-5-sonnet"
                if "opus" in model_str:
                    return "claude-3-opus"
                return "claude-sonnet-4-6"

            # Normalização de modelos OpenAI
            if "gpt-4o" in model_str:
                return "gpt-4o-mini" if "mini" in model_str else "gpt-4o"
            if "o1" in model_str:
                return "o1-mini" if "mini" in model_str else "o1"
            if "o3" in model_str:
                return "o3-mini"

            # Normalização DeepSeek
            if "deepseek" in model_str:
                if "r1" in model_str or "reasoner" in model_str:
                    return "deepseek-reasoner"
                return "deepseek-chat"

    return None


def detect_effort(
    conversation_id: str,
    steps: Optional[List[Dict[str, Any]]] = None,
    explicit_effort: Optional[str] = None,
) -> Optional[str]:
    """Detecta o nível de reasoning effort ativo (Low, Medium, High, Thinking)."""
    if explicit_effort:
        return explicit_effort.capitalize()

    # 1. Transcript steps (USER_SETTINGS_CHANGE / Model Selection)
    if steps:
        for step in reversed(steps):
            if step.get("type") != "USER_INPUT":
                continue
            content = step.get("content", "")
            if not isinstance(content, str):
                content = json.dumps(content) if content else ""
            # Evita falsos positivos em saídas de ferramentas lendo código
            if "File Path:" in content or "Created At:" in content or "diff_block_start" in content:
                continue
            if "USER_SETTINGS_CHANGE" in content and "Model Selection" in content:
                to_part = content.split("to", 1)[-1] if "to" in content else content
                m = re.search(r"\b(high|medium|low|thinking)\b", to_part, re.IGNORECASE)
                if m:
                    val = m.group(1).lower()
                    return "Thinking" if val == "thinking" else val.capitalize()
            elif step.get("source") == "USER_EXPLICIT" and ("--effort" in content.lower() or "/effort" in content.lower()):
                m = re.search(r"(?:--effort|/effort)\s+(high|medium|low)", content, re.IGNORECASE)
                if m:
                    return m.group(1).capitalize()

    # 2. Env vars
    for env_key in ("AGY_EFFORT", "REASONING_EFFORT", "EFFORT"):
        env_val = os.environ.get(env_key, "").strip().lower()
        if env_val:
            return env_val.capitalize()

    # 3. Settings files
    home = Path.home()
    for cfg_path in [
        home / ".gemini" / "antigravity-cli" / "settings.json",
        home / ".gemini" / "antigravity-ide" / "settings.json",
        home / ".gemini" / "config" / "settings.json",
    ]:
        if cfg_path.is_file():
            try:
                data = json.loads(cfg_path.read_text(encoding="utf-8"))
                eff = data.get("reasoningEffort") or data.get("effort")
                if eff and isinstance(eff, str):
                    return eff.strip().capitalize()
                mod = data.get("model", "")
                if isinstance(mod, str):
                    m = re.search(r"\b(high|medium|low|thinking)\b", mod, re.IGNORECASE)
                    if m:
                        val = m.group(1).lower()
                        return "Thinking" if val == "thinking" else val.capitalize()
            except Exception:
                pass

    return "Medium"


def _measure_system_prompt_bytes() -> int:
    """Mede o tamanho real do system prompt somando regras e schemas carregados."""
    home = Path.home()
    total = 0

    # Regras globais IDE e CLI
    for rules_root in [
        home / ".gemini" / "config" / "rules",
        home / ".gemini" / "antigravity-ide" / "builtin",
    ]:
        if rules_root.is_dir():
            for f in rules_root.rglob("*.md"):
                try:
                    total += f.stat().st_size
                except Exception:
                    pass

    # Regras do workspace (AGENTS.md / GEMINI.md)
    for ws_file in [Path("AGENTS.md"), Path("GEMINI.md"), Path(".agents/agents")]:
        if ws_file.is_file():
            try:
                total += ws_file.stat().st_size
            except Exception:
                pass

    # Overhead base: schemas de ferramentas, MCP, instruções builtin
    BASE_OVERHEAD = 45_000
    total += BASE_OVERHEAD

    return max(DEFAULT_SYSTEM_PROMPT_BYTES, total)


def get_model_limits(model_name: Optional[str]) -> Dict[str, int]:
    """Retorna a janela de contexto e limite de output para o modelo informado."""
    if not model_name:
        return MODEL_LIMITS["default"]

    clean_name = model_name.lower().strip()
    for key, limits in MODEL_LIMITS.items():
        if key in clean_name:
            return limits

    return MODEL_LIMITS["default"]


def human_tokens(count: int) -> str:
    """Converte contagem de tokens para formato legível (ex: 45.4k, 1.05M)."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.2f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}k"
    return str(count)


def calculate_rolling_windows(
    search_dirs: Optional[List[Path]] = None,
    limit_5h: Optional[int] = None,
    limit_7d: Optional[int] = None,
) -> RollingWindowStats:
    """Calcula o volume agregado de tokens consumidos nas últimas 5h e nos últimos 7 dias."""
    home = Path.home()
    if search_dirs is None:
        search_dirs = [home / ".gemini" / "antigravity-ide", home / ".gemini" / "antigravity-cli"]

    eff_limit_5h = limit_5h or parse_token_limit(os.environ.get("XP_LIMIT_5H"), DEFAULT_LIMIT_5H)
    eff_limit_7d = limit_7d or parse_token_limit(os.environ.get("XP_LIMIT_WEEKLY"), DEFAULT_LIMIT_WEEKLY)

    now = time.time()
    five_hours_ago = now - (5 * 3600)
    seven_days_ago = now - (7 * 86400)

    tokens_5h = 0
    convs_5h = 0
    tokens_7d = 0
    convs_7d = 0

    for base_dir in search_dirs:
        brain_dir = base_dir / "brain"
        if not brain_dir.is_dir():
            continue

        for conv_dir in brain_dir.iterdir():
            t_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if not t_file.is_file():
                continue

            mtime = t_file.stat().st_mtime
            if mtime < seven_days_ago:
                continue

            file_tokens = 0
            try:
                with open(t_file, "r", encoding="utf-8", errors="ignore") as fp:
                    for raw_line in fp:
                        raw_line = raw_line.strip()
                        if not raw_line:
                            continue
                        try:
                            step = json.loads(raw_line)
                            # Extrai apenas conteúdo real (não metadata JSON)
                            content = step.get("content", "") or ""
                            thinking = step.get("thinking", "") or ""
                            if not isinstance(content, str):
                                content = json.dumps(content)
                            if not isinstance(thinking, str):
                                thinking = ""
                            stype = step.get("type", "")
                            # Usa ratio correto por tipo de conteúdo
                            if stype == "PLANNER_RESPONSE":
                                file_tokens += _tokens_from_bytes(
                                    len(content) + len(thinking), _CHARS_PER_TOKEN_MIXED
                                )
                            elif stype == "USER_INPUT":
                                file_tokens += _tokens_from_bytes(len(content), _CHARS_PER_TOKEN_PROSE)
                            else:
                                file_tokens += _tokens_from_bytes(len(content), _CHARS_PER_TOKEN_CODE)
                        except Exception:
                            # Fallback conservador: linha bruta com fator de correção JSON
                            file_tokens += max(0, estimate_tokens(raw_line) // 3)
            except Exception:
                pass

            tokens_7d += file_tokens
            convs_7d += 1

            if mtime >= five_hours_ago:
                tokens_5h += file_tokens
                convs_5h += 1

    return RollingWindowStats(
        tokens_5h=tokens_5h,
        conversations_5h=convs_5h,
        limit_5h=eff_limit_5h,
        tokens_7d=tokens_7d,
        conversations_7d=convs_7d,
        limit_7d=eff_limit_7d,
    )


def parse_transcript_data(
    conversation_id: str,
    model_name: str,
    steps: List[Dict[str, Any]],
    system_prompt_bytes: int = 0,
    rolling: Optional[RollingWindowStats] = None,
    live_quota: Optional[LiveServerQuota] = None,
    fetch_live: bool = False,
    effort: Optional[str] = None,
) -> TokenStats:
    """Processa steps do transcript e consolida telemetria em 3 camadas.

    Correções aplicadas:
    - Ignora steps com is_truncated=True (não consomem contexto ativo)
    - CONVERSATION_HISTORY conta apenas 50% (é compressão de conteúdo já registrado)
    - Usa ratio chars/token específico por tipo de conteúdo
    - Mede system prompt dinamicamente se não fornecido
    """
    limits = get_model_limits(model_name)

    # Mede o system prompt real se não fornecido
    eff_sys_bytes = system_prompt_bytes if system_prompt_bytes > 0 else _measure_system_prompt_bytes()
    sys_tokens = _tokens_from_bytes(eff_sys_bytes, _CHARS_PER_TOKEN_CONFIG)

    user_bytes = 0
    tool_bytes = 0
    model_bytes = 0
    tool_breakdown: Dict[str, Dict[str, int]] = {}
    active_steps = 0

    for step in steps:
        stype = step.get("type", "UNKNOWN")

        # Pula steps truncados — foram removidos da janela de contexto ativa
        if step.get("is_truncated", False):
            continue

        content = step.get("content", "")
        if not isinstance(content, str):
            content = json.dumps(content) if content else ""

        step_len = len(content)
        active_steps += 1

        if stype == "USER_INPUT":
            user_bytes += step_len

        elif stype == "PLANNER_RESPONSE":
            thinking = step.get("thinking", "")
            if isinstance(thinking, str):
                step_len += len(thinking)
            model_bytes += step_len

        elif stype == "CONVERSATION_HISTORY":
            # É compressão de turnos antigos já contados → peso 50% para evitar double-count
            user_bytes += step_len // 2

        elif stype in ("CHECKPOINT", "KNOWLEDGE_ARTIFACTS"):
            # Novo contexto injetado, conta integral
            user_bytes += step_len

        else:
            tool_bytes += step_len
            if stype not in tool_breakdown:
                tool_breakdown[stype] = {"bytes": 0, "tokens": 0, "calls": 0}
            tool_breakdown[stype]["bytes"] += step_len
            tool_breakdown[stype]["calls"] += 1

    # Aplica ratio correto por tipo (prose=4.0, code=3.2, mixed=3.5)
    user_tokens = _tokens_from_bytes(user_bytes, _CHARS_PER_TOKEN_PROSE)
    tool_tokens = _tokens_from_bytes(tool_bytes, _CHARS_PER_TOKEN_CODE)
    model_tokens = _tokens_from_bytes(model_bytes, _CHARS_PER_TOKEN_MIXED)

    for t_name, t_data in tool_breakdown.items():
        t_data["tokens"] = _tokens_from_bytes(t_data["bytes"], _CHARS_PER_TOKEN_CODE)

    sorted_tools = dict(
        sorted(tool_breakdown.items(), key=lambda item: item[1]["bytes"], reverse=True)
    )

    total_tokens = sys_tokens + user_tokens + tool_tokens + model_tokens
    remaining = max(0, limits["context_window"] - total_tokens)
    pct = (total_tokens / limits["context_window"]) * 100.0 if limits["context_window"] else 0.0

    if live_quota is None and fetch_live:
        live_quota = fetch_live_antigravity_quota()
    else:
        live_quota = live_quota or LiveServerQuota(is_live=False)

    if effort is None:
        effort = detect_effort(conversation_id, steps=steps)

    return TokenStats(
        conversation_id=conversation_id,
        model_name=model_name,
        context_window=limits["context_window"],
        max_output=limits["max_output"],
        effort=effort,
        system_prompt_tokens=sys_tokens,
        system_prompt_bytes=eff_sys_bytes,
        user_input_tokens=user_tokens,
        user_input_bytes=user_bytes,
        tool_tokens=tool_tokens,
        tool_bytes=tool_bytes,
        model_output_tokens=model_tokens,
        model_output_bytes=model_bytes,
        total_tokens=total_tokens,
        remaining_tokens=remaining,
        percent_used=pct,
        rolling=rolling or RollingWindowStats(),
        live_quota=live_quota,
        top_tools=sorted_tools,
        steps_count=active_steps,
    )



def format_badge(stats: TokenStats) -> str:
    """Gera um badge markdown exibindo telemetria para Janela, 5h e Semanal."""
    tot_str = human_tokens(stats.total_tokens)
    win_str = human_tokens(stats.context_window)

    if stats.live_quota and stats.live_quota.is_live:
        is_gemini = "gemini" in stats.model_name.lower()
        b_5h = stats.live_quota.gemini_5h if is_gemini else stats.live_quota.claude_5h
        b_7d = stats.live_quota.gemini_weekly if is_gemini else stats.live_quota.claude_weekly
        pct_5h_rem = (b_5h.remaining_fraction * 100.0) if b_5h else 100.0
        pct_7d_rem = (b_7d.remaining_fraction * 100.0) if b_7d else 100.0
        return (
            f"📊 **Token Telemetry ({stats.model_name}):** `{tot_str}/{win_str}` ({stats.percent_used:.1f}%) "
            f"| **5h:** `{pct_5h_rem:.1f}% restante` "
            f"| **Semana:** `{pct_7d_rem:.1f}% restante`"
        )

    r5h_used = human_tokens(stats.rolling.tokens_5h)
    r5h_tot = human_tokens(stats.rolling.limit_5h)
    r7d_used = human_tokens(stats.rolling.tokens_7d)
    r7d_tot = human_tokens(stats.rolling.limit_7d)
    return (
        f"📊 **Token Telemetry ({stats.model_name}):** `{tot_str}/{win_str}` ({stats.percent_used:.1f}%) "
        f"| **5h:** `{r5h_used}/{r5h_tot}` ({stats.rolling.percent_5h:.1f}%) "
        f"| **Semana:** `{r7d_used}/{r7d_tot}` ({stats.rolling.percent_7d:.1f}%)"
    )


def format_message_footer(stats: TokenStats, turn: TurnStats) -> str:
    """Gera rodapé markdown elegante exibindo o consumo desta mensagem e a telemetria acumulada."""
    display_model = get_model_display_name(stats.model_name)
    turn_tot = human_tokens(turn.total_tokens)
    turn_in = human_tokens(turn.user_input_tokens)
    turn_tools = human_tokens(turn.tool_tokens)
    turn_out = human_tokens(turn.model_output_tokens)
    tool_warn = " ⚠️ [Alto Uso de Ferramentas: use agy-sanitize/fatiamento]" if turn.tool_tokens > 1500 else ""

    tot_str = human_tokens(stats.total_tokens)
    win_str = human_tokens(stats.context_window)
    max_out_str = human_tokens(stats.max_output)

    effort_tag = f" (Effort: `{stats.effort}`)" if stats.effort else ""

    if stats.live_quota and stats.live_quota.is_live:
        is_gemini = "gemini" in stats.model_name.lower()
        b_5h = stats.live_quota.gemini_5h if is_gemini else stats.live_quota.claude_5h
        b_7d = stats.live_quota.gemini_weekly if is_gemini else stats.live_quota.claude_weekly

        pct_5h_rem = (b_5h.remaining_fraction * 100.0) if b_5h else 100.0
        pct_7d_rem = (b_7d.remaining_fraction * 100.0) if b_7d else 100.0

        desc_5h = clean_refresh_text(b_5h.description) if b_5h else ""
        desc_7d = clean_refresh_text(b_7d.description) if b_7d else ""

        s_5h = f"{pct_5h_rem:.1f}% restante" + (f" ({desc_5h})" if desc_5h else "")
        s_7d = f"{pct_7d_rem:.1f}% restante" + (f" ({desc_7d})" if desc_7d else "")

        return (
            f"---\n"
            f"🪙 **Consumo Desta Mensagem:** ~`{turn_tot}` tokens "
            f"(Entrada: `{turn_in}` | Ferramentas: `{turn_tools}`{tool_warn} | Resposta: `{turn_out}`)\n"
            f"📊 **Telemetria Acumulada ({display_model}):** "
            f"Contexto: `{tot_str}/{win_str}` ({stats.percent_used:.1f}%) | "
            f"5h: `{s_5h}` | "
            f"Semana: `{s_7d}`\n"
            f"🎯 **Modelo & Limites:** `{display_model}`{effort_tag} | Janela: `{win_str}` | Saída Máx: `{max_out_str}`"
        )

    r5h_used = human_tokens(stats.rolling.tokens_5h)
    r5h_tot = human_tokens(stats.rolling.limit_5h)
    r7d_used = human_tokens(stats.rolling.tokens_7d)
    r7d_tot = human_tokens(stats.rolling.limit_7d)

    return (
        f"---\n"
        f"🪙 **Consumo Desta Mensagem:** ~`{turn_tot}` tokens "
        f"(Entrada: `{turn_in}` | Ferramentas: `{turn_tools}`{tool_warn} | Resposta: `{turn_out}`)\n"
        f"📊 **Telemetria Acumulada ({display_model}):** "
        f"Contexto: `{tot_str}/{win_str}` ({stats.percent_used:.1f}%) | "
        f"5h: `{r5h_used}/{r5h_tot}` ({stats.rolling.percent_5h:.1f}%) | "
        f"Semana: `{r7d_used}/{r7d_tot}` ({stats.rolling.percent_7d:.1f}%)\n"
        f"🎯 **Modelo & Limites:** `{display_model}`{effort_tag} | Janela: `{win_str}` | Saída Máx: `{max_out_str}`"
    )


def format_json_stats(stats: TokenStats) -> str:
    """Exporta as métricas de telemetria em formato JSON estruturado com os tetos <usado>/<total>."""
    display_model = get_model_display_name(stats.model_name)
    payload = {
        "conversation_id": stats.conversation_id,
        "model": stats.model_name,
        "model_display_name": display_model,
        "effort": stats.effort,
        "model_limits": {
            "context_window": stats.context_window,
            "max_output": stats.max_output,
            "context_window_human": human_tokens(stats.context_window),
            "max_output_human": human_tokens(stats.max_output),
        },
        "context_window": stats.context_window,
        "max_output": stats.max_output,
        "total_tokens": stats.total_tokens,
        "remaining_tokens": stats.remaining_tokens,
        "percent_used": round(stats.percent_used, 2),
        "steps_count": stats.steps_count,
        "live_server_quota": {
            "is_live": stats.live_quota.is_live,
            "plan_name": stats.live_quota.plan_name,
            "gemini_5h_remaining_pct": round(stats.live_quota.gemini_5h.remaining_fraction * 100.0, 2) if stats.live_quota.gemini_5h else None,
            "gemini_5h_refresh": clean_refresh_text(stats.live_quota.gemini_5h.description) if stats.live_quota.gemini_5h else None,
            "gemini_weekly_remaining_pct": round(stats.live_quota.gemini_weekly.remaining_fraction * 100.0, 2) if stats.live_quota.gemini_weekly else None,
            "gemini_weekly_refresh": clean_refresh_text(stats.live_quota.gemini_weekly.description) if stats.live_quota.gemini_weekly else None,
            "claude_5h_remaining_pct": round(stats.live_quota.claude_5h.remaining_fraction * 100.0, 2) if stats.live_quota.claude_5h else None,
            "claude_5h_refresh": clean_refresh_text(stats.live_quota.claude_5h.description) if stats.live_quota.claude_5h else None,
            "claude_weekly_remaining_pct": round(stats.live_quota.claude_weekly.remaining_fraction * 100.0, 2) if stats.live_quota.claude_weekly else None,
            "claude_weekly_refresh": clean_refresh_text(stats.live_quota.claude_weekly.description) if stats.live_quota.claude_weekly else None,
            "error": stats.live_quota.error,
        },
        "rolling_limits": {
            "tokens_5h": stats.rolling.tokens_5h,
            "limit_5h": stats.rolling.limit_5h,
            "percent_5h": round(stats.rolling.percent_5h, 2),
            "remaining_5h": stats.rolling.remaining_5h,
            "conversations_5h": stats.rolling.conversations_5h,
            "tokens_7d": stats.rolling.tokens_7d,
            "limit_7d": stats.rolling.limit_7d,
            "percent_7d": round(stats.rolling.percent_7d, 2),
            "remaining_7d": stats.rolling.remaining_7d,
            "conversations_7d": stats.rolling.conversations_7d,
        },
        "breakdown": {
            "system_prompt": {
                "tokens": stats.system_prompt_tokens,
                "bytes": stats.system_prompt_bytes,
            },
            "user_input": {
                "tokens": stats.user_input_tokens,
                "bytes": stats.user_input_bytes,
            },
            "tools": {
                "tokens": stats.tool_tokens,
                "bytes": stats.tool_bytes,
                "top_tools": stats.top_tools,
            },
            "model_output": {
                "tokens": stats.model_output_tokens,
                "bytes": stats.model_output_bytes,
            },
        },
    }
    return json.dumps(payload, indent=2)


def format_markdown_report(stats: TokenStats) -> str:
    """Gera o relatório visual em Markdown para TOKEN_TELEMETRY.md cobrindo <usado>/<total>."""
    status_emoji = "🟢 Saudável"
    if stats.percent_used >= 80 or stats.rolling.percent_5h >= 80 or stats.rolling.percent_7d >= 80:
        status_emoji = "🔴 Crítico (>80%)"
    elif stats.percent_used >= 50 or stats.rolling.percent_5h >= 50 or stats.rolling.percent_7d >= 50:
        status_emoji = "🟡 Atenção (>50%)"

    tools_rows = []
    for tool_name, data in stats.top_tools.items():
        tools_rows.append(
            f"| `{tool_name}` | {data['calls']} | {human_tokens(data['tokens'])} | {data['bytes']:,} B |"
        )
    tools_table = "\n".join(tools_rows) if tools_rows else "| Nenhuma ferramenta executada | - | - | - |"

    display_model = get_model_display_name(stats.model_name)
    effort_str = f" | **Effort:** `{stats.effort}`" if stats.effort else ""
    report = f"""# 📊 Relatório de Telemetria de Tokens — Antigravity
> **Status:** {status_emoji} | **Última Leitura:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
> **Sessão:** `{stats.conversation_id}` | **Modelo Utilizado:** `{display_model}` (`{stats.model_name}`){effort_str}  
> **Limites do Modelo:** Janela de Contexto: `{human_tokens(stats.context_window)}` (`{stats.context_window:,}` tokens) | Saída Máxima: `{human_tokens(stats.max_output)}` (`{stats.max_output:,}` tokens)

---

## 1. As 3 Camadas de Limites no Antigravity (<Usado> / <Total>)

| Camada de Limite | Consumo Usado | Teto / Limite Total | Utilizado (%) | Margem Restante | Status & Ritmo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Janela de Mensagem (Context)** | `{human_tokens(stats.total_tokens)}` tokens | `{human_tokens(stats.context_window)}` | **{stats.percent_used:.2f}%** | `{human_tokens(stats.remaining_tokens)}` livres | Ativa na sessão |
| **2. Janela Móvel de 5 Horas (Rate)** | `{human_tokens(stats.rolling.tokens_5h)}` tokens | `{human_tokens(stats.rolling.limit_5h)}` | **{stats.rolling.percent_5h:.2f}%** | `{human_tokens(stats.rolling.remaining_5h)}` livres | {stats.rolling.conversations_5h} sessões (~{human_tokens(stats.rolling.tokens_5h // 5)}/h) |
| **3. Janela Semanal (7 Dias Quota)** | `{human_tokens(stats.rolling.tokens_7d)}` tokens | `{human_tokens(stats.rolling.limit_7d)}` | **{stats.rolling.percent_7d:.2f}%** | `{human_tokens(stats.rolling.remaining_7d)}` livres | {stats.rolling.conversations_7d} sessões (~{human_tokens(stats.rolling.tokens_7d // 7)}/dia) |

---

## 2. Distribuição de Consumo da Sessão Atual
| Categoria | Tokens Estimados | Bytes | Participação |
| :--- | :--- | :--- | :--- |
| **System Prompt & Schemas** | `{human_tokens(stats.system_prompt_tokens)}` | {stats.system_prompt_bytes:,} B | {stats.system_prompt_tokens * 100 / max(1, stats.total_tokens):.1f}% |
| **Execuções de Ferramentas** | `{human_tokens(stats.tool_tokens)}` | {stats.tool_bytes:,} B | {stats.tool_tokens * 100 / max(1, stats.total_tokens):.1f}% |
| **Respostas & Thinking** | `{human_tokens(stats.model_output_tokens)}` | {stats.model_output_bytes:,} B | {stats.model_output_tokens * 100 / max(1, stats.total_tokens):.1f}% |
| **Mensagens do Usuário** | `{human_tokens(stats.user_input_tokens)}` | {stats.user_input_bytes:,} B | {stats.user_input_tokens * 100 / max(1, stats.total_tokens):.1f}% |

---

## 3. Top Ferramentas Consumidoras
{tools_table}

---

## 4. Recomendações de Governança
- **Janela de 5 Horas:** Consumo atual em **{stats.rolling.percent_5h:.1f}%** do teto ({human_tokens(stats.rolling.remaining_5h)} disponíveis). Mantenha comandos e testes com saída concisa.
- **Janela Semanal:** Consumo atual em **{stats.rolling.percent_7d:.1f}%** da cota semanal ({human_tokens(stats.rolling.remaining_7d)} disponíveis). Utilize `PROJECT_MEMORY.md` para resetar sessões longas ao concluir marcos.
"""
    return report


def check_budget_status(stats: TokenStats) -> Tuple[str, bool, str]:
    """
    Avalia a integridade do orçamento nas 3 camadas.
    Retorna (status, is_low, alert_message).
    - Status: 'HEALTHY' | 'WARNING' | 'CRITICAL'
    - is_low: True se atingir patamar crítico de exaustão (>80% em 5h/semana ou >70% em contexto)
    - alert_message: Texto de advertência detalhado com recomendações de escopo.
    """
    warnings = []
    is_critical = False

    # 1. Janela de Mensagem (Context Window)
    if stats.percent_used >= 80:
        is_critical = True
        warnings.append(f"• Contexto da Mensagem em {stats.percent_used:.1f}% ({human_tokens(stats.remaining_tokens)} livres de {human_tokens(stats.context_window)})")
    elif stats.percent_used >= 65:
        warnings.append(f"• Contexto da Mensagem em {stats.percent_used:.1f}% ({human_tokens(stats.remaining_tokens)} livres de {human_tokens(stats.context_window)})")

    # 2 e 3. Cotas de 5h e Semanal (Oficiais da Google ou Heurística Offline)
    if stats.live_quota and stats.live_quota.is_live:
        is_gemini = "gemini" in stats.model_name.lower()
        b_5h = stats.live_quota.gemini_5h if is_gemini else stats.live_quota.claude_5h
        b_7d = stats.live_quota.gemini_weekly if is_gemini else stats.live_quota.claude_weekly

        rem_5h = b_5h.remaining_fraction if b_5h else 1.0
        rem_7d = b_7d.remaining_fraction if b_7d else 1.0

        if rem_5h <= 0.10:
            is_critical = True
            warnings.append(f"• Limite Móvel 5 Horas (Google): apenas {rem_5h * 100.0:.1f}% restante ({clean_refresh_text(b_5h.description)})")
        elif rem_5h <= 0.25:
            warnings.append(f"• Limite Móvel 5 Horas (Google): {rem_5h * 100.0:.1f}% restante ({clean_refresh_text(b_5h.description)})")

        if rem_7d <= 0.05:
            is_critical = True
            warnings.append(f"• Cota Semanal (Google): apenas {rem_7d * 100.0:.1f}% restante ({clean_refresh_text(b_7d.description)})")
        elif rem_7d <= 0.20:
            warnings.append(f"• Cota Semanal (Google): {rem_7d * 100.0:.1f}% restante ({clean_refresh_text(b_7d.description)})")
    else:
        if stats.rolling.percent_5h >= 80:
            is_critical = True
            warnings.append(f"• Janela Móvel de 5 Horas em {stats.rolling.percent_5h:.1f}% ({human_tokens(stats.rolling.remaining_5h)} livres de {human_tokens(stats.rolling.limit_5h)})")
        elif stats.rolling.percent_5h >= 65:
            warnings.append(f"• Janela Móvel de 5 Horas em {stats.rolling.percent_5h:.1f}% ({human_tokens(stats.rolling.remaining_5h)} livres de {human_tokens(stats.rolling.limit_5h)})")

        if stats.rolling.percent_7d >= 85:
            is_critical = True
            warnings.append(f"• Cota Semanal em {stats.rolling.percent_7d:.1f}% ({human_tokens(stats.rolling.remaining_7d)} livres de {human_tokens(stats.rolling.limit_7d)})")
        elif stats.rolling.percent_7d >= 70:
            warnings.append(f"• Cota Semanal em {stats.rolling.percent_7d:.1f}% ({human_tokens(stats.rolling.remaining_7d)} livres de {human_tokens(stats.rolling.limit_7d)})")

    if is_critical:
        msg = (
            "⚠️ **ALERTA DE LIMITE CRÍTICO DE TOKENS DETECTADO:**\n"
            + "\n".join(warnings) + "\n\n"
            + "**Recomendações Operacionais:**\n"
            + "1. O agente alertará o usuário antes de iniciar tarefas substantivas.\n"
            + "2. Se o usuário insistir em prosseguir, a execução adotará **Modo Cirúrgico Atômico**: apenas tarefas essenciais cabíveis na margem disponível, finalizando sempre em um checkpoint estável e testado para não deixar trabalho pela metade.\n"
            + "3. Para poupar tokens, utilize `PROJECT_MEMORY.md` para resetar a sessão e abrir um chat limpo."
        )
        return "CRITICAL", True, msg
    elif warnings:
        msg = (
            "🟡 **AVISO DE ATENÇÃO AO CONSUMO DE TOKENS:**\n"
            + "\n".join(warnings) + "\n"
            + "Recomenda-se evitar comandos verbosos ou leituras de arquivos inteiros."
        )
        return "WARNING", False, msg

    return "HEALTHY", False, "Orçamento de tokens saudável em todas as 3 camadas."


def audit_token_bottlenecks(stats: TokenStats) -> Dict[str, Any]:
    """
    Analisa a distribuição de tokens e identifica ferramentas ou padrões causadores de inchaço de contexto.
    Retorna recomendações acionáveis para redução imediata de consumo.
    """
    bottlenecks = []
    total = max(1, stats.total_tokens)

    # 1. Auditoria de Ferramentas Vilãs
    for tool_name, data in stats.top_tools.items():
        tool_pct = (data["tokens"] / total) * 100.0
        if tool_pct >= 35.0:
            rec = ""
            if tool_name == "RUN_COMMAND":
                rec = "Saídas extensas de terminal detectadas. Utilize flags silenciosas (--silent, -q), supressão via head ou o utilitário scripts/sanitize-tool-output.sh."
            elif tool_name == "VIEW_FILE":
                rec = "Leituras extensas de arquivo. Restrinja o fatiamento utilizando StartLine e EndLine (máximo 50-100 linhas por vez)."
            else:
                rec = f"A ferramenta {tool_name} consumiu mais de 35% do contexto. Avalie truncamento de output."
            
            bottlenecks.append({
                "tool": tool_name,
                "tokens": data["tokens"],
                "percent": round(tool_pct, 1),
                "calls": data["calls"],
                "recommendation": rec,
            })

    # 2. Auditoria de Longevidade da Sessão
    session_rec = None
    if stats.steps_count >= 25 or stats.total_tokens >= 65_000:
        session_rec = (
            f"Sessão longa detectada ({stats.steps_count} passos, {human_tokens(stats.total_tokens)} tokens). "
            "Recomenda-se realizar Session Reset: salvar o progresso no PROJECT_MEMORY.md e iniciar um chat limpo."
        )

    # 3. Auditoria do System Prompt
    sys_rec = None
    if stats.system_prompt_bytes > 90_000:
        sys_rec = "System Prompt elevado (>90KB). Verifique duplicações de regras em ~/.gemini/config/rules/ ou descrições verbosas de skills."

    return {
        "conversation_id": stats.conversation_id,
        "total_tokens": stats.total_tokens,
        "bottlenecks": bottlenecks,
        "session_longevity_warning": session_rec,
        "system_prompt_warning": sys_rec,
    }


def find_active_session() -> Tuple[Optional[str], Optional[Path], Optional[str]]:
    """Localiza a sessão mais recente no ambiente IDE ou CLI."""
    home = Path.home()
    candidates = []

    for app in ("antigravity-ide", "antigravity-cli"):
        base_dir = home / ".gemini" / app
        brain_dir = base_dir / "brain"
        if brain_dir.is_dir():
            for conv_dir in brain_dir.iterdir():
                t_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
                if t_file.is_file():
                    candidates.append((t_file.stat().st_mtime, conv_dir.name, t_file, app))

    if not candidates:
        return None, None, None

    candidates.sort(key=lambda x: x[0], reverse=True)
    best = candidates[0]
    return best[1], best[2], best[3]


def load_transcript(transcript_path: Path) -> List[Dict[str, Any]]:
    """Lê as linhas do transcript.jsonl em formato JSON."""
    steps = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        steps.append(json.loads(line))
                    except Exception:
                        pass
    except Exception as e:
        sys.stderr.write(f"Erro ao ler transcript {transcript_path}: {e}\n")
    return steps


def detect_model_name(conversation_id: str, steps: Optional[List[Dict[str, Any]]] = None) -> str:
    """Detecta o modelo ativo via: steps do transcript → env vars → config files → SQLite → padrão."""
    # 1. Detecção dinâmica via transcript (prioridade máxima — detecta troca em tempo real)
    if steps:
        detected = detect_model_name_from_steps(steps)
        if detected:
            return detected

    # 2. Variáveis de ambiente (usuário configurou explicitamente no ambiente)
    for env_key in ("AGY_MODEL", "XP_MODEL", "ANTHROPIC_MODEL", "GEMINI_MODEL"):
        env_val = os.environ.get(env_key, "").strip().lower()
        if env_val:
            return env_val

    # 3. Arquivo de configuração do Antigravity (IDE ou CLI)
    home = Path.home()
    for cfg_path in [
        home / ".gemini" / "antigravity-cli" / "settings.json",
        home / ".gemini" / "antigravity-ide" / "settings.json",
        home / ".gemini" / "antigravity-ide" / "config.json",
        home / ".gemini" / "antigravity-cli" / "config.json",
        home / ".gemini" / "config" / "settings.json",
    ]:
        if cfg_path.is_file():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                model = (
                    cfg.get("model")
                    or cfg.get("defaultModel")
                    or cfg.get("default_model")
                    or ""
                )
                if model:
                    norm = detect_model_name_from_steps([{"type": "USER_INPUT", "content": f"Model Selection to {model}"}])
                    if norm:
                        return norm
                    return str(model).lower().strip()
            except Exception:
                pass

    # 4. SQLite da conversa
    for app in ("antigravity-ide", "antigravity-cli"):
        db_path = home / ".gemini" / app / "conversations" / f"{conversation_id}.db"
        if db_path.is_file():
            try:
                con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                cur = con.cursor()
                rows = cur.execute("SELECT data FROM gen_metadata ORDER BY idx DESC LIMIT 5").fetchall()
                for (data,) in rows:
                    payload = data if isinstance(data, bytes) else str(data).encode()
                    for m in MODEL_LIMITS.keys():
                        if m == "default":
                            continue
                        if m.encode() in payload:
                            con.close()
                            return m
                con.close()
            except Exception:
                pass

    # 5. Padrão conservador
    return "gemini-3.8-flash"


def render_rich_dashboard(stats: TokenStats):
    """Exibe um dashboard interativo no terminal utilizando rich com <usado>/<total>."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text

        console = Console()
        console.clear()

        c_msg = "green" if stats.percent_used < 50 else ("yellow" if stats.percent_used < 80 else "red")
        c_5h = "green" if stats.rolling.percent_5h < 50 else ("yellow" if stats.rolling.percent_5h < 80 else "red")
        c_7d = "green" if stats.rolling.percent_7d < 50 else ("yellow" if stats.rolling.percent_7d < 80 else "red")

        info_text = Text()
        info_text.append("Sessão Ativa: ", style="bold cyan")
        info_text.append(f"{stats.conversation_id}\n", style="white")
        display_model = get_model_display_name(stats.model_name)
        info_text.append("Modelo Utilizado: ", style="bold cyan")
        info_text.append(f"{display_model} ", style="bold yellow")
        info_text.append(f"({stats.model_name})", style="dim")
        if stats.effort:
            info_text.append(" | Effort: ", style="bold cyan")
            info_text.append(f"{stats.effort}", style="bold magenta")
        info_text.append("\n", style="white")
        info_text.append("Limites do Modelo: ", style="bold cyan")
        info_text.append(f"Janela Contexto: {human_tokens(stats.context_window)} ({stats.context_window:,}) | Saída Máx: {human_tokens(stats.max_output)} ({stats.max_output:,})\n", style="bold green")
        info_text.append("Passos Registrados: ", style="bold cyan")
        info_text.append(f"{stats.steps_count}\n\n", style="white")

        info_text.append("1. JANELA DE MENSAGEM: ", style="bold magenta")
        info_text.append(f"{human_tokens(stats.total_tokens)} / {human_tokens(stats.context_window)} tokens ", style="bold white")
        info_text.append(f"({stats.percent_used:.2f}%)\n", style=f"bold {c_msg}")
        info_text.append(f"   Margem Livre: {human_tokens(stats.remaining_tokens)} tokens | Saída Max: {human_tokens(stats.max_output)}\n\n", style="dim")

        info_text.append("2. LIMITE MÓVEL 5 HORAS: ", style="bold magenta")
        info_text.append(f"{human_tokens(stats.rolling.tokens_5h)} / {human_tokens(stats.rolling.limit_5h)} tokens ", style="bold white")
        info_text.append(f"({stats.rolling.percent_5h:.2f}%)\n", style=f"bold {c_5h}")
        info_text.append(f"   Margem Livre: {human_tokens(stats.rolling.remaining_5h)} tokens | {stats.rolling.conversations_5h} sessões (~{human_tokens(stats.rolling.tokens_5h // 5)}/h)\n\n", style="dim")

        info_text.append("3. LIMITE SEMANAL (7 DIAS): ", style="bold magenta")
        info_text.append(f"{human_tokens(stats.rolling.tokens_7d)} / {human_tokens(stats.rolling.limit_7d)} tokens ", style="bold white")
        info_text.append(f"({stats.rolling.percent_7d:.2f}%)\n", style=f"bold {c_7d}")
        info_text.append(f"   Margem Livre: {human_tokens(stats.rolling.remaining_7d)} tokens | {stats.rolling.conversations_7d} sessões (~{human_tokens(stats.rolling.tokens_7d // 7)}/dia)\n", style="dim")

        if stats.live_quota and stats.live_quota.is_live:
            is_gemini = "gemini" in stats.model_name.lower()
            b_5h = stats.live_quota.gemini_5h if is_gemini else stats.live_quota.claude_5h
            b_7d = stats.live_quota.gemini_weekly if is_gemini else stats.live_quota.claude_weekly
            pct_5h = (b_5h.remaining_fraction * 100.0) if b_5h else 100.0
            pct_7d = (b_7d.remaining_fraction * 100.0) if b_7d else 100.0
            d_5h = f" ({clean_refresh_text(b_5h.description)})" if b_5h and b_5h.description else ""
            d_7d = f" ({clean_refresh_text(b_7d.description)})" if b_7d and b_7d.description else ""
            info_text.append(f"\n⚡ COTA AO VIVO (Google Language Server - {stats.live_quota.plan_name}):\n", style="bold yellow")
            info_text.append(f"   • Janela 5h:     {pct_5h:.1f}% restante{d_5h}\n", style="white")
            info_text.append(f"   • Cota Semanal:  {pct_7d:.1f}% restante{d_7d}\n", style="white")

        console.print(Panel(info_text, title="🧠 [bold magenta]Antigravity Token & Quota Tracker[/bold magenta]", border_style="bright_blue"))

        table = Table(title="📦 Distribuição de Consumo da Sessão Atual", border_style="blue", header_style="bold cyan")
        table.add_column("Categoria", style="white")
        table.add_column("Tokens Est.", justify="right", style="green")
        table.add_column("Bytes", justify="right", style="dim")
        table.add_column("% Janela", justify="right", style="bold")

        categories = [
            ("System Prompt & Tools Schemas", stats.system_prompt_tokens, stats.system_prompt_bytes),
            ("Execuções de Ferramentas", stats.tool_tokens, stats.tool_bytes),
            ("Respostas & Thinking", stats.model_output_tokens, stats.model_output_bytes),
            ("Mensagens do Usuário", stats.user_input_tokens, stats.user_input_bytes),
        ]
        for name, tok, byt in categories:
            pct_total = (tok / max(1, stats.total_tokens)) * 100.0
            table.add_row(name, f"{tok:,} ({human_tokens(tok)})", f"{byt:,} B", f"{pct_total:.1f}%")

        console.print(table)

        if stats.top_tools:
            t_table = Table(title="⚡ Top Ferramentas Consumidoras", border_style="yellow", header_style="bold yellow")
            t_table.add_column("Ferramenta", style="white")
            t_table.add_column("Chamadas", justify="right", style="cyan")
            t_table.add_column("Tokens Est.", justify="right", style="bold red")
            t_table.add_column("Bytes", justify="right", style="dim")

            for t_name, data in list(stats.top_tools.items())[:5]:
                t_table.add_row(t_name, str(data["calls"]), f"{data['tokens']:,} ({human_tokens(data['tokens'])})", f"{data['bytes']:,} B")
            console.print(t_table)

    except ImportError:
        render_plain_dashboard(stats)


def render_plain_dashboard(stats: TokenStats):
    """Fallback simples caso rich não esteja instalado."""
    display_model = get_model_display_name(stats.model_name)
    print("=" * 70)
    print(" ANTIGRAVITY TOKEN & QUOTA TELEMETRY TRACKER")
    print("=" * 70)
    print(f"Sessão:          {stats.conversation_id}")
    effort_str = f" | Effort: {stats.effort}" if stats.effort else ""
    print(f"Modelo Utilizado: {display_model} ({stats.model_name}){effort_str}")
    print(f"Limites Modelo:   Janela Contexto: {stats.context_window:,} ({human_tokens(stats.context_window)}) | Saída Máx: {stats.max_output:,} ({human_tokens(stats.max_output)})")
    print("-" * 70)
    print(f"1. Contexto Msg: {stats.total_tokens:,} / {stats.context_window:,} ({stats.percent_used:.2f}%)")
    print(f"   Margem Livre: {stats.remaining_tokens:,} tokens disponíveis")
    print(f"2. Janela 5h:    {stats.rolling.tokens_5h:,} / {stats.rolling.limit_5h:,} ({stats.rolling.percent_5h:.2f}%)")
    print(f"   Margem Livre: {stats.rolling.remaining_5h:,} tokens disponíveis ({stats.rolling.conversations_5h} conversas)")
    print(f"3. Janela 7d:    {stats.rolling.tokens_7d:,} / {stats.rolling.limit_7d:,} ({stats.rolling.percent_7d:.2f}%)")
    print(f"   Margem Livre: {stats.rolling.remaining_7d:,} tokens disponíveis ({stats.rolling.conversations_7d} conversas)")
    if stats.live_quota and stats.live_quota.is_live:
        is_gemini = "gemini" in stats.model_name.lower()
        b_5h = stats.live_quota.gemini_5h if is_gemini else stats.live_quota.claude_5h
        b_7d = stats.live_quota.gemini_weekly if is_gemini else stats.live_quota.claude_weekly
        pct_5h = (b_5h.remaining_fraction * 100.0) if b_5h else 100.0
        pct_7d = (b_7d.remaining_fraction * 100.0) if b_7d else 100.0
        d_5h = f" ({clean_refresh_text(b_5h.description)})" if b_5h and b_5h.description else ""
        d_7d = f" ({clean_refresh_text(b_7d.description)})" if b_7d and b_7d.description else ""
        print("-" * 70)
        print(f"⚡ COTA AO VIVO (Google Language Server - {stats.live_quota.plan_name}):")
        print(f"   • Janela 5 Horas: {pct_5h:.1f}% restante{d_5h}")
        print(f"   • Cota Semanal:   {pct_7d:.1f}% restante{d_7d}")
    print("-" * 70)
    print(f" - System Prompt & Schemas: {stats.system_prompt_tokens:,} tokens ({stats.system_prompt_bytes:,} B)")
    print(f" - Execuções de Ferramentas: {stats.tool_tokens:,} tokens ({stats.tool_bytes:,} B)")
    print(f" - Respostas & Thinking:    {stats.model_output_tokens:,} tokens ({stats.model_output_bytes:,} B)")
    print(f" - Mensagens do Usuário:    {stats.user_input_tokens:,} tokens ({stats.user_input_bytes:,} B)")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Antigravity Token & Quota Telemetry Tracker")
    parser.add_argument("-c", "--conversation-id", help="ID da conversa específica para monitorar")
    parser.add_argument("-m", "--model", help="Sobrescreve o modelo ativo para exibição e limites (ex: gemini-3.8-flash, claude-sonnet-4-6, gpt-4o)")
    parser.add_argument("-e", "--effort", help="Sobrescreve o nível de reasoning effort para exibição (ex: low, medium, high)")
    parser.add_argument("-w", "--watch", action="store_true", help="Atualiza em loop contínuo (tempo real)")
    parser.add_argument("-i", "--interval", type=int, default=2, help="Intervalo de atualização em segundos para --watch")
    parser.add_argument("--limit-5h", help="Teto da janela de 5h (ex: 500k, 300000)")
    parser.add_argument("--limit-weekly", help="Teto da cota semanal (ex: 10M, 15M, 10000000)")
    parser.add_argument("--badge", action="store_true", help="Imprime apenas o badge markdown de telemetria")
    parser.add_argument("--turn", action="store_true", help="Imprime o rodapé de telemetria da mensagem/turno atual e acumulado")
    parser.add_argument("--json", action="store_true", help="Imprime as estatísticas em formato JSON")
    parser.add_argument("--report", action="store_true", help="Gera e grava o arquivo .agents/memory/TOKEN_TELEMETRY.md")
    parser.add_argument("--check", action="store_true", help="Avalia se os limites estão baixos e emite alerta se necessário")
    parser.add_argument("--audit", action="store_true", help="Audita gargalos de consumo e emite recomendações de otimização")
    parser.add_argument("--plain", action="store_true", help="Força saída em texto simples (sem rich)")

    args = parser.parse_args()

    limit_5h = parse_token_limit(args.limit_5h, DEFAULT_LIMIT_5H) if args.limit_5h else None
    limit_7d = parse_token_limit(args.limit_weekly, DEFAULT_LIMIT_WEEKLY) if args.limit_weekly else None

    while True:
        conv_id = args.conversation_id
        transcript_path = None

        if not conv_id:
            conv_id, transcript_path, _ = find_active_session()
        else:
            home = Path.home()
            for app in ("antigravity-ide", "antigravity-cli"):
                candidate = home / ".gemini" / app / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
                if candidate.is_file():
                    transcript_path = candidate
                    break

        if not conv_id or not transcript_path or not transcript_path.is_file():
            sys.stderr.write("Nenhuma conversa ativa encontrada no Antigravity IDE/CLI.\n")
            if not args.watch:
                sys.exit(1)
            time.sleep(args.interval)
            continue

        steps = load_transcript(transcript_path)
        model_name = args.model if args.model else detect_model_name(conv_id, steps=steps)
        rolling = calculate_rolling_windows(limit_5h=limit_5h, limit_7d=limit_7d)
        stats = parse_transcript_data(conv_id, model_name, steps, rolling=rolling, fetch_live=True, effort=args.effort)

        if args.turn:
            turn = calculate_turn_stats(steps)
            print(format_message_footer(stats, turn))
            return

        if args.check:
            status, is_low, msg = check_budget_status(stats)
            print(f"[{status}] {msg}")
            sys.exit(2 if is_low else 0)

        if args.audit:
            audit = audit_token_bottlenecks(stats)
            print("=" * 70)
            print(" 🔍 AUDITORIA DE GARGALOS DE CONSUMO DE TOKENS")
            print("=" * 70)
            print(f"Sessão: {audit['conversation_id']} | Total: {audit['total_tokens']:,} tokens")
            print("-" * 70)
            if audit["bottlenecks"]:
                print("⚠️  FERRAMENTAS VILÃS IDENTIFICADAS (>35% do contexto):")
                for b in audit["bottlenecks"]:
                    print(f"  • {b['tool']}: {b['tokens']:,} tokens ({b['percent']}%, {b['calls']} chamadas)")
                    print(f"    👉 Ação: {b['recommendation']}\n")
            else:
                print("✅ Nenhuma ferramenta isolada ultrapassou 35% do contexto.")

            if audit["session_longevity_warning"]:
                print(f"⚠️  LONGEVIDADE: {audit['session_longevity_warning']}")
            if audit["system_prompt_warning"]:
                print(f"⚠️  SYSTEM PROMPT: {audit['system_prompt_warning']}")
            print("=" * 70)
            return

        if args.badge:
            print(format_badge(stats))
            return

        if args.json:
            print(format_json_stats(stats))
            return

        if args.report:
            report_text = format_markdown_report(stats)
            if Path.cwd().name == ".agents":
                report_path = Path.cwd() / "memory" / "TOKEN_TELEMETRY.md"
            else:
                report_path = Path.cwd() / ".agents" / "memory" / "TOKEN_TELEMETRY.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_text, encoding="utf-8")
            print(f"Relatório gravado com sucesso em: {report_path.resolve()}")
            return

        if args.plain:
            render_plain_dashboard(stats)
        else:
            render_rich_dashboard(stats)

        if not args.watch:
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
