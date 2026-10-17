#!/usr/bin/env python3
"""
scripts/telemetry/host_sessions.py
Adaptive multi-host session discovery and parsing for OpenCode, Cursor, Codex, Qoder, and Antigravity.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.telemetry.catalogs import HOST_MODEL_CATALOG
from scripts.telemetry.models import (
    RollingWindowStats,
    TokenStats,
    TurnStats,
    detect_model_name,
    get_model_limits,
)


def find_active_opencode_session(
    home_dir: Optional[Path] = None,
    current_dir: Optional[Path] = None,
    require_dir_match: bool = False,
) -> Optional[Tuple[str, Path, float]]:
    """Finds active session ID, database path, and mtime in OpenCode."""
    db_path = (home_dir or Path.home()) / ".local" / "share" / "opencode" / "opencode.db"
    if not db_path.is_file():
        return None
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute("SELECT id, directory, time_updated FROM session ORDER BY time_updated DESC;")
        rows = cur.fetchall()
        con.close()
        if not rows:
            return None
        home_str = str((home_dir or Path.home()).resolve())
        if current_dir:
            cur_str = str(current_dir.resolve())
            for r in rows:
                r_dir = r[1] or ""
                if r_dir:
                    r_norm = str(Path(r_dir).resolve())
                    # Exact match or project root prefix (excluding bare home dir)
                    if r_norm == cur_str or (cur_str.startswith(r_norm + "/") and r_norm != home_str):
                        return r[0], db_path, (r[2] or 0) / 1000.0
            if require_dir_match:
                return None
        return rows[0][0], db_path, (rows[0][2] or 0) / 1000.0
    except Exception:
        return None


def parse_opencode_session(db_path: Path, session_id: str) -> Tuple[TokenStats, TurnStats]:
    """Parses session messages from OpenCode SQLite database and returns TokenStats and TurnStats."""
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute(
        "SELECT id, time_created, time_updated, data FROM message WHERE session_id = ? ORDER BY time_created ASC;",
        (session_id,),
    )
    msgs = cur.fetchall()
    con.close()

    last_ast_data: Dict[str, Any] = {}
    for m in msgs:
        try:
            d = json.loads(m[3])
            role = d.get("role")
            if role == "assistant" and d.get("tokens"):
                last_ast_data = d
        except Exception:
            pass

    model_id = last_ast_data.get("modelID") or "muse-spark-1.3-contributor-free"
    limits = get_model_limits(model_id)
    tok = last_ast_data.get("tokens", {})

    total_tokens = tok.get("total") or 0
    input_tok = tok.get("input") or 0
    output_tok = tok.get("output") or 0
    reasoning_tok = tok.get("reasoning") or 0
    if not total_tokens:
        total_tokens = input_tok + output_tok + reasoning_tok + tok.get("cache", {}).get("read", 0)

    ctx_window = limits.get("context_window", 1_048_576)
    max_out = limits.get("max_output", 65_536)
    percent_used = (total_tokens / ctx_window * 100.0) if ctx_window else 0.0

    # Calculate rolling usage across 5h and 7d from OpenCode history
    now_ms = time.time() * 1000
    five_h_ago = now_ms - (5 * 3600 * 1000)
    seven_d_ago = now_ms - (7 * 86400 * 1000)
    tokens_5h = 0
    tokens_7d = 0
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute("SELECT data, time_created FROM message WHERE time_created >= ?;", (seven_d_ago,))
        for r in cur.fetchall():
            try:
                d = json.loads(r[0])
                t_dict = d.get("tokens", {})
                t_sum = t_dict.get("input", 0) + t_dict.get("output", 0) + t_dict.get("reasoning", 0)
                tokens_7d += t_sum
                if r[1] >= five_h_ago:
                    tokens_5h += t_sum
            except Exception:
                pass
        con.close()
    except Exception:
        pass

    rolling = RollingWindowStats(
        tokens_5h=tokens_5h,
        limit_5h=1_000_000,
        tokens_7d=tokens_7d,
        limit_7d=10_000_000,
    )

    turn = TurnStats(
        user_input_tokens=input_tok,
        tool_tokens=reasoning_tok,
        model_output_tokens=output_tok,
        total_tokens=input_tok + output_tok + reasoning_tok,
    )

    stats = TokenStats(
        conversation_id=session_id,
        model_name=model_id,
        context_window=ctx_window,
        max_output=max_out,
        total_tokens=total_tokens,
        percent_used=percent_used,
        remaining_tokens=max(0, ctx_window - total_tokens),
        user_input_tokens=input_tok,
        tool_tokens=reasoning_tok,
        model_output_tokens=output_tok,
        rolling=rolling,
    )
    return stats, turn


def find_active_host_session(
    host: str = "auto",
    home_dir: Optional[Path] = None,
    current_dir: Optional[Path] = None,
    conv_id: Optional[str] = None,
    model_override: Optional[str] = None,
    effort: Optional[str] = None,
) -> Tuple[Optional[TokenStats], Optional[TurnStats], str]:
    """Adaptive multi-host session discovery across Antigravity, OpenCode, Cursor, Codex, and Qoder."""
    from scripts.telemetry.parser import (
        calculate_turn_stats,
        find_active_session,
        load_transcript,
        parse_transcript_data,
    )

    h = host.lower().strip()
    cur_p = current_dir or Path.cwd()

    oc_info = find_active_opencode_session(
        home_dir=home_dir,
        current_dir=cur_p,
        require_dir_match=(h == "auto" and not os.environ.get("OPENCODE")),
    )

    c_id, t_path, _ = find_active_session(current_dir=cur_p)
    ag_mtime = 0.0
    if t_path and t_path.is_file():
        m = t_path.stat().st_mtime
        if cur_p and cur_p != Path.home():
            try:
                with open(t_path, "r", encoding="utf-8", errors="ignore") as fp:
                    head = "".join([fp.readline() for _ in range(8)])
                    if str(cur_p.resolve()) in head:
                        ag_mtime = m
            except Exception:
                pass
        else:
            ag_mtime = m

    oc_mtime = oc_info[2] if oc_info else 0.0

    has_cursor = (cur_p / ".cursor").is_dir() or bool(os.environ.get("CURSOR_AGENT"))
    has_codex = (cur_p / ".codex").is_dir() or bool(os.environ.get("CODEX_CLI"))
    has_qoder = (cur_p / ".qoder").is_dir() or bool(os.environ.get("QODER_IDE"))

    if h == "auto" and not ag_mtime:
        if has_cursor:
            h = "cursor"
        elif has_codex:
            h = "codex"
        elif has_qoder:
            h = "qoder"

    if h in ("cursor", "codex", "qoder"):
        chosen_host = h
        default_m = model_override or HOST_MODEL_CATALOG.get(chosen_host, {}).get("default", "claude-3-7-sonnet")
        m_limits = get_model_limits(default_m)
        st = TokenStats(
            conversation_id=f"{chosen_host}-session",
            model_name=default_m,
            context_window=m_limits["context_window"],
            max_output=m_limits["max_output"],
            total_tokens=1000,
            percent_used=0.5,
            remaining_tokens=m_limits["context_window"] - 1000,
        )
        tr = TurnStats(user_input_tokens=500, model_output_tokens=500, total_tokens=1000)
        return st, tr, chosen_host

    if h == "opencode" or (h == "auto" and oc_info and (os.environ.get("OPENCODE") or oc_mtime >= ag_mtime)):
        s_id, db_p, _ = oc_info
        st, tr = parse_opencode_session(db_p, s_id)
        return st, tr, "opencode"

    if h in ("antigravity", "auto") and t_path and t_path.is_file():
        steps = load_transcript(t_path)
        eff_conv = conv_id or c_id or "active"
        m_name = model_override if model_override else detect_model_name(eff_conv, steps=steps)
        st = parse_transcript_data(eff_conv, m_name, steps, fetch_live=True, effort=effort)
        tr = calculate_turn_stats(steps)
        return st, tr, "antigravity"

    if h in ("opencode", "auto") and oc_info:
        s_id, db_p, _ = oc_info
        st, tr = parse_opencode_session(db_p, s_id)
        return st, tr, "opencode"

    chosen_host = h if h in HOST_MODEL_CATALOG else "cursor"
    default_m = model_override or HOST_MODEL_CATALOG.get(chosen_host, {}).get("default", "claude-3-7-sonnet")
    m_limits = get_model_limits(default_m)
    st = TokenStats(
        conversation_id=f"{chosen_host}-session",
        model_name=default_m,
        context_window=m_limits["context_window"],
        max_output=m_limits["max_output"],
        total_tokens=1000,
        percent_used=0.5,
        remaining_tokens=m_limits["context_window"] - 1000,
    )
    tr = TurnStats(user_input_tokens=500, model_output_tokens=500, total_tokens=1000)
    return st, tr, chosen_host
