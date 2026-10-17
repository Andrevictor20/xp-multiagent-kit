#!/usr/bin/env python3
"""
scripts/telemetry/models.py
Model definitions, dynamic model detection, limits, and data structures for XP Multi-Agent Kit Telemetry.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.telemetry.catalogs import (
    HOST_MODEL_CATALOG,
    MODEL_DISPLAY_NAMES,
    MODEL_LIMITS,
    PROVIDER_RATE_LIMITS,
    get_models_for_host,
)


def detect_active_host() -> str:
    """Detects active host environment from environment variables or processes."""
    if os.environ.get("CURSOR_VERSION") or os.environ.get("CURSOR_RESOURCES_PATH"):
        return "cursor"
    if os.environ.get("CODEX_HOME") or os.environ.get("OPENAI_CODEX"):
        return "codex"
    if os.environ.get("QODER_HOME") or os.environ.get("QODER_VERSION"):
        return "qoder"
    if os.environ.get("OPENCODE_CONFIG") or os.environ.get("OPENCODE_HOME"):
        return "opencode"
    return "antigravity"


DEFAULT_SYSTEM_PROMPT_BYTES = 85_000
DEFAULT_LIMIT_5H = 800_000
DEFAULT_LIMIT_WEEKLY = 10_000_000

_CHARS_PER_TOKEN_PROSE = 4.0
_CHARS_PER_TOKEN_CODE = 3.2
_CHARS_PER_TOKEN_MIXED = 3.5
_CHARS_PER_TOKEN_CONFIG = 3.3


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
    is_projected: bool = False
    plan_name: str = "Google AI Pro"
    gemini_5h: Optional[LiveQuotaBucket] = None
    gemini_weekly: Optional[LiveQuotaBucket] = None
    gemini_argon_weekly: Optional[LiveQuotaBucket] = None
    claude_5h: Optional[LiveQuotaBucket] = None
    claude_weekly: Optional[LiveQuotaBucket] = None
    description: str = ""
    error: Optional[str] = None
    sync_timestamp: float = 0.0
    sync_datetime: str = ""


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
    system_prompt_tokens: int = 0
    system_prompt_bytes: int = 0
    user_input_tokens: int = 0
    user_input_bytes: int = 0
    tool_tokens: int = 0
    tool_bytes: int = 0
    model_output_tokens: int = 0
    model_output_bytes: int = 0
    total_tokens: int = 0
    remaining_tokens: int = 0
    percent_used: float = 0.0
    effort: Optional[str] = None
    rolling: RollingWindowStats = field(default_factory=RollingWindowStats)
    live_quota: LiveServerQuota = field(default_factory=LiveServerQuota)
    top_tools: Dict[str, Dict[str, int]] = field(default_factory=dict)
    steps_count: int = 0
    rtk_savings: Optional[Dict[str, Any]] = None


@dataclass
class TurnStats:
    user_input_tokens: int = 0
    tool_tokens: int = 0
    model_output_tokens: int = 0
    total_tokens: int = 0
    ephemeral_tokens: int = 0


def get_model_display_name(model_name: Optional[str]) -> str:
    """Returns a human-readable model display name, preserving dynamic model names."""
    if not model_name:
        return "Unknown Model"
    clean_name = model_name.lower().strip()
    for key, display in MODEL_DISPLAY_NAMES.items():
        if key in clean_name or key.replace("-", " ") in clean_name or key.replace("-", "") in clean_name:
            if "(high)" in clean_name:
                return f"{display} (High)"
            if "(low)" in clean_name:
                return f"{display} (Low)"
            if "(medium)" in clean_name:
                return f"{display} (Medium)"
            if "thinking" in clean_name:
                return f"{display} (Thinking)"
            return display
    # Dynamic title-case formatting for newly released models (e.g., gemini-4-argon -> Gemini 4 Argon)
    if re.match(r"^(?:gemini|claude|gpt|deepseek)-", clean_name):
        parts = clean_name.split("-")
        formatted = []
        for p in parts:
            if p == "gpt":
                formatted.append("GPT")
            elif p == "deepseek":
                formatted.append("DeepSeek")
            else:
                formatted.append(p.capitalize())
        return " ".join(formatted)
    return model_name


def get_provider_defaults(model_name: str) -> Dict[str, int]:
    """Returns provider-specific 5h/weekly rate limits."""
    m = (model_name or "").lower()
    if "gemini" in m:
        return PROVIDER_RATE_LIMITS["gemini"]
    if "claude" in m or "anthropic" in m:
        return PROVIDER_RATE_LIMITS["claude"]
    if "gpt" in m or "o1" in m or "o3" in m or "openai" in m:
        return PROVIDER_RATE_LIMITS["openai"]
    if "deepseek" in m:
        return PROVIDER_RATE_LIMITS["deepseek"]
    return PROVIDER_RATE_LIMITS["default"]


def get_model_limits(model_name: Optional[str]) -> Dict[str, int]:
    """Returns context window and max output for the model."""
    if not model_name:
        return MODEL_LIMITS["default"]
    clean_name = model_name.lower().strip()
    for key, limits in MODEL_LIMITS.items():
        if key in clean_name or key.replace("-", " ") in clean_name or key.replace("-", "") in clean_name:
            return limits
    if "gemini" in clean_name:
        return {"context_window": 2_097_152 if "pro" in clean_name else 1_048_576, "max_output": 65_536}
    return MODEL_LIMITS["default"]


def parse_token_limit(val: Any, default: int = 800_000) -> int:
    """Converts k/M/B suffixed strings to integer token counts."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip().upper()
    if not s:
        return default
    multiplier = 1
    if s.endswith("K"):
        multiplier, s = 1_000, s[:-1]
    elif s.endswith("M"):
        multiplier, s = 1_000_000, s[:-1]
    elif s.endswith("B"):
        multiplier, s = 1_000_000_000, s[:-1]
    try:
        return int(float(s) * multiplier)
    except ValueError:
        return default


def human_tokens(count: int) -> str:
    """Formats token integer into human-readable k/M string."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.2f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}k"
    return str(count)


def detect_model_name_from_steps(steps: List[Dict[str, Any]]) -> Optional[str]:
    """Detects active model from transcript steps without hardcoded fallback to 3.8-flash."""
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
                r"Model Selection.*?\bto\s+([A-Za-z0-9\.\-\s]+?)(?:\s*\(|\.\s+[A-Z]|\n|<|$)",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            model_str = m.group(1).strip().lower() if m else content.lower()
            model_str = re.sub(r"\s*\((?:high|medium|low|thinking)\).*$", "", model_str, flags=re.IGNORECASE).strip()

            if "gemini" in model_str:
                for ver in ("3.8", "3.7", "3.6", "3.1", "2.5", "2.0", "1.5"):
                    if ver in model_str:
                        if ver in ("3.6",):
                            return "gemini-3.6-flash"
                        if ver in ("3.1",):
                            return "gemini-3.1-pro"
                        return f"gemini-{ver}-pro" if "pro" in model_str else f"gemini-{ver}-flash"
                # Dynamic normalization for new Gemini models (e.g. "gemini 4 argon" -> "gemini-4-argon")
                slug = re.sub(r"[^a-z0-9\.]+", "-", model_str).strip("-")
                return slug if slug else "gemini-3.8-flash"

            if any(k in model_str for k in ("claude", "sonnet", "opus", "haiku")):
                if "4" in model_str or "4.6" in model_str:
                    if "opus" in model_str:
                        return "claude-opus-4-6"
                    if "haiku" in model_str:
                        return "claude-haiku-4-6"
                    return "claude-sonnet-4-6"
                if "3.7" in model_str:
                    return "claude-3-7-sonnet"
                if "3.5" in model_str:
                    return "claude-3-5-haiku" if "haiku" in model_str else "claude-3-5-sonnet"
                if "opus" in model_str:
                    return "claude-3-opus"
                return "claude-sonnet-4-6"

            if "gpt-4o" in model_str:
                return "gpt-4o-mini" if "mini" in model_str else "gpt-4o"
            if "o1" in model_str:
                return "o1-mini" if "mini" in model_str else "o1"
            if "o3" in model_str:
                return "o3-mini"
            if "deepseek" in model_str:
                return "deepseek-reasoner" if ("r1" in model_str or "reasoner" in model_str) else "deepseek-chat"

    return None


def detect_effort(
    conversation_id: str,
    steps: Optional[List[Dict[str, Any]]] = None,
    explicit_effort: Optional[str] = None,
) -> Optional[str]:
    """Detects active reasoning effort (Low, Medium, High, Thinking)."""
    if explicit_effort:
        return explicit_effort.capitalize()

    if steps:
        for step in reversed(steps):
            if step.get("type") != "USER_INPUT":
                continue
            content = step.get("content", "")
            if not isinstance(content, str):
                content = json.dumps(content) if content else ""
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

    for env_key in ("AGY_EFFORT", "REASONING_EFFORT", "EFFORT"):
        env_val = os.environ.get(env_key, "").strip().lower()
        if env_val:
            return env_val.capitalize()

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


def detect_model_name(conversation_id: str, steps: Optional[List[Dict[str, Any]]] = None) -> str:
    """Detects active model across transcript steps, env vars, config files, and SQLite."""
    if steps:
        detected = detect_model_name_from_steps(steps)
        if detected:
            return detected

    for env_key in ("AGY_MODEL", "XP_MODEL", "OPENCODE_MODEL", "CURSOR_MODEL", "ANTHROPIC_MODEL", "GEMINI_MODEL"):
        env_val = os.environ.get(env_key, "").strip().lower()
        if env_val:
            return env_val

    home = Path.home()
    for cfg_path in [
        home / ".gemini" / "antigravity-cli" / "settings.json",
        home / ".gemini" / "antigravity-ide" / "settings.json",
        home / ".gemini" / "antigravity-ide" / "config.json",
        home / ".gemini" / "antigravity-cli" / "config.json",
        home / ".gemini" / "config" / "settings.json",
        home / ".config" / "opencode" / "opencode.json",
    ]:
        if cfg_path.is_file():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                model = cfg.get("model") or cfg.get("defaultModel") or cfg.get("default_model") or ""
                if model:
                    norm = detect_model_name_from_steps([{"type": "USER_INPUT", "content": f"Model Selection to {model}"}])
                    return norm if norm else str(model).lower().strip()
            except Exception:
                pass

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
                        if m != "default" and m.encode() in payload:
                            con.close()
                            return m
                con.close()
            except Exception:
                pass

    return "gemini-3.8-flash"
