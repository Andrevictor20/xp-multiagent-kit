#!/usr/bin/env python3
"""
scripts/telemetry/parser.py
Transcript parsing, compaction awareness, turn stats, and rolling window calculation.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from scripts.telemetry.models import (
    DEFAULT_LIMIT_5H,
    DEFAULT_LIMIT_WEEKLY,
    DEFAULT_SYSTEM_PROMPT_BYTES,
    LiveServerQuota,
    RollingWindowStats,
    TokenStats,
    TurnStats,
    _CHARS_PER_TOKEN_CODE,
    _CHARS_PER_TOKEN_CONFIG,
    _CHARS_PER_TOKEN_MIXED,
    _CHARS_PER_TOKEN_PROSE,
    detect_effort,
    detect_model_name,
    get_model_limits,
    get_provider_defaults,
    parse_token_limit,
)
from scripts.telemetry.quota_rpc import fetch_live_antigravity_quota, fetch_rtk_savings


def estimate_tokens(text: Optional[str]) -> int:
    """Estimates token count using BPE/SentencePiece heuristics."""
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
    return max(0, int(byte_count / chars_per_token))


def calculate_turn_stats(steps: List[Dict[str, Any]]) -> TurnStats:
    """Calculates tokens consumed exclusively in the latest user turn."""
    if not steps:
        return TurnStats()

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
    ephemeral_bytes = 0
    seen_ephemerals = set()

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
        elif stype in ("EPHEMERAL_MESSAGE", "SYSTEM_MESSAGE", "ERROR_MESSAGE"):
            digest = hash(content)
            if digest not in seen_ephemerals:
                seen_ephemerals.add(digest)
                ephemeral_bytes += step_len
        else:
            tool_bytes += step_len

    user_tokens = _tokens_from_bytes(user_bytes, _CHARS_PER_TOKEN_PROSE)
    tool_tokens = _tokens_from_bytes(tool_bytes, _CHARS_PER_TOKEN_CODE)
    model_tokens = _tokens_from_bytes(model_bytes, _CHARS_PER_TOKEN_MIXED)
    ephemeral_tokens = _tokens_from_bytes(ephemeral_bytes, _CHARS_PER_TOKEN_PROSE)
    total_tokens = user_tokens + tool_tokens + model_tokens + ephemeral_tokens

    return TurnStats(
        user_input_tokens=user_tokens,
        tool_tokens=tool_tokens,
        model_output_tokens=model_tokens,
        total_tokens=total_tokens,
        ephemeral_tokens=ephemeral_tokens,
    )


def _measure_system_prompt_bytes() -> int:
    """Measures active system prompt size across loaded rules and workspace."""
    home = Path.home()
    total = 0
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

    for ws_file in [Path("AGENTS.md"), Path("GEMINI.md")]:
        if ws_file.is_file():
            try:
                total += ws_file.stat().st_size
            except Exception:
                pass

    total += 45_000
    return max(DEFAULT_SYSTEM_PROMPT_BYTES, total)


def calculate_rolling_windows(
    search_dirs: Optional[List[Path]] = None,
    limit_5h: Optional[int] = None,
    limit_7d: Optional[int] = None,
) -> RollingWindowStats:
    """Calculates rolling 5h and 7d token usage across local transcripts."""
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
                            content = step.get("content", "") or ""
                            thinking = step.get("thinking", "") or ""
                            if not isinstance(content, str):
                                content = json.dumps(content)
                            if not isinstance(thinking, str):
                                thinking = ""
                            stype = step.get("type", "")
                            if stype == "PLANNER_RESPONSE":
                                file_tokens += _tokens_from_bytes(
                                    len(content) + len(thinking), _CHARS_PER_TOKEN_MIXED
                                )
                            elif stype == "USER_INPUT":
                                file_tokens += _tokens_from_bytes(len(content), _CHARS_PER_TOKEN_PROSE)
                            else:
                                file_tokens += _tokens_from_bytes(len(content), _CHARS_PER_TOKEN_CODE)
                        except Exception:
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
    live_quota_fetcher: Optional[Callable[..., LiveServerQuota]] = None,
) -> TokenStats:
    """Processes transcript steps and consolidates 3-layer token telemetry."""
    limits = get_model_limits(model_name)
    eff_sys_bytes = system_prompt_bytes if system_prompt_bytes > 0 else _measure_system_prompt_bytes()
    sys_tokens = _tokens_from_bytes(eff_sys_bytes, _CHARS_PER_TOKEN_CONFIG)

    last_checkpoint_idx = -1
    for i in range(len(steps) - 1, -1, -1):
        if steps[i].get("type") == "CHECKPOINT":
            last_checkpoint_idx = i
            break

    last_pr_idx = -1
    for i in range(len(steps) - 1, -1, -1):
        s = steps[i]
        if s.get("type") == "PLANNER_RESPONSE" and (
            s.get("input_tokens") is not None or s.get("cache_read_tokens") is not None
        ):
            last_pr_idx = i
            break

    active_start_idx = max(0, last_checkpoint_idx) if last_checkpoint_idx >= 0 else 0
    active_steps_slice = steps[active_start_idx:]

    user_bytes = 0
    tool_bytes = 0
    model_bytes = 0
    active_prompt_model_bytes = 0
    tool_breakdown: Dict[str, Dict[str, int]] = {}
    active_steps = 0

    for step in active_steps_slice:
        stype = step.get("type", "UNKNOWN")
        if step.get("is_truncated", False) or stype in ("EPHEMERAL_MESSAGE", "SYSTEM_MESSAGE"):
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
                model_bytes += len(thinking)
            model_bytes += step_len
            active_prompt_model_bytes += step_len
        elif stype == "CONVERSATION_HISTORY":
            user_bytes += step_len // 2
        elif stype in ("CHECKPOINT", "KNOWLEDGE_ARTIFACTS"):
            user_bytes += step_len
        else:
            tool_bytes += step_len
            if stype not in tool_breakdown:
                tool_breakdown[stype] = {"bytes": 0, "tokens": 0, "calls": 0}
            tool_breakdown[stype]["bytes"] += step_len
            tool_breakdown[stype]["calls"] += 1

    user_tokens = _tokens_from_bytes(user_bytes, _CHARS_PER_TOKEN_PROSE)
    tool_tokens = _tokens_from_bytes(tool_bytes, _CHARS_PER_TOKEN_CODE)
    model_tokens = _tokens_from_bytes(model_bytes, _CHARS_PER_TOKEN_MIXED)

    for t_data in tool_breakdown.values():
        t_data["tokens"] = _tokens_from_bytes(t_data["bytes"], _CHARS_PER_TOKEN_CODE)

    sorted_tools = dict(sorted(tool_breakdown.items(), key=lambda item: item[1]["bytes"], reverse=True))

    if last_pr_idx >= 0 and last_pr_idx >= last_checkpoint_idx:
        pr_step = steps[last_pr_idx]
        api_base = int(pr_step.get("input_tokens") or 0) + int(pr_step.get("cache_read_tokens") or 0)
        pr_out = int(pr_step.get("output_tokens") or 0)
        if pr_out == 0:
            pr_content = pr_step.get("content", "")
            if not isinstance(pr_content, str):
                pr_content = json.dumps(pr_content) if pr_content else ""
            pr_out = _tokens_from_bytes(len(pr_content), _CHARS_PER_TOKEN_MIXED)

        delta_tokens = 0
        for s_after in steps[last_pr_idx + 1 :]:
            st_after = s_after.get("type", "UNKNOWN")
            if s_after.get("is_truncated", False) or st_after in ("EPHEMERAL_MESSAGE", "SYSTEM_MESSAGE"):
                continue
            c_after = s_after.get("content", "")
            if not isinstance(c_after, str):
                c_after = json.dumps(c_after) if c_after else ""
            if st_after == "USER_INPUT":
                delta_tokens += _tokens_from_bytes(len(c_after), _CHARS_PER_TOKEN_PROSE)
            elif st_after == "PLANNER_RESPONSE":
                delta_tokens += _tokens_from_bytes(len(c_after), _CHARS_PER_TOKEN_MIXED)
            else:
                delta_tokens += _tokens_from_bytes(len(c_after), _CHARS_PER_TOKEN_CODE)
        total_tokens = api_base + delta_tokens
    else:
        active_prompt_model_tokens = _tokens_from_bytes(active_prompt_model_bytes, _CHARS_PER_TOKEN_MIXED)
        total_tokens = sys_tokens + user_tokens + tool_tokens + active_prompt_model_tokens

    ctx_window = limits["context_window"]
    max_out = limits["max_output"]
    remaining = max(0, ctx_window - total_tokens)
    percent_used = (total_tokens / ctx_window) * 100.0 if ctx_window else 0.0

    prov_defaults = get_provider_defaults(model_name)
    if rolling is not None:
        eff_rolling = rolling
    else:
        eff_rolling = calculate_rolling_windows(
            limit_5h=prov_defaults["limit_5h"],
            limit_7d=prov_defaults["limit_7d"],
        )

    fetcher = live_quota_fetcher or fetch_live_antigravity_quota
    eff_live_quota = live_quota or (
        fetcher(rolling=eff_rolling, model_name=model_name) if fetch_live else LiveServerQuota()
    )
    resolved_effort = detect_effort(conversation_id, steps=steps, explicit_effort=effort)
    rtk_data = fetch_rtk_savings()

    return TokenStats(
        conversation_id=conversation_id,
        model_name=model_name,
        context_window=ctx_window,
        max_output=max_out,
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
        percent_used=percent_used,
        effort=resolved_effort,
        rolling=eff_rolling,
        live_quota=eff_live_quota,
        top_tools=sorted_tools,
        steps_count=active_steps,
        rtk_savings=rtk_data,
    )


def find_active_session(
    current_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[Path], Optional[str]]:
    """Finds the most recent active session across IDE and CLI, prioritizing current_dir."""
    home = Path.home()
    candidates = []
    cur_str = str(current_dir.resolve()) if current_dir and current_dir != home else None

    for app in ("antigravity-ide", "antigravity-cli"):
        brain_dir = home / ".gemini" / app / "brain"
        if brain_dir.is_dir():
            for conv_dir in brain_dir.iterdir():
                t_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
                if t_file.is_file():
                    mtime = t_file.stat().st_mtime
                    matches_cwd = False
                    if cur_str:
                        try:
                            with open(t_file, "r", encoding="utf-8", errors="ignore") as fp:
                                head = "".join([fp.readline() for _ in range(8)])
                                if cur_str in head:
                                    matches_cwd = True
                        except Exception:
                            pass
                    candidates.append((matches_cwd, mtime, conv_dir.name, t_file, app))
    if not candidates:
        return None, None, None
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best = candidates[0]
    return best[2], best[3], best[4]


def load_transcript(transcript_path: Path) -> List[Dict[str, Any]]:
    """Loads JSONL transcript steps."""
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


from scripts.telemetry.host_sessions import (
    find_active_host_session,
    find_active_opencode_session,
    parse_opencode_session,
)


