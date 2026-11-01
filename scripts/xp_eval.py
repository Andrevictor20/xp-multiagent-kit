#!/usr/bin/env python3
"""scripts/xp_eval.py — Motor de benchmark e comparação estatística (AC-12)
Implementa `xp kit eval compare <file_a.jsonl> <file_b.jsonl>`.
Limite estrito: <= 250 linhas.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_eval_file(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.is_file():
        raise FileNotFoundError(f"Arquivo de benchmark não encontrado: {file_path}")
    records: List[Dict[str, Any]] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            records.append(json.loads(line))
        except Exception as e:
            continue
    return records


def calculate_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    if total == 0:
        return {
            "total_tasks": 0,
            "passed_tasks": 0,
            "total_tokens": 0,
            "tokens_per_pass": 0.0,
            "first_gate_pass_rate": 0.0,
            "repeat_failure_rate": 0.0,
            "human_interventions_per_task": 0.0,
            "unverified_l1_plus_sessions": 0,
            "avg_turns": 0.0,
            "avg_duration_seconds": 0.0,
        }

    passed = 0
    total_tokens = 0
    first_gate_passes = 0
    repeat_failures = 0
    total_human = 0
    unverified_l1 = 0
    total_turns = 0
    total_duration = 0.0

    for r in records:
        is_pass = bool(r.get("gate_pass", False))
        if is_pass:
            passed += 1
        total_tokens += int(r.get("total_tokens", 0))
        if r.get("first_gate_pass", is_pass):
            first_gate_passes += 1
        if int(r.get("repeat_failures", 0)) > 0:
            repeat_failures += 1
        total_human += int(r.get("human_interventions", 0))
        risk = str(r.get("risk", "L1")).upper()
        if risk in ("L1", "L2", "L3") and not r.get("gate_verdict_present", is_pass):
            unverified_l1 += 1
        total_turns += int(r.get("turns", 1))
        total_duration += float(r.get("duration_seconds", 0.0))

    tokens_per_pass = (total_tokens / passed) if passed > 0 else float("inf")

    return {
        "total_tasks": total,
        "passed_tasks": passed,
        "total_tokens": total_tokens,
        "tokens_per_pass": round(tokens_per_pass, 2),
        "first_gate_pass_rate": round(first_gate_passes / total, 4),
        "repeat_failure_rate": round(repeat_failures / total, 4),
        "human_interventions_per_task": round(total_human / total, 2),
        "unverified_l1_plus_sessions": unverified_l1,
        "avg_turns": round(total_turns / total, 2),
        "avg_duration_seconds": round(total_duration / total, 2),
    }


def compare_metrics(m_a: Dict[str, Any], m_b: Dict[str, Any]) -> Dict[str, Any]:
    def pct_diff(val_a: float, val_b: float) -> Optional[float]:
        if val_a == 0:
            return 0.0 if val_b == 0 else 100.0
        return round(((val_b - val_a) / val_a) * 100.0, 1)

    return {
        "tokens_per_pass": {
            "a": m_a["tokens_per_pass"],
            "b": m_b["tokens_per_pass"],
            "diff_pct": pct_diff(m_a["tokens_per_pass"], m_b["tokens_per_pass"]),
        },
        "first_gate_pass_rate": {
            "a": m_a["first_gate_pass_rate"],
            "b": m_b["first_gate_pass_rate"],
            "diff_pct": pct_diff(m_a["first_gate_pass_rate"], m_b["first_gate_pass_rate"]),
        },
        "repeat_failure_rate": {
            "a": m_a["repeat_failure_rate"],
            "b": m_b["repeat_failure_rate"],
            "diff_pct": pct_diff(m_a["repeat_failure_rate"], m_b["repeat_failure_rate"]),
        },
        "human_interventions_per_task": {
            "a": m_a["human_interventions_per_task"],
            "b": m_b["human_interventions_per_task"],
            "diff_pct": pct_diff(m_a["human_interventions_per_task"], m_b["human_interventions_per_task"]),
        },
        "unverified_l1_plus_sessions": {
            "a": m_a["unverified_l1_plus_sessions"],
            "b": m_b["unverified_l1_plus_sessions"],
            "diff_abs": m_b["unverified_l1_plus_sessions"] - m_a["unverified_l1_plus_sessions"],
        },
        "avg_turns": {
            "a": m_a["avg_turns"],
            "b": m_b["avg_turns"],
            "diff_pct": pct_diff(m_a["avg_turns"], m_b["avg_turns"]),
        },
        "avg_duration_seconds": {
            "a": m_a["avg_duration_seconds"],
            "b": m_b["avg_duration_seconds"],
            "diff_pct": pct_diff(m_a["avg_duration_seconds"], m_b["avg_duration_seconds"]),
        },
    }


def format_table(comp: Dict[str, Any], label_a: str, label_b: str) -> str:
    lines = [
        "═══════════════════════════════════════════════════════════════════════════════",
        "📊 XP KIT EVALUATION & BENCHMARK COMPARISON (AC-12)",
        "═══════════════════════════════════════════════════════════════════════════════",
        f"{'Métrica':<35} | {label_a:<15} | {label_b:<15} | {'Variação':<12}",
        "────────────────────────────────────┼─────────────────┼─────────────────┼─────────────",
    ]

    t_pass = comp["tokens_per_pass"]
    lines.append(f"{'Tokens / Tarefa PASS (Principal)':<35} | {t_pass['a']:<15} | {t_pass['b']:<15} | {str(t_pass['diff_pct'])+'%':<12}")
    lines.append("────────────────────────────────────┼─────────────────┼─────────────────┼─────────────")

    fg = comp["first_gate_pass_rate"]
    fg_a = f"{fg['a']*100:.1f}%"
    fg_b = f"{fg['b']*100:.1f}%"
    lines.append(f"{'Taxa PASS 1º Gate':<35} | {fg_a:<15} | {fg_b:<15} | {str(fg['diff_pct'])+'%':<12}")

    rf = comp["repeat_failure_rate"]
    rf_a = f"{rf['a']*100:.1f}%"
    rf_b = f"{rf['b']*100:.1f}%"
    lines.append(f"{'Taxa Falhas Repetidas':<35} | {rf_a:<15} | {rf_b:<15} | {str(rf['diff_pct'])+'%':<12}")

    hi = comp["human_interventions_per_task"]
    hi_a = str(hi['a'])
    hi_b = str(hi['b'])
    lines.append(f"{'Intervenções Humanas / Tarefa':<35} | {hi_a:<15} | {hi_b:<15} | {str(hi['diff_pct'])+'%':<12}")

    un = comp["unverified_l1_plus_sessions"]
    un_a = str(un['a'])
    un_b = str(un['b'])
    diff_abs_str = f"abs: {un['diff_abs']}"
    lines.append(f"{'Sessões L1+ Sem Veredito (Risco)':<35} | {un_a:<15} | {un_b:<15} | {diff_abs_str:<12}")

    at = comp["avg_turns"]
    at_a = str(at['a'])
    at_b = str(at['b'])
    lines.append(f"{'Média de Turnos':<35} | {at_a:<15} | {at_b:<15} | {str(at['diff_pct'])+'%':<12}")

    ad = comp["avg_duration_seconds"]
    ad_a = f"{ad['a']}s"
    ad_b = f"{ad['b']}s"
    lines.append(f"{'Duração Média (s)':<35} | {ad_a:<15} | {ad_b:<15} | {str(ad['diff_pct'])+'%':<12}")

    lines.append("═══════════════════════════════════════════════════════════════════════════════")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Kit Eval & Benchmark Comparator (AC-12)")
    sub = parser.add_subparsers(dest="subcommand")

    p_comp = sub.add_parser("compare", help="Compara dois arquivos de execução em formato JSONL")
    p_comp.add_argument("file_a", help="Arquivo JSONL do baseline (A)")
    p_comp.add_argument("file_b", help="Arquivo JSONL da versão avaliada (B)")
    p_comp.add_argument("--json", action="store_true", help="Saída em formato JSON estruturado")

    args = parser.parse_args()
    if args.subcommand != "compare":
        parser.print_help()
        return 1

    try:
        rec_a = parse_eval_file(Path(args.file_a))
        rec_b = parse_eval_file(Path(args.file_b))
    except Exception as e:
        print(f"Erro ao ler arquivos de benchmark: {e}", file=sys.stderr)
        return 1

    m_a = calculate_metrics(rec_a)
    m_b = calculate_metrics(rec_b)
    comp = compare_metrics(m_a, m_b)

    if args.json:
        print(json.dumps({"baseline": m_a, "target": m_b, "comparison": comp}, indent=2))
    else:
        print(format_table(comp, Path(args.file_a).name, Path(args.file_b).name))

    return 0


if __name__ == "__main__":
    sys.exit(main())
