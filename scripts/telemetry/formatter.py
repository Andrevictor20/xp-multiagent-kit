#!/usr/bin/env python3
"""
scripts/telemetry/formatter.py
Formatting and rendering for Token Telemetry:
- Compact 3-line/4-line chat footer (only Contexto, Limites 5h/Semana, Consumo, Modelo)
- ANSI-colored terminal telemetry view (Green/Yellow/Red progress bars & badges)
- Legacy full footer compatibility (when compact=False)
- Rich/Plain dashboards, Markdown report, JSON export, and budget audit.
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any, Dict, Optional, Tuple

from scripts.telemetry.models import (
    TokenStats,
    TurnStats,
    get_model_display_name,
    human_tokens,
)
from scripts.telemetry.quota_rpc import clean_refresh_text

try:
    from scripts.turn_telemetry import summarize as _turn_summarize
except ImportError:
    try:
        from turn_telemetry import summarize as _turn_summarize  # type: ignore
    except ImportError:
        _turn_summarize = None  # type: ignore


# ANSI Escape Codes for Terminal Styling
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_GREEN = "\033[38;5;82m"
ANSI_YELLOW = "\033[38;5;220m"
ANSI_RED = "\033[38;5;196m"
ANSI_CYAN = "\033[38;5;81m"
ANSI_MAGENTA = "\033[38;5;177m"
ANSI_WHITE = "\033[38;5;255m"


def _pct_color(pct_used: float) -> str:
    if pct_used >= 80.0:
        return ANSI_RED
    if pct_used >= 50.0:
        return ANSI_YELLOW
    return ANSI_GREEN


def make_progress_bar(percent_used: float, width: int = 10, use_color: bool = False) -> str:
    """Generates a modern Unicode block bar (▰▰▰▰▱▱▱▱▱▱), optionally colored with ANSI."""
    p = max(0.0, min(100.0, percent_used))
    filled = int(round((p / 100.0) * width))
    empty = max(0, width - filled)
    if not use_color:
        return "▰" * filled + "▱" * empty
    c = _pct_color(p)
    return f"{c}{'▰' * filled}{ANSI_DIM}{'▱' * empty}{ANSI_RESET}"


def _format_resend_line(conversation_id: str) -> str:
    if _turn_summarize is None:
        return ""
    try:
        s = _turn_summarize(session_id=conversation_id)
    except Exception:
        return ""
    if not s.get("turns") or s.get("resend_tokens", 0) <= 0:
        return ""
    resend_str = human_tokens(int(s["resend_tokens"]))
    share = float(s.get("resend_share_pct", 0.0))
    return f"Reenvio:  {resend_str} tokens acumulados ({share:.1f}% do total da sessão)  \n"


def _extract_quota_metrics(stats: TokenStats) -> Tuple[bool, float, float, str, float, float, str]:
    """Returns (is_live, pct_5h_used, pct_5h_rem, desc_5h, pct_7d_used, pct_7d_rem, desc_7d)."""
    if stats.live_quota and stats.live_quota.is_live:
        model_lower = (stats.model_name or "").lower()
        is_argon = "argon" in model_lower
        is_claude = "claude" in model_lower or "gpt" in model_lower

        if is_argon and getattr(stats.live_quota, "gemini_argon_weekly", None):
            b_5h = stats.live_quota.gemini_5h
            b_7d = stats.live_quota.gemini_argon_weekly
        elif is_claude:
            b_5h = stats.live_quota.claude_5h
            b_7d = stats.live_quota.claude_weekly
        else:
            b_5h = stats.live_quota.gemini_5h
            b_7d = stats.live_quota.gemini_weekly

        pct_5h_rem = (b_5h.remaining_fraction * 100.0) if b_5h else 100.0
        pct_7d_rem = (b_7d.remaining_fraction * 100.0) if b_7d else 100.0
        pct_5h_used = max(0.0, 100.0 - pct_5h_rem)
        pct_7d_used = max(0.0, 100.0 - pct_7d_rem)

        desc_5h = clean_refresh_text(b_5h.description) if b_5h else ""
        desc_7d = clean_refresh_text(b_7d.description) if b_7d else ""
        return True, pct_5h_used, pct_5h_rem, desc_5h, pct_7d_used, pct_7d_rem, desc_7d
    return False, 0.0, 0.0, "", 0.0, 0.0, ""


def format_compact_footer(stats: Any, turn: Optional[TurnStats] = None) -> str:
    """
    Renders the compact 4-line footer showing:
    Contexto, Limites (5h & Semana), Consumo, and Modelo (with host attribution if non-default).
    Clean, aligned, zero clutter.
    """
    if isinstance(stats, dict):
        total_tokens = stats.get("total_tokens", 0)
        limits = stats.get("limits", {})
        context_window = limits.get("context_window", 1_000_000)
        max_output = limits.get("max_output", 65_536)
        percent_used = stats.get("percent_used", 0.0)
        model_name = stats.get("model_name", "default")
        effort = stats.get("effort", "")
        host = stats.get("host", "")
        if turn is None and "turn_tokens" in stats:
            tt = stats["turn_tokens"]
            turn = TurnStats(
                user_input_tokens=tt.get("user", 0),
                tool_tokens=tt.get("tool", 0),
                model_output_tokens=tt.get("model", 0),
                total_tokens=tt.get("total", 0),
            )
    else:
        total_tokens = stats.total_tokens
        context_window = stats.context_window
        max_output = stats.max_output
        percent_used = stats.percent_used
        model_name = stats.model_name
        effort = stats.effort
        host = getattr(stats, "host", "")

    tot_str = human_tokens(total_tokens)
    win_str = human_tokens(context_window)
    max_out_str = human_tokens(max_output)
    display_model = get_model_display_name(model_name)
    effort_cap = effort.capitalize() if effort else "Medium"
    effort_tag = f" ({effort_cap})" if f"({effort_cap.lower()})" not in display_model.lower() else ""
    host_tag = f" • Host: {host.capitalize()}" if host and host.lower() != "antigravity" else ""

    t = turn or TurnStats()
    t_tot = human_tokens(t.total_tokens)
    t_in = human_tokens(t.user_input_tokens + t.ephemeral_tokens)
    t_tools = human_tokens(t.tool_tokens)
    t_out = human_tokens(t.model_output_tokens)

    bar_ctx = make_progress_bar(percent_used, 10, use_color=False)

    if isinstance(stats, dict) and "rate_limits" in stats:
        rl = stats["rate_limits"]
        r5 = rl.get("rolling_5h", {})
        r7 = rl.get("rolling_weekly", {})
        p5_used = r5.get("percent", 0.0)
        p7_used = r7.get("percent", 0.0)
        p7_rem = max(0.0, 100.0 - p7_used)
        bar_5h = make_progress_bar(p5_used, 8, use_color=False)
        bar_7d = make_progress_bar(p7_used, 8, use_color=False)
        limites_line = (
            f"Limites:  5h [{bar_5h}] {p5_used:.1f}% usado • "
            f"Semana [{bar_7d}] **{p7_rem:.1f}% livre**  \n"
        )
    else:
        is_live, p5_used, p5_rem, d5, p7_used, p7_rem, d7 = _extract_quota_metrics(stats)
        if is_live:
            bar_5h = make_progress_bar(p5_used, 8, use_color=False)
            bar_7d = make_progress_bar(p7_used, 8, use_color=False)
            d5_s = f" ({d5.replace('renova em ', '↻ ')})" if d5 else ""
            d7_s = f" ({d7.replace('renova em ', '↻ ')})" if d7 else ""
            limites_line = (
                f"Limites:  5h [{bar_5h}] {p5_used:.1f}% usado{d5_s} • "
                f"Semana [{bar_7d}] **{p7_rem:.1f}% livre**{d7_s}  \n"
            )
        else:
            r5 = human_tokens(stats.rolling.tokens_5h) if stats.rolling else "0"
            r7 = human_tokens(stats.rolling.tokens_7d) if stats.rolling else "0"
            limites_line = f"Limites:  5h: {r5} locais • Semana: {r7} locais (RPC offline)  \n"

    return (
        f"Contexto: [{bar_ctx}] {percent_used:.1f}% ({tot_str} / {win_str})  \n"
        f"{limites_line}"
        f"Consumo:  {t_tot} tok (In: {t_in} | Tool: {t_tools} | Out: {t_out})  \n"
        f"Modelo:   {display_model}{effort_tag}{host_tag} • Janela: {win_str} • Saída: {max_out_str}"
    )


def format_terminal_telemetry(
    stats: TokenStats,
    turn: Optional[TurnStats] = None,
    use_color: Optional[bool] = None,
) -> str:
    """
    Renders a visually sleek, ANSI-colored 4-line telemetry card for the terminal CLI.
    Shows ONLY Contexto, Limites (5h & Semana), Consumo, and Modelo.
    """
    color = sys.stdout.isatty() if use_color is None else use_color
    if not color:
        return format_compact_footer(stats, turn).replace("  \n", "\n").replace("**", "")

    tot_str = human_tokens(stats.total_tokens)
    win_str = human_tokens(stats.context_window)
    max_out_str = human_tokens(stats.max_output)
    display_model = get_model_display_name(stats.model_name)
    effort_cap = stats.effort.capitalize() if stats.effort else "Medium"
    effort_tag = f" ({effort_cap})" if f"({effort_cap.lower()})" not in display_model.lower() else ""

    t = turn or TurnStats()
    t_tot = human_tokens(t.total_tokens)
    t_in = human_tokens(t.user_input_tokens + t.ephemeral_tokens)
    t_tools = human_tokens(t.tool_tokens)
    t_out = human_tokens(t.model_output_tokens)

    c_ctx = _pct_color(stats.percent_used)
    bar_ctx = make_progress_bar(stats.percent_used, 10, use_color=True)

    is_live, p5_used, p5_rem, d5, p7_used, p7_rem, d7 = _extract_quota_metrics(stats)
    if is_live:
        c5 = _pct_color(p5_used)
        c7 = _pct_color(p7_used)
        bar_5h = make_progress_bar(p5_used, 8, use_color=True)
        bar_7d = make_progress_bar(p7_used, 8, use_color=True)
        d5_s = f" {ANSI_DIM}({d5.replace('renova em ', '↻ ')}){ANSI_RESET}" if d5 else ""
        d7_s = f" {ANSI_DIM}({d7.replace('renova em ', '↻ ')}){ANSI_RESET}" if d7 else ""
        lim_str = (
            f"{ANSI_BOLD}{ANSI_CYAN}Limites:{ANSI_RESET}  "
            f"5h [{bar_5h}] {c5}{p5_used:.1f}%{ANSI_RESET}{d5_s}  •  "
            f"Semana [{bar_7d}] {ANSI_BOLD}{c7}{p7_rem:.1f}% livre{ANSI_RESET}{d7_s}"
        )
    else:
        r5 = human_tokens(stats.rolling.tokens_5h) if stats.rolling else "0"
        r7 = human_tokens(stats.rolling.tokens_7d) if stats.rolling else "0"
        lim_str = (
            f"{ANSI_BOLD}{ANSI_CYAN}Limites:{ANSI_RESET}  "
            f"5h: {ANSI_YELLOW}{r5}{ANSI_RESET} locais  •  "
            f"Semana: {ANSI_YELLOW}{r7}{ANSI_RESET} locais {ANSI_DIM}(RPC offline){ANSI_RESET}"
        )

    lines = [
        f"{ANSI_BOLD}{ANSI_CYAN}Contexto:{ANSI_RESET} [{bar_ctx}] {ANSI_BOLD}{c_ctx}{stats.percent_used:.1f}%{ANSI_RESET} {ANSI_WHITE}({tot_str} / {win_str}){ANSI_RESET}",
        lim_str,
        f"{ANSI_BOLD}{ANSI_CYAN}Consumo:{ANSI_RESET}  {ANSI_BOLD}{ANSI_WHITE}{t_tot}{ANSI_RESET} tok {ANSI_DIM}(In: {t_in} │ Tool: {t_tools} │ Out: {t_out}){ANSI_RESET}",
        f"{ANSI_BOLD}{ANSI_CYAN}Modelo:{ANSI_RESET}   {ANSI_BOLD}{ANSI_MAGENTA}{display_model}{effort_tag}{ANSI_RESET} {ANSI_DIM}• Janela: {win_str} • Saída: {max_out_str}{ANSI_RESET}",
    ]
    return "\n".join(lines)


def format_message_footer(
    stats: TokenStats,
    turn: Optional[TurnStats] = None,
    compact: bool = False,
) -> str:
    """
    Formats the chat message telemetry footer.
    - When compact=True (used by --turn and hooks in v3.0): outputs the sleek 4-line block.
    - When compact=False (default for legacy unit test calls): preserves legacy fields.
    """
    if compact:
        return format_compact_footer(stats, turn)

    tot_str = human_tokens(stats.total_tokens)
    win_str = human_tokens(stats.context_window)
    max_out_str = human_tokens(stats.max_output)
    display_model = get_model_display_name(stats.model_name)

    consumo_line = ""
    if turn is not None:
        t_tot = human_tokens(turn.total_tokens)
        effective_input_tokens = turn.user_input_tokens + turn.ephemeral_tokens
        t_in = human_tokens(effective_input_tokens)
        t_tools = human_tokens(turn.tool_tokens)
        t_out = human_tokens(turn.model_output_tokens)

        pct_win_turn = (turn.total_tokens / stats.context_window * 100.0) if stats.context_window else 0.0
        pct_win_str = "<0.1%" if (0 < pct_win_turn < 0.1) else f"{pct_win_turn:.1f}%"

        tot_t = max(1, turn.total_tokens)
        pct_in = int(round((effective_input_tokens / tot_t) * 100.0)) if turn.total_tokens > 0 else 0
        pct_tools = int(round((turn.tool_tokens / tot_t) * 100.0)) if turn.total_tokens > 0 else 0
        pct_out = max(0, 100 - pct_in - pct_tools) if turn.total_tokens > 0 else 0

        consumo_line = (
            f"Consumo:  {t_tot} tokens ({pct_win_str} da janela) • "
            f"Entrada: {t_in} ({pct_in}%) | Ferramentas: {t_tools} ({pct_tools}%) | Resposta: {t_out} ({pct_out}%)  \n"
        )

    effort_cap = stats.effort.capitalize() if stats.effort else "Medium"
    effort_tag = f" (Effort: {effort_cap})"
    bar_ctx = make_progress_bar(stats.percent_used, 10)
    pct_ctx_rem = max(0.0, 100.0 - stats.percent_used)
    resend_line = _format_resend_line(stats.conversation_id)
    rtk_line = ""
    if stats.rtk_savings and stats.rtk_savings.get("saved_tokens", 0) > 0:
        s = stats.rtk_savings
        tok_saved = human_tokens(s.get("saved_tokens", 0))
        pct_saved = s.get("avg_savings_pct", 0.0)
        n_cmds = s.get("total_commands", 0)
        rtk_line = f"RTK:      ⚡ {tok_saved} economizados em {n_cmds} comandos ({pct_saved:.1f}% de redução)  \n"

    is_live, p5_used, p5_rem, d5, p7_used, p7_rem, d7 = _extract_quota_metrics(stats)
    if is_live:
        desc_5h_str = f" ({d5})" if d5 else ""
        desc_7d_str = f" ({d7})" if d7 else ""
        bar_5h = make_progress_bar(p5_used, 10)
        bar_7d = make_progress_bar(p7_used, 10)
        line_5h = f"5h:       [{bar_5h}] {p5_used:.1f}% usado • {p5_rem:.1f}% restante{desc_5h_str}  \n"
        line_7d = f"Semana:   [{bar_7d}] {p7_used:.1f}% usado • **{p7_rem:.1f}% restante**{desc_7d_str}  \n"
    else:
        line_5h = "5h:       Não está sendo possível aferir no momento  \n"
        line_7d = "Semana:   Não está sendo possível aferir no momento  \n"

    return (
        f"{consumo_line}"
        f"{resend_line}"
        f"{rtk_line}"
        f"Contexto: [{bar_ctx}] {stats.percent_used:.1f}% usado ({tot_str}) • {pct_ctx_rem:.1f}% livre de {win_str}  \n"
        f"{line_5h}"
        f"{line_7d}"
        f"Modelo:   {display_model}{effort_tag} | Janela: {win_str} | Saída: {max_out_str}"
    )


def format_badge(stats: TokenStats) -> str:
    """Formats inline Markdown telemetry badge."""
    tot_str = human_tokens(stats.total_tokens)
    win_str = human_tokens(stats.context_window)
    is_live, p5_used, p5_rem, d5, p7_used, p7_rem, d7 = _extract_quota_metrics(stats)

    if is_live:
        d5_s = f" ({d5})" if d5 else ""
        d7_s = f" ({d7})" if d7 else ""
        s_5h = f"`{p5_used:.1f}% usado • {p5_rem:.1f}% restante{d5_s}`"
        s_7d = f"`{p7_used:.1f}% usado • {p7_rem:.1f}% restante{d7_s}`"
    else:
        s_5h = "`Não está sendo possível aferir no momento`"
        s_7d = "`Não está sendo possível aferir no momento`"

    rtk_part = ""
    if stats.rtk_savings and stats.rtk_savings.get("saved_tokens", 0) > 0:
        s = stats.rtk_savings
        rtk_part = f" | ⚡ **RTK:** `{human_tokens(s['saved_tokens'])} (-{s['avg_savings_pct']:.1f}%)`"

    return (
        f"> 📊 **Token Telemetry ({stats.model_name}):** "
        f"**Contexto:** `{tot_str} / {win_str} ({stats.percent_used:.1f}%)` | "
        f"**5h:** {s_5h} | **Semana:** {s_7d}{rtk_part}"
    )


from scripts.telemetry.reports import (
    audit_token_bottlenecks,
    check_budget_status,
    format_json_stats,
    format_markdown_report,
    render_plain_dashboard,
)


def render_rich_dashboard(stats: TokenStats, turn: Optional[TurnStats] = None) -> None:
    """Renders compact colored terminal telemetry by default."""
    print(format_terminal_telemetry(stats, turn, use_color=True))

