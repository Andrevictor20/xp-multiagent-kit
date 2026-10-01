#!/usr/bin/env python3
"""
scripts/turn_telemetry.py
Telemetria local de turnos, agnóstica de provedor (D1-D5).

Motivo: a telemetria anterior dependia do Language Server RPC do Antigravity e
só media o OUTPUT incremental das ferramentas. O custo dominante de uma sessão
é invisível a essa métrica: cada turno reenvia system prompt + contexto base +
histórico. Este módulo mede exatamente isso, localmente, sem depender de IDE.

Métricas registradas por turno em .agents/runtime/turn_log.jsonl:
    context_base_tokens   custo fixo do kit (AGENTS.md + memória + índice de skills)
    tool_output_tokens    output incremental das ferramentas
    response_tokens       resposta do agente
    resend_tokens         (contexto base + histórico) reenviado naquele turno
    cumulative_resend     soma acumulada de reenvios na sessão

Uso:
    agy-turn --record --risk L1 --tools 4 --tool-chars 8200 --response-chars 1400
    agy-turn --report
    agy-turn --preflight
    agy-turn --top 5
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from scripts.kit_constants import (
        CHARS_PER_TOKEN,
        MIN_TURNS_FOR_RESEND_ALERT,
        PREFLIGHT_CONTEXT_PCT,
        PREFLIGHT_QUOTA_PCT,
        RESEND_SHARE_ALERT_PCT,
        TURN_BUDGET,
        TURN_LOG_FILE,
        kit_root,
        runtime_dir,
    )
except ImportError:  # pragma: no cover - execução direta
    from kit_constants import (  # type: ignore
        CHARS_PER_TOKEN,
        MIN_TURNS_FOR_RESEND_ALERT,
        PREFLIGHT_CONTEXT_PCT,
        PREFLIGHT_QUOTA_PCT,
        RESEND_SHARE_ALERT_PCT,
        TURN_BUDGET,
        TURN_LOG_FILE,
        kit_root,
        runtime_dir,
    )

CONTEXT_BASE_ARTIFACTS = (
    "AGENTS.md",
    ".agents/memory/PROJECT_MEMORY.md",
    ".agents/skills/SKILLS_INDEX.md",
)


def estimate_tokens(text: str) -> int:
    """Estimativa determinística de tokens (não depende de tokenizer externo)."""
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


def _file_tokens(path: Path) -> int:
    try:
        return estimate_tokens(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return 0


def measure_context_base(root: Optional[Path] = None) -> Dict[str, int]:
    """
    Custo fixo pago em TODO turno: regras globais + índice de memória + índice
    de skills. É a principal alavanca de economia do kit (A1/A2/A3).
    """
    base = root or kit_root()
    breakdown: Dict[str, int] = {}
    for relative in CONTEXT_BASE_ARTIFACTS:
        path = base / relative
        if path.is_file():
            breakdown[relative] = _file_tokens(path)

    skills_dir = base / ".agents" / "skills"
    if skills_dir.is_dir() and ".agents/skills/SKILLS_INDEX.md" not in breakdown:
        # Sem índice compacto: o catálogo de descrições é o que a IDE injeta
        catalog = 0
        for skill in sorted(skills_dir.glob("*/SKILL.md")):
            catalog += estimate_tokens(skill.read_text(encoding="utf-8", errors="ignore")[:1200])
        breakdown["skills_catalog"] = catalog

    breakdown["total"] = sum(breakdown.values())
    return breakdown


def turn_log_path() -> Path:
    return runtime_dir() / TURN_LOG_FILE


def load_turns(log_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    path = log_path or turn_log_path()
    if not path.is_file():
        return []
    turns: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            turns.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return turns


def record_turn(
    risk_level: str = "L1",
    tool_calls: int = 0,
    tool_chars: int = 0,
    response_chars: int = 0,
    history_chars: int = 0,
    session_id: Optional[str] = None,
    log_path: Optional[Path] = None,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Registra um turno e devolve a entrada gravada (com reenvio calculado)."""
    session = session_id or "default"
    context_base = measure_context_base(root)["total"]
    history_tokens = history_chars // CHARS_PER_TOKEN

    prior = [t for t in load_turns(log_path) if t.get("session_id") == session]
    cumulative_resend = sum(int(t.get("resend_tokens", 0)) for t in prior)

    entry: Dict[str, Any] = {
        "ts": round(time.time(), 3),
        "session_id": session,
        "risk_level": risk_level,
        "turn_index": len(prior) + 1,
        "tool_calls": tool_calls,
        "context_base_tokens": context_base,
        "tool_output_tokens": tool_chars // CHARS_PER_TOKEN,
        "response_tokens": response_chars // CHARS_PER_TOKEN,
        "resend_tokens": context_base + history_tokens,
        "cumulative_resend": cumulative_resend + context_base + history_tokens,
        "turn_budget": TURN_BUDGET.get(risk_level),
    }

    path = log_path or turn_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def summarize(session_id: Optional[str] = None, log_path: Optional[Path] = None) -> Dict[str, Any]:
    """Consolida a sessão: o que custou mais e quanto foi reenvio acumulado."""
    turns = load_turns(log_path)
    if session_id:
        turns = [t for t in turns if t.get("session_id") == session_id]
    if not turns:
        return {
            "turns": 0,
            "tool_calls": 0,
            "tool_output_tokens": 0,
            "response_tokens": 0,
            "resend_tokens": 0,
            "context_base_tokens": 0,
            "total_tokens": 0,
            "resend_share_pct": 0.0,
        }

    tool_tokens = sum(int(t.get("tool_output_tokens", 0)) for t in turns)
    response_tokens = sum(int(t.get("response_tokens", 0)) for t in turns)
    resend = sum(int(t.get("resend_tokens", 0)) for t in turns)
    total = tool_tokens + response_tokens + resend

    return {
        "turns": len(turns),
        "tool_calls": sum(int(t.get("tool_calls", 0)) for t in turns),
        "tool_output_tokens": tool_tokens,
        "response_tokens": response_tokens,
        "resend_tokens": resend,
        "context_base_tokens": int(turns[-1].get("context_base_tokens", 0)),
        "total_tokens": total,
        "resend_share_pct": round(resend * 100 / total, 1) if total else 0.0,
        "turn_budget": turns[-1].get("turn_budget"),
        "risk_level": turns[-1].get("risk_level"),
    }


def preflight(context_window: int = 1_000_000, session_id: Optional[str] = None,
              log_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Pre-Flight Gate portátil: usa a estimativa local quando não há cota oficial.
    Dispara alerta acima de PREFLIGHT_CONTEXT_PCT do contexto ou quando o
    orçamento de turnos do nível de risco é excedido.
    """
    stats = summarize(session_id, log_path)
    used_pct = round(stats["resend_tokens"] * 100 / context_window, 2) if context_window else 0.0
    budget = stats.get("turn_budget")
    over_budget = bool(budget) and stats["tool_calls"] > int(budget)

    alerts: List[str] = []
    if used_pct > PREFLIGHT_CONTEXT_PCT:
        alerts.append(
            f"Contexto em {used_pct}% (> {PREFLIGHT_CONTEXT_PCT}%): fechar checkpoint e abrir sessão limpa."
        )
    if over_budget:
        alerts.append(
            f"Orçamento de turnos de {stats.get('risk_level')} excedido "
            f"({stats['tool_calls']} chamadas > {budget})."
        )
    if stats["resend_share_pct"] > RESEND_SHARE_ALERT_PCT and stats["turns"] >= MIN_TURNS_FOR_RESEND_ALERT:
        alerts.append(
            f"Reenvio representa {stats['resend_share_pct']}% do consumo: reduzir contexto base "
            f"(AGENTS.md/memória/skills) ou o número de turnos."
        )

    return {
        "status": "CRITICAL" if alerts else "OK",
        "context_used_pct": used_pct,
        "alerts": alerts,
        "quota_threshold_pct": PREFLIGHT_QUOTA_PCT,
        **stats,
    }


def top_offenders(limit: int = 5, log_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Ranking dos turnos mais caros (D4)."""
    turns = load_turns(log_path)
    ranked = sorted(turns, key=lambda t: int(t.get("resend_tokens", 0)), reverse=True)
    return ranked[:limit]


def format_report(session_id: Optional[str] = None, log_path: Optional[Path] = None) -> str:
    stats = summarize(session_id, log_path)
    base = measure_context_base()
    lines = [
        "Telemetria local de turnos (estimada, sem Language Server)",
        f"  Turnos                : {stats['turns']}",
        f"  Chamadas de ferramenta: {stats['tool_calls']}",
        f"  Contexto base / turno : {stats['context_base_tokens']} tokens",
        f"  Output de ferramentas : {stats['tool_output_tokens']} tokens",
        f"  Respostas             : {stats['response_tokens']} tokens",
        f"  Reenvio acumulado     : {stats['resend_tokens']} tokens ({stats['resend_share_pct']}% do total)",
        "  Composição do contexto base:",
    ]
    for key, value in base.items():
        if key != "total":
            lines.append(f"    - {key}: {value} tokens")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Telemetria local de turnos do XP Kit")
    parser.add_argument("--record", action="store_true", help="Registra um turno")
    parser.add_argument("--report", action="store_true", help="Relatório consolidado")
    parser.add_argument("--preflight", action="store_true", help="Pre-Flight Gate local")
    parser.add_argument("--top", type=int, default=0, help="Ranking dos N turnos mais caros")
    parser.add_argument("--risk", default="L1", choices=sorted(TURN_BUDGET))
    parser.add_argument("--tools", type=int, default=0)
    parser.add_argument("--tool-chars", type=int, default=0)
    parser.add_argument("--response-chars", type=int, default=0)
    parser.add_argument("--history-chars", type=int, default=0)
    parser.add_argument("--session", default="default")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    if args.record:
        entry = record_turn(
            risk_level=args.risk,
            tool_calls=args.tools,
            tool_chars=args.tool_chars,
            response_chars=args.response_chars,
            history_chars=args.history_chars,
            session_id=args.session,
        )
        print(json.dumps(entry, ensure_ascii=False, indent=2) if args.json else
              f"turno #{entry['turn_index']} registrado | reenvio: {entry['resend_tokens']} tokens "
              f"| acumulado: {entry['cumulative_resend']} tokens")
        return 0

    if args.preflight:
        result = preflight(session_id=args.session)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Pre-Flight: {result['status']} (contexto {result['context_used_pct']}%)")
            for alert in result["alerts"]:
                print(f"  ⚠️ {alert}")
        return 1 if result["status"] == "CRITICAL" else 0

    if args.top:
        for turn in top_offenders(args.top):
            print(f"  turno #{turn['turn_index']} | {turn['risk_level']} | "
                  f"reenvio {turn['resend_tokens']} | tools {turn['tool_calls']}")
        return 0

    print(format_report(args.session) if not args.json
          else json.dumps(summarize(args.session), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
