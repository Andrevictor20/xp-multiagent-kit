#!/usr/bin/env python3
"""
scripts/token_tracker.py — Compact & Multi-Host Token Telemetry CLI & Facade
XP Multi-Agent Kit v3.0

Modularized into scripts/telemetry/{models,quota_rpc,parser,formatter}.py (< 500 lines rule).
Preserves 100% backward-compatible imports for all existing scripts, hooks, and tests.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.telemetry.formatter import (
     audit_token_bottlenecks,
    check_budget_status,
    format_badge,
    format_compact_footer,
    format_json_stats,
    format_markdown_report,
    format_message_footer,
    format_terminal_telemetry,
    make_progress_bar,
    render_plain_dashboard,
    render_rich_dashboard,
)
from scripts.telemetry.models import (
    DEFAULT_LIMIT_5H,
    DEFAULT_LIMIT_WEEKLY,
    DEFAULT_SYSTEM_PROMPT_BYTES,
     LiveQuotaBucket,
    LiveServerQuota,
    MODEL_DISPLAY_NAMES,
    MODEL_LIMITS,
    PROVIDER_RATE_LIMITS,
    RollingWindowStats,
    TokenStats,
    TurnStats,
    detect_effort,
    detect_model_name,
    detect_model_name_from_steps,
    get_model_display_name,
    get_model_limits,
    get_provider_defaults,
    human_tokens,
    parse_token_limit,
)
from scripts.telemetry.parser import (
    calculate_rolling_windows,
    calculate_turn_stats,
    estimate_tokens,
    find_active_host_session,
    find_active_session,
    load_transcript,
    parse_transcript_data as _parse_transcript_data,
)
from scripts.telemetry.quota_rpc import (
    ACTIVE_LS_CONN_FILE,
    QUOTA_SNAPSHOT_FILE,
    _LIVE_QUOTA_CACHE,
    calculate_projected_quota,
    clean_refresh_text,
    fetch_live_antigravity_quota as _fetch_live_quota,
    fetch_rtk_savings,
    load_active_ls_conn,
    load_quota_snapshot,
    save_active_ls_conn,
    save_quota_snapshot,
)


def fetch_live_antigravity_quota(
    force_refresh: bool = False,
    rolling: Optional[RollingWindowStats] = None,
    model_name: str = "gemini-3.8-flash",
) -> LiveServerQuota:
    """Wrapper binding module-level ACTIVE_LS_CONN_FILE and _LIVE_QUOTA_CACHE for mock compatibility."""
    return _fetch_live_quota(
        force_refresh=force_refresh,
        rolling=rolling,
        model_name=model_name,
        active_conn_file=ACTIVE_LS_CONN_FILE,
        cache_store=_LIVE_QUOTA_CACHE,
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
    """Wrapper passing module-bound fetch_live_antigravity_quota."""
    return _parse_transcript_data(
        conversation_id=conversation_id,
        model_name=model_name,
        steps=steps,
        system_prompt_bytes=system_prompt_bytes,
        rolling=rolling,
        live_quota=live_quota,
        fetch_live=fetch_live,
        effort=effort,
        live_quota_fetcher=fetch_live_antigravity_quota,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="XP Multi-Agent Kit — Compact Token & Quota Telemetry")
    parser.add_argument("-c", "--conversation-id", help="Specific conversation ID to inspect")
    parser.add_argument("-m", "--model", help="Override active model name")
    parser.add_argument("-e", "--effort", help="Override reasoning effort (low, medium, high)")
    parser.add_argument("--host", choices=["auto", "antigravity", "opencode", "cursor", "codex", "qoder"], default="auto", help="Target host IDE/CLI environment")
    parser.add_argument("-w", "--watch", action="store_true", help="Continuous live watch mode")
    parser.add_argument("-i", "--interval", type=int, default=2, help="Refresh interval in seconds")
    parser.add_argument("--limit-5h", help="5h rolling window token limit (e.g. 800k)")
    parser.add_argument("--limit-weekly", help="Weekly token limit (e.g. 10M)")
    parser.add_argument("--badge", action="store_true", help="Print inline Markdown telemetry badge")
    parser.add_argument("--turn", action="store_true", help="Print compact turn telemetry footer")
    parser.add_argument("--legacy-footer", action="store_true", help="Print legacy verbose turn footer")
    parser.add_argument("--color", action="store_true", help="Force ANSI colors in terminal output")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--json", action="store_true", help="Export telemetry as JSON")
    parser.add_argument("--report", action="store_true", help="Write .agents/memory/TOKEN_TELEMETRY.md")
    parser.add_argument("--check", action="store_true", help="Evaluate token budget health (exit 2 if critical)")
    parser.add_argument("--audit", action="store_true", help="Audit top consuming tools and bottlenecks")
    parser.add_argument("--plain", action="store_true", help="Print legacy plain dashboard")
    args = parser.parse_args()

    limit_5h = parse_token_limit(args.limit_5h, DEFAULT_LIMIT_5H) if args.limit_5h else None
    limit_7d = parse_token_limit(args.limit_weekly, DEFAULT_LIMIT_WEEKLY) if args.limit_weekly else None

    while True:
        stats, turn, host_found = find_active_host_session(
            host=args.host,
            conv_id=args.conversation_id,
            model_override=args.model,
            effort=args.effort,
        )

        if not stats or not turn:
            sys.stderr.write("Nenhuma conversa ativa encontrada.\n")
            if not args.watch:
                sys.exit(1)
            time.sleep(args.interval)
            continue

        if limit_5h or limit_7d:
            if limit_5h:
                stats.rolling.limit_5h = limit_5h
            if limit_7d:
                stats.rolling.limit_7d = limit_7d

        if args.turn:
            if args.color:
                print(format_terminal_telemetry(stats, turn, use_color=True))
            elif args.legacy_footer:
                print(format_message_footer(stats, turn, compact=False))
            else:
                print(format_message_footer(stats, turn, compact=True))
            return

        if args.check:
            status, is_low, msg = check_budget_status(stats)
            print(f"[{status}] {msg}")
            sys.exit(2 if is_low else 0)

        if args.audit:
            audit = audit_token_bottlenecks(stats)
            print(f"Sessão: {audit['conversation_id']} | Total: {audit['total_tokens']:,} tokens")
            for b in audit["bottlenecks"]:
                print(f" • {b['tool']}: {b['tokens']:,} tok ({b['percent']}%) -> {b['recommendation']}")
            return

        if args.badge:
            print(format_badge(stats))
            return

        if args.json:
            print(format_json_stats(stats))
            return

        if args.report:
            report_text = format_markdown_report(stats)
            report_path = (Path.cwd() / "memory" / "TOKEN_TELEMETRY.md") if Path.cwd().name == ".agents" else (Path.cwd() / ".agents" / "memory" / "TOKEN_TELEMETRY.md")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_text, encoding="utf-8")
            print(f"Relatório gravado com sucesso em: {report_path.resolve()}")
            return

        if args.plain:
            render_plain_dashboard(stats)
        else:
            use_c = False if args.no_color else (True if args.color else sys.stdout.isatty())
            print(format_terminal_telemetry(stats, turn, use_color=use_c))

        if not args.watch:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
