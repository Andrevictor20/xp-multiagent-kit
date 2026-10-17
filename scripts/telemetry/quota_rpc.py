#!/usr/bin/env python3
"""
scripts/telemetry/quota_rpc.py
Live Language Server RPC quota discovery, snapshot persistence, and RTK SQLite queries.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sqlite3
import ssl
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from scripts.telemetry.models import LiveQuotaBucket, LiveServerQuota, RollingWindowStats

QUOTA_SNAPSHOT_FILE = Path.home() / ".gemini" / "antigravity-cli" / "last_known_quota.json"
ACTIVE_LS_CONN_FILE = Path.home() / ".gemini" / "antigravity-cli" / "active_ls_conn.json"
_LIVE_QUOTA_CACHE: Dict[str, Any] = {"timestamp": 0.0, "data": None}


def clean_refresh_text(desc: Optional[str]) -> str:
    """Formats verbose refresh descriptions into concise PT strings (e.g. 'renova em 4 h, 49 m')."""
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


def save_quota_snapshot(
    quota: LiveServerQuota,
    anchor_tokens_5h: int = 0,
    anchor_tokens_7d: int = 0,
    target_file: Optional[Path] = None,
) -> bool:
    """Persists the last successful Language Server quota snapshot."""
    if not quota:
        return False
    target = target_file or QUOTA_SNAPSHOT_FILE
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        now_ts = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_ts))

        def bucket_to_dict(b: Optional[LiveQuotaBucket]) -> Optional[Dict[str, Any]]:
            if not b:
                return None
            return {
                "bucket_id": b.bucket_id,
                "display_name": b.display_name,
                "description": b.description,
                "window": b.window,
                "remaining_fraction": b.remaining_fraction,
                "reset_time": b.reset_time,
            }

        data = {
            "timestamp": now_ts,
            "datetime": now_str,
            "is_live": quota.is_live,
            "plan_name": quota.plan_name,
            "gemini_5h": bucket_to_dict(quota.gemini_5h),
            "gemini_weekly": bucket_to_dict(quota.gemini_weekly),
            "claude_5h": bucket_to_dict(quota.claude_5h),
            "claude_weekly": bucket_to_dict(quota.claude_weekly),
            "description": quota.description,
            "anchor_tokens_5h": anchor_tokens_5h,
            "anchor_tokens_7d": anchor_tokens_7d,
        }
        target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def load_quota_snapshot(target_file: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Loads persisted quota snapshot from disk."""
    target = target_file or QUOTA_SNAPSHOT_FILE
    if not target.is_file():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_active_ls_conn(
    port: int,
    token: str,
    scheme: str = "http",
    target_file: Optional[Path] = None,
) -> bool:
    """Persists active Language Server connection info for fast reuse."""
    if not port:
        return False
    target = target_file or ACTIVE_LS_CONN_FILE
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "port": port,
            "csrf_token": token,
            "scheme": scheme,
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def load_active_ls_conn(target_file: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Loads last active Language Server connection if younger than 12 hours."""
    target = target_file or ACTIVE_LS_CONN_FILE
    if not target.is_file():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if time.time() - float(data.get("timestamp", 0)) < 43200:
            return data
        return None
    except Exception:
        return None


def calculate_projected_quota(
    snapshot: Dict[str, Any],
    current_tokens_5h: int = 0,
    current_tokens_7d: int = 0,
    model_name: str = "gemini-3.8-flash",
) -> LiveServerQuota:
    """Projection disabled to avoid inaccurate heuristics."""
    return LiveServerQuota(
        is_live=False,
        is_projected=False,
        error="Não está sendo possível aferir no momento",
    )


def _query_quota_endpoint(
    port: int,
    token: str,
    scheme: str = "http",
    timeout: float = 0.5,
    urlopen_fn: Optional[Callable[..., Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Queries the official Language Server RetrieveUserQuotaSummary endpoint."""
    url = f"{scheme}://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary"
    ctx = ssl._create_unverified_context() if scheme == "https" else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["x-codeium-csrf-token"] = token
    req = urllib.request.Request(url, data=b"{}", headers=headers)
    opener = urlopen_fn or urllib.request.urlopen
    try:
        with opener(req, context=ctx, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and "response" in data:
                return data
    except Exception:
        return None
    return None


def fetch_live_antigravity_quota(
    force_refresh: bool = False,
    rolling: Optional[RollingWindowStats] = None,
    model_name: str = "gemini-3.8-flash",
    active_conn_file: Optional[Path] = None,
    cache_store: Optional[Dict[str, Any]] = None,
) -> LiveServerQuota:
    """Queries live Language Server quota via Fast Path (~5ms) or process/log discovery."""
    cache = cache_store if cache_store is not None else _LIVE_QUOTA_CACHE
    conn_file = active_conn_file or ACTIVE_LS_CONN_FILE
    now = time.time()
    if not force_refresh and cache.get("data") is not None and (now - cache.get("timestamp", 0.0) < 10.0):
        return cache["data"]

    raw_data: Optional[Dict[str, Any]] = None
    successful_conn: Optional[Tuple[int, str, str]] = None

    # 1. Fast Path: Active connection persisted on disk
    cached_conn = load_active_ls_conn(target_file=conn_file)
    if cached_conn:
        c_port = cached_conn.get("port")
        c_tok = cached_conn.get("csrf_token", "")
        c_scheme = cached_conn.get("scheme", "http")
        if c_port:
            res_cached = _query_quota_endpoint(int(c_port), c_tok, c_scheme, timeout=0.5)
            if res_cached and "response" in res_cached:
                raw_data = res_cached
                successful_conn = (int(c_port), c_tok, c_scheme)

    # 2. Fast Path: Direct environment variables
    if not raw_data:
        env_token = os.environ.get("ANTIGRAVITY_CSRF_TOKEN", "")
        env_addr = os.environ.get("ANTIGRAVITY_LS_ADDRESS", "")
        if env_token and env_addr:
            m_env = re.search(r":(\d+)", env_addr)
            if m_env:
                e_port = int(m_env.group(1))
                for s in ["http", "https"]:
                    res_env = _query_quota_endpoint(e_port, env_token, s, timeout=0.5)
                    if res_env and "response" in res_env:
                        raw_data = res_env
                        successful_conn = (e_port, env_token, s)
                        break

    # 3. Fallback Discovery (logs + /proc + listening ports)
    if not raw_data:
        ports_to_try: List[Tuple[int, str]] = []
        csrf_token = os.environ.get("ANTIGRAVITY_CSRF_TOKEN") or None

        log_patterns = [
            os.path.expanduser("~/.config/Antigravity IDE/logs/*/ls-main*.log"),
            os.path.expanduser("~/.config/Antigravity IDE/logs/*/window*/exthost/google.antigravity/*.log"),
            os.path.expanduser("~/.config/Antigravity/logs/*/ls-main*.log"),
            os.path.expanduser("~/.gemini/antigravity-cli/log/cli-*.log"),
        ]
        log_files: List[str] = []
        for pat in log_patterns:
            log_files.extend(glob.glob(pat))

        http_port = None
        https_port = None

        if log_files:
            try:
                latest_log = max(log_files, key=os.path.getmtime)
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
            except Exception:
                pass

        if not csrf_token or not ports_to_try:
            for p_env in glob.glob("/proc/[0-9]*/environ"):
                try:
                    with open(p_env, "rb") as ef:
                        edata = ef.read()
                        if b"ANTIGRAVITY_CSRF_TOKEN=" in edata:
                            items = dict(item.split(b"=", 1) for item in edata.split(b"\x00") if b"=" in item)
                            tok = items.get(b"ANTIGRAVITY_CSRF_TOKEN", b"").decode("utf-8", "ignore")
                            addr = items.get(b"ANTIGRAVITY_LS_ADDRESS", b"").decode("utf-8", "ignore")
                            if tok and not csrf_token:
                                csrf_token = tok
                            if addr and tok:
                                m_a = re.search(r":(\d+)", addr)
                                if m_a:
                                    ports_to_try.append((int(m_a.group(1)), tok))
                                    break
                except Exception:
                    pass

        candidates = []
        for cmd_path in glob.glob("/proc/[0-9]*/cmdline"):
            try:
                with open(cmd_path, "rb") as f:
                    parts = f.read().split(b"\x00")
                    is_match = any(
                        any(name in p for name in [b"language_server", b"agy-native", b"agy-bin", b"antigravity"])
                        for p in parts
                    )
                    if is_match:
                        pid = os.path.basename(os.path.dirname(cmd_path))
                        tok = None
                        if b"--csrf_token" in parts:
                            idx = parts.index(b"--csrf_token")
                            tok = parts[idx + 1].decode("utf-8", errors="ignore")
                        elif csrf_token:
                            tok = csrf_token
                        else:
                            tok = ""
                        candidates.append((pid, tok))
            except Exception:
                pass

        for pid, token in candidates:
            try:
                out_lsof = subprocess.check_output(
                    ["lsof", "-Pan", "-p", pid, "-iTCP", "-sTCP:LISTEN"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=0.6,
                )
                for m in re.finditer(r":(\d+)\s+\(LISTEN\)", out_lsof):
                    ports_to_try.append((int(m.group(1)), token))
            except Exception:
                pass

        if not ports_to_try:
            tok_fallback = csrf_token or ""
            for p in [p for p in [http_port, https_port, 44351, 39831, 36977, 43923] if p]:
                ports_to_try.append((p, tok_fallback))

        ports_to_try = list(dict.fromkeys(ports_to_try))
        for port, token in ports_to_try:
            for scheme in ["http", "https"]:
                res_disc = _query_quota_endpoint(port, token, scheme, timeout=0.5)
                if res_disc and "response" in res_disc:
                    raw_data = res_disc
                    successful_conn = (port, token, scheme)
                    break
            if raw_data:
                break

    if successful_conn and successful_conn[1]:
        try:
            save_active_ls_conn(successful_conn[0], successful_conn[1], successful_conn[2], target_file=conn_file)
        except Exception:
            pass

    if not raw_data or "response" not in raw_data:
        quota = LiveServerQuota(is_live=False, error="Não está sendo possível aferir no momento")
        cache["timestamp"] = now
        cache["data"] = quota
        return quota

    res = raw_data.get("response", {})
    gem_5h = None
    gem_week = None
    gem_argon_week = None
    claude_5h = None
    claude_week = None

    for grp in res.get("groups", []):
        grp_name = grp.get("displayName", "")
        buckets = grp.get("buckets", [])
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
            if "Argon" in grp_name or "argon" in bid.lower():
                gem_argon_week = bucket_obj
            elif "Gemini" in grp_name:
                if win == "5h" or "5h" in bid:
                    gem_5h = bucket_obj
                elif win == "weekly" or "weekly" in bid:
                    gem_week = bucket_obj
            elif "Claude" in grp_name or "GPT" in grp_name:
                if win == "5h" or "5h" in bid:
                    claude_5h = bucket_obj
                elif win == "weekly" or "weekly" in bid:
                    claude_week = bucket_obj

    quota = LiveServerQuota(
        is_live=True,
        is_projected=False,
        plan_name="Google AI Pro",
        gemini_5h=gem_5h,
        gemini_weekly=gem_week,
        gemini_argon_weekly=gem_argon_week,
        claude_5h=claude_5h,
        claude_weekly=claude_week,
        description=res.get("description", ""),
        error=None,
        sync_timestamp=now,
        sync_datetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
    )
    cache["timestamp"] = now
    cache["data"] = quota

    try:
        a_5h = rolling.tokens_5h if rolling else 0
        a_7d = rolling.tokens_7d if rolling else 0
        save_quota_snapshot(quota, anchor_tokens_5h=a_5h, anchor_tokens_7d=a_7d)
    except Exception:
        pass

    return quota


def fetch_rtk_savings(db_path: Optional[Path] = None, project_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Queries RTK (Rust Token Killer) SQLite history database."""
    target = db_path or (Path.home() / ".local" / "share" / "rtk" / "history.db")
    if not target.is_file():
        return None
    try:
        conn = sqlite3.connect(str(target), timeout=0.2)
        cursor = conn.cursor()
        if project_path:
            cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(input_tokens), 0), COALESCE(SUM(output_tokens), 0), COALESCE(SUM(saved_tokens), 0) FROM commands WHERE project_path = ?",
                (project_path,),
            )
        else:
            cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(input_tokens), 0), COALESCE(SUM(output_tokens), 0), COALESCE(SUM(saved_tokens), 0) FROM commands"
            )
        row = cursor.fetchone()
        conn.close()
        if row and row[0] > 0:
            inp, outp, saved = int(row[1]), int(row[2]), int(row[3])
            pct = round((float(saved) / inp * 100.0), 1) if inp > 0 else 0.0
            return {
                "total_commands": int(row[0]),
                "input_tokens": inp,
                "output_tokens": outp,
                "saved_tokens": saved,
                "avg_savings_pct": pct,
            }
    except Exception:
        pass
    return None
