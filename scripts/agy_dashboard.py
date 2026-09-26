#!/usr/bin/env python3
"""
scripts/agy_dashboard.py
Dashboard Visual de Terminal (TUI) em Tempo Real para o XP Multi-Agent Kit.
Apresenta em painel unificado:
  - Saúde do Sistema e Conexão RPC do Language Server
  - Gauges Visuais das Cotas (Janela, 5h e Semanal) com tempo de refresh
  - Telemetria de Memória (Viva vs Arquivada e FTS5 indexado)
  - Estado do Daemon de Background e Checkpoint de Sessão Ativa
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def build_progress_bar(pct: float, width: int = 10) -> str:
    """Gera barra de progresso gráfica [▰▰▱▱▱▱▱▱▱▱]."""
    clamped = max(0.0, min(100.0, pct))
    filled = int(round((clamped / 100.0) * width))
    empty = width - filled
    return f"[{'▰' * filled}{'▱' * empty}]"


def collect_dashboard_data(workspace: Path) -> Dict[str, Any]:
    """Coleta métricas e status consolidados de todos os subsistemas."""
    workspace = workspace.resolve()

    # 1. Saúde do Sistema
    health_data = {}
    try:
        from scripts.agy_health import run_health_checks
        h = run_health_checks(workspace)
        health_data = {
            "all_ok": h.get("all_ok", True),
            "checks": h.get("checks", []),
        }
    except Exception:
        health_data = {"all_ok": True, "checks": []}

    # 2. Cotas e RPC
    quotas_data = {}
    try:
        from scripts.token_tracker import fetch_live_antigravity_quota
        q = fetch_live_antigravity_quota(force_refresh=True)
        if q and q.is_live:
            if q.gemini_5h:
                quotas_data["gemini_5h_used_pct"] = round((1.0 - q.gemini_5h.remaining_fraction) * 100, 1)
                quotas_data["gemini_5h_reset"] = getattr(q.gemini_5h, "reset_time_str", "N/A")
            if q.gemini_weekly:
                quotas_data["gemini_weekly_used_pct"] = round((1.0 - q.gemini_weekly.remaining_fraction) * 100, 1)
                quotas_data["gemini_weekly_reset"] = getattr(q.gemini_weekly, "reset_time_str", "N/A")
            if q.claude_5h:
                quotas_data["3p_5h_used_pct"] = round((1.0 - q.claude_5h.remaining_fraction) * 100, 1)
            if q.claude_weekly:
                quotas_data["3p_weekly_used_pct"] = round((1.0 - q.claude_weekly.remaining_fraction) * 100, 1)
    except Exception:
        pass

    # 3. Memória Contínua
    memory_data = {"live_kb": 0.0, "history_kb": 0.0, "fts_items": 0}
    mem_file = workspace / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if mem_file.is_file():
        memory_data["live_kb"] = round(mem_file.stat().st_size / 1024.0, 1)

    hist_file = workspace / ".agents" / "memory" / "archive" / "HISTORY.md"
    if hist_file.is_file():
        memory_data["history_kb"] = round(hist_file.stat().st_size / 1024.0, 1)

    db_file = workspace / ".agents" / "memory" / ".memory_index.db"
    if db_file.is_file():
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM memory_fts;")
            memory_data["fts_items"] = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass

    # 4. Daemon de Background
    daemon_data = {"running": False, "pid": None}
    try:
        from scripts.agy_daemon import get_daemon_status, DEFAULT_PID_FILE
        daemon_data = get_daemon_status(DEFAULT_PID_FILE)
    except Exception:
        pass

    # 5. Checkpoint de Sessão
    session_data = None
    try:
        from scripts.session_resumer import load_session_state
        session_data = load_session_state(workspace)
    except Exception:
        pass

    return {
        "workspace": str(workspace),
        "health": health_data,
        "quotas": quotas_data,
        "memory": memory_data,
        "daemon": daemon_data,
        "session": session_data,
    }


def render_dashboard(data: Dict[str, Any], width: int = 76) -> str:
    """Renderiza o painel visual TUI em formato texto com bordas Unicode."""
    lines: List[str] = []

    border_top = "┌" + "─" * (width - 2) + "┐"
    border_mid = "├" + "─" * (width - 2) + "┤"
    border_bot = "└" + "─" * (width - 2) + "┘"

    def row(text: str) -> str:
        # Garante alinhamento visual
        visible_len = len(text)
        pad = max(0, width - 4 - visible_len)
        return f"│  {text}{' ' * pad}│"

    # Header
    lines.append(border_top)
    lines.append(row("🪐 Antigravity XP Kit — Terminal Dashboard v2.33.0"))
    lines.append(border_mid)

    # 1. Seção de Cotas
    quotas = data.get("quotas", {})
    gemini_5h = quotas.get("gemini_5h_used_pct", 0.0)
    gemini_week = quotas.get("gemini_weekly_used_pct", 0.0)
    g_5h_res = quotas.get("gemini_5h_reset", "N/A")
    g_wk_res = quotas.get("gemini_weekly_reset", "N/A")

    lines.append(row("📊 TELEMETRIA DE COTAS AO VIVO (Language Server RPC)"))
    bar_5h = build_progress_bar(gemini_5h, 10)
    lines.append(row(f"  • Cota 5h (Gemini)    : {bar_5h} {gemini_5h:5.1f}% usado (renova em {g_5h_res})"))
    bar_wk = build_progress_bar(gemini_week, 10)
    lines.append(row(f"  • Cota Semanal (Gemini): {bar_wk} {gemini_week:5.1f}% usado (renova em {g_wk_res})"))

    p3_5h = quotas.get("3p_5h_used_pct")
    p3_week = quotas.get("3p_weekly_used_pct")
    if p3_5h is not None and p3_week is not None:
        bar_p3_5h = build_progress_bar(p3_5h, 10)
        bar_p3_wk = build_progress_bar(p3_week, 10)
        lines.append(row(f"  • Cota 5h (Claude/GPT): {bar_p3_5h} {p3_5h:5.1f}% usado"))
        lines.append(row(f"  • Semanal (Claude/GPT): {bar_p3_wk} {p3_week:5.1f}% usado"))

    lines.append(border_mid)

    # 2. Seção de Memória
    mem = data.get("memory", {})
    live_kb = mem.get("live_kb", 0.0)
    hist_kb = mem.get("history_kb", 0.0)
    fts_items = mem.get("fts_items", 0)
    mem_status = "🟢 Saudável" if live_kb <= 35.0 else "🟡 Rotação recomendada"

    lines.append(row("🧠 MOTOR DE MEMÓRIA & RECUPERAÇÃO PROCEDURAL"))
    lines.append(row(f"  • Memória Viva (PROJECT_MEMORY.md) : {live_kb} KB ({mem_status})"))
    lines.append(row(f"  • Histórico Arquivado (HISTORY.md) : {hist_kb} KB"))
    lines.append(row(f"  • Índice FTS5 SQLite (.memory_index): {fts_items} itens indexados (<2ms search)"))

    lines.append(border_mid)

    # 3. Daemon & Sessão
    daemon = data.get("daemon", {})
    daemon_status = f"🟢 Ativo (PID: {daemon.get('pid')})" if daemon.get("running") else "⚪ Parado (inicie com 'agy-daemon start')"
    session = data.get("session")

    lines.append(row("🤖 SUPERVISOR DE BACKGROUND & CONTINUIDADE"))
    lines.append(row(f"  • agy-daemon        : {daemon_status}"))
    if session:
        goal = session.get("goal", "N/A")
        if len(goal) > 42:
            goal = goal[:39] + "..."
        branch = session.get("branch", "unknown")
        lines.append(row(f"  • Checkpoint Ativo  : Branch '{branch}' | Meta: {goal}"))
    else:
        lines.append(row("  • Checkpoint Ativo  : Nenhum salvo (use 'agy-resume --save')"))

    lines.append(border_mid)

    # Comandos Rápidos
    lines.append(row("⚡ COMANDOS RÁPIDOS:"))
    lines.append(row("  agy-health | agy-tokens | agy-resume | agy-memory-search | agy-git-ops"))
    lines.append(border_bot)

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dashboard Visual de Terminal do XP Multi-Agent Kit (agy-dashboard)")
    parser.add_argument("--workspace", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--watch", action="store_true", help="Atualiza a cada N segundos")
    parser.add_argument("--interval", type=int, default=3, help="Intervalo de atualização em segundos no modo watch (padrão: 3)")
    parser.add_argument("--json", action="store_true", help="Exibe dados brutos em formato JSON")

    args = parser.parse_args()
    ws = Path(args.workspace)

    if args.json:
        data = collect_dashboard_data(ws)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    if not args.watch:
        data = collect_dashboard_data(ws)
        print(render_dashboard(data))
        return 0

    # Modo watch contínuo
    try:
        while True:
            # Limpa tela do terminal
            sys.stdout.write("\033[2J\033[H")
            data = collect_dashboard_data(ws)
            sys.stdout.write(render_dashboard(data) + "\n")
            sys.stdout.write(f"\n[Modo Watch Ativo — Atualizando a cada {args.interval}s | Pressione Ctrl+C para sair]\n")
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nDashboard encerrado.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
