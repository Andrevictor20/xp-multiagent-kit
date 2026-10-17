#!/usr/bin/env python3
"""
scripts/telemetry/catalogs.py
Canonical model catalogs, limits, display names, and host mappings.
"""

from __future__ import annotations
from typing import Any, Dict, List

MODEL_LIMITS: Dict[str, Dict[str, int]] = {
    # Google Gemini Models
    "gemini-4-argon": {"context_window": 1_048_576, "max_output": 65_536},
    "gemini-4-pro": {"context_window": 2_097_152, "max_output": 65_536},
    "gemini-4-flash": {"context_window": 1_048_576, "max_output": 65_536},
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
    # Anthropic Claude Models
    "claude-sonnet-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-opus-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-haiku-4-6": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-7-sonnet": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-5-sonnet": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-5-haiku": {"context_window": 200_000, "max_output": 8_192},
    "claude-3-opus": {"context_window": 200_000, "max_output": 8_192},
    # OpenAI Models
    "gpt-4o-mini": {"context_window": 128_000, "max_output": 16_384},
    "gpt-4o": {"context_window": 128_000, "max_output": 16_384},
    "gpt-4-turbo": {"context_window": 128_000, "max_output": 4_096},
    "o1-mini": {"context_window": 128_000, "max_output": 65_536},
    "o1": {"context_window": 200_000, "max_output": 100_000},
    "o3-mini": {"context_window": 200_000, "max_output": 100_000},
    # DeepSeek Models
    "deepseek-chat": {"context_window": 128_000, "max_output": 8_192},
    "deepseek-reasoner": {"context_window": 128_000, "max_output": 8_192},
    "deepseek-v3": {"context_window": 128_000, "max_output": 8_192},
    "deepseek-r1": {"context_window": 128_000, "max_output": 8_192},
    "qwen-2.5-coder": {"context_window": 131_072, "max_output": 8_192},
    "cursor-small": {"context_window": 200_000, "max_output": 8_192},
    # OpenCode Models
    "muse-spark-1.3-contributor-free": {"context_window": 1_048_576, "max_output": 65_536},
    "muse-spark": {"context_window": 1_048_576, "max_output": 65_536},
    "muse-spark-1.3-free": {"context_window": 1_048_576, "max_output": 65_536},
    "default": {"context_window": 1_000_000, "max_output": 8_192},
}

PROVIDER_RATE_LIMITS: Dict[str, Dict[str, int]] = {
    "gemini": {"limit_5h": 800_000, "limit_7d": 10_000_000},
    "claude": {"limit_5h": 100_000, "limit_7d": 2_000_000},
    "openai": {"limit_5h": 80_000, "limit_7d": 1_500_000},
    "deepseek": {"limit_5h": 60_000, "limit_7d": 1_000_000},
    "opencode": {"limit_5h": 1_000_000, "limit_7d": 10_000_000},
    "default": {"limit_5h": 80_000, "limit_7d": 1_000_000},
}

MODEL_DISPLAY_NAMES: Dict[str, str] = {
    "gemini-4-argon": "Gemini 4 Argon",
    "gemini-4-pro": "Gemini 4 Pro",
    "gemini-4-flash": "Gemini 4 Flash",
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
    "cursor-small": "Cursor Small",
    "qwen-2.5-coder": "Qwen 2.5 Coder",
    "muse-spark-1.3-contributor-free": "Muse Spark 1.3 Free",
    "muse-spark": "Muse Spark",
    "muse-spark-1.3-free": "Muse Spark 1.3 Free",
}

HOST_MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "antigravity": {
        "display_name": "Antigravity",
        "provider": "gemini",
        "models": ["gemini-4-argon", "gemini-3.8-flash", "gemini-3.8-pro", "gemini-4-pro", "claude-3-7-sonnet"],
        "default": "gemini-3.8-flash",
    },
    "cursor": {
        "display_name": "Cursor",
        "provider": "claude",
        "models": ["claude-3-7-sonnet", "claude-3-5-sonnet", "gpt-4o", "o3-mini", "cursor-small"],
        "default": "claude-3-7-sonnet",
    },
    "codex": {
        "display_name": "Codex",
        "provider": "openai",
        "models": ["gpt-4o", "o3-mini", "o1", "claude-3-5-sonnet"],
        "default": "gpt-4o",
    },
    "qoder": {
        "display_name": "Qoder",
        "provider": "deepseek",
        "models": ["deepseek-r1", "deepseek-v3", "qwen-2.5-coder", "gpt-4o"],
        "default": "deepseek-r1",
    },
    "opencode": {
        "display_name": "OpenCode",
        "provider": "opencode",
        "models": ["muse-spark-1.3-contributor-free", "claude-3-7-sonnet", "gpt-4o", "deepseek-r1", "gemini-3.8-flash"],
        "default": "muse-spark-1.3-contributor-free",
    },
}


def get_models_for_host(host: str) -> List[str]:
    """Returns recommended canonical models for a host environment."""
    canon_host = host.lower().strip()
    entry = HOST_MODEL_CATALOG.get(canon_host)
    if entry and "models" in entry:
        return list(entry["models"])
    return list(HOST_MODEL_CATALOG["antigravity"]["models"])
