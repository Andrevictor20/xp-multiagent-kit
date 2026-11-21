"""Aggregate LLM-in-the-loop benchmark metrics and generate LLM_RESULTS.md."""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"


def load_llm_records(raw_path: Path | None = None) -> List[Dict[str, Any]]:
    path = raw_path or (RESULTS_DIR / "llm_raw.jsonl")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_arm(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {
            "tasks": 0,
            "resolved": 0,
            "resolve_rate_pct": 0.0,
            "base_suite_ok": 0,
            "defect_escapes": 0,
            "defect_escape_rate_pct": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "thinking_tokens": 0,
            "total_tokens": 0,
            "avg_tokens_per_task": 0,
            "median_tokens_per_task": 0,
            "tokens_per_resolved_task": None,
            "total_cost_usd": 0.0,
            "avg_turns": 0.0,
            "avg_duration_s": 0.0,
            "avg_tool_calls": 0.0,
            "kit_gate_pass": 0,
            "kit_tdd_evidence": 0,
        }

    n = len(records)
    resolved = sum(1 for r in records if r.get("resolved"))
    base_ok = sum(1 for r in records if r.get("base_suite_ok"))
    escapes = sum(1 for r in records if r.get("defect_escaped"))
    inp = sum(int(r.get("input_tokens", 0)) for r in records)
    out = sum(int(r.get("output_tokens", 0)) for r in records)
    cache_read = sum(int(r.get("cache_read_tokens", 0)) for r in records)
    thinking = sum(int(r.get("thinking_tokens", 0)) for r in records)
    tot_list = [int(r.get("total_tokens", 0)) for r in records]
    tot = sum(tot_list)
    cost = round(sum(float(r.get("cost_usd", 0.0)) for r in records), 6)
    gate_pass = sum(1 for r in records if r.get("kit_ceremony", {}).get("gate_pass"))
    tdd_ev = sum(1 for r in records if r.get("kit_ceremony", {}).get("red_green_evidence"))

    return {
        "tasks": n,
        "resolved": resolved,
        "resolve_rate_pct": round(100.0 * resolved / n, 1),
        "base_suite_ok": base_ok,
        "defect_escapes": escapes,
        "defect_escape_rate_pct": round(100.0 * escapes / n, 1),
        "input_tokens": inp,
        "output_tokens": out,
        "cache_read_tokens": cache_read,
        "thinking_tokens": thinking,
        "total_tokens": tot,
        "avg_tokens_per_task": round(tot / n),
        "median_tokens_per_task": round(statistics.median(tot_list)),
        "tokens_per_resolved_task": round(tot / resolved) if resolved else None,
        "total_cost_usd": cost,
        "avg_turns": round(sum(int(r.get("turns", 0)) for r in records) / n, 2),
        "avg_duration_s": round(sum(float(r.get("duration_s", 0.0)) for r in records) / n, 2),
        "avg_tool_calls": round(sum(int(r.get("tool_calls", 0)) for r in records) / n, 2),
        "kit_gate_pass": gate_pass,
        "kit_tdd_evidence": tdd_ev,
    }


def _pct_delta(base_val: float | int | None, kit_val: float | int | None) -> str:
    if base_val is None or kit_val is None or base_val == 0:
        return "—"
    pct = round(100.0 * (float(kit_val) - float(base_val)) / float(base_val), 1)
    return f"{pct:+.1f}%"


def build_llm_markdown(records: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    b = summary["arms"]["baseline"]
    k = summary["arms"]["kit"]
    runner = records[0].get("runner", "?") if records else "?"
    model = next((r.get("model") for r in records if r.get("model")), "padrão")

    lines = [
        "# Benchmark A/B com LLM Real: Sem Kit vs Com XP Multi-Agent Kit v4",
        "",
        f"- **Runner CLI:** `{runner}` | **Modelo:** `{model}` | **Execuções por braço:** {b['tasks']}",
        "",
        "## 1. Resumo Executivo (Ganhos Reais & Consumo Real de Tokens)",
        "",
        "| Métrica | Sem Kit (`baseline`) | Com Kit (`kit`) | Δ |",
        "|---|---:|---:|---:|",
        f"| Tarefas 100% resolvidas (testes ocultos + oráculos) | {b['resolved']}/{b['tasks']} ({b['resolve_rate_pct']}%) | {k['resolved']}/{k['tasks']} ({k['resolve_rate_pct']}%) | {round(k['resolve_rate_pct'] - b['resolve_rate_pct'], 1):+.1f} p.p. |",
        f"| Escape de defeito / violação pós-entrega | {b['defect_escapes']} ({b['defect_escape_rate_pct']}%) | {k['defect_escapes']} ({k['defect_escape_rate_pct']}%) | {round(k['defect_escape_rate_pct'] - b['defect_escape_rate_pct'], 1):+.1f} p.p. |",
        f"| **Tokens totais consumidos** | {b['total_tokens']} | {k['total_tokens']} | {_pct_delta(b['total_tokens'], k['total_tokens'])} |",
        f"| Média de tokens / tarefa | {b['avg_tokens_per_task']} | {k['avg_tokens_per_task']} | {_pct_delta(b['avg_tokens_per_task'], k['avg_tokens_per_task'])} |",
        f"| **Tokens / tarefa resolvida (KPI)** | {b['tokens_per_resolved_task'] or '∞'} | {k['tokens_per_resolved_task'] or '∞'} | {_pct_delta(b['tokens_per_resolved_task'], k['tokens_per_resolved_task'])} |",
        f"| Input tokens | {b['input_tokens']} | {k['input_tokens']} | {_pct_delta(b['input_tokens'], k['input_tokens'])} |",
        f"| Output tokens | {b['output_tokens']} | {k['output_tokens']} | {_pct_delta(b['output_tokens'], k['output_tokens'])} |",
        f"| Cache read tokens | {b['cache_read_tokens']} | {k['cache_read_tokens']} | {_pct_delta(b['cache_read_tokens'], k['cache_read_tokens'])} |",
        f"| Turnos médios / tarefa | {b['avg_turns']} | {k['avg_turns']} | {_pct_delta(b['avg_turns'], k['avg_turns'])} |",
        f"| Duração média / tarefa (s) | {b['avg_duration_s']} s | {k['avg_duration_s']} s | {_pct_delta(b['avg_duration_s'], k['avg_duration_s'])} |",
        f"| Custo USD reportado | ${b['total_cost_usd']:.4f} | ${k['total_cost_usd']:.4f} | {_pct_delta(b['total_cost_usd'], k['total_cost_usd'])} |",
        f"| Gate `xp gate check` PASS (braço kit) | — | {k['kit_gate_pass']}/{k['tasks']} | — |",
        f"| Evidência RED→GREEN registrada (braço kit) | — | {k['kit_tdd_evidence']}/{k['tasks']} | — |",
        "",
        "## 2. Comparação Pareada por Tarefa",
        "",
        "| Tarefa | Risco | Sem Kit (OK / Tokens / Turnos) | Com Kit (OK / Tokens / Turnos) | Δ Tokens | Oráculos violados |",
        "|---|---|---|---|---:|---|",
    ]

    grouped: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for rec in records:
        grouped[str(rec["task"])][str(rec["arm"])] = rec

    for tid, pair in grouped.items():
        base = pair.get("baseline", {})
        kit = pair.get("kit", {})
        b_ok = "PASS" if base.get("resolved") else "FAIL"
        k_ok = "PASS" if kit.get("resolved") else "FAIL"
        b_tok = base.get("total_tokens", 0)
        k_tok = kit.get("total_tokens", 0)
        b_cell = f"{b_ok} / {b_tok} / {base.get('turns', 0)}t"
        k_cell = f"{k_ok} / {k_tok} / {kit.get('turns', 0)}t"
        b_orac = list((base.get("oracle_failures") or {}).keys())
        k_orac = list((kit.get("oracle_failures") or {}).keys())
        orac_str = f"base:{','.join(b_orac) or 'none'} | kit:{','.join(k_orac) or 'none'}"
        lines.append(
            f"| `{tid}` | {base.get('risk') or kit.get('risk', '?')} | {b_cell} | {k_cell} | "
            f"{_pct_delta(b_tok, k_tok)} | {orac_str} |"
        )

    lines.append("")
    return "\n".join(lines)


def aggregate_results(
    raw_path: Path | None = None,
    out_dir: Path | None = None,
) -> Tuple[Dict[str, Any], str]:
    records = load_llm_records(raw_path)
    odir = out_dir or RESULTS_DIR
    odir.mkdir(parents=True, exist_ok=True)
    summary = {
        "arms": {
            "baseline": summarize_arm([r for r in records if r["arm"] == "baseline"]),
            "kit": summarize_arm([r for r in records if r["arm"] == "kit"]),
        }
    }
    md = build_llm_markdown(records, summary)
    (odir / "llm_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (odir / "LLM_RESULTS.md").write_text(md, encoding="utf-8")
    return summary, md


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Aggregate LLM benchmark records")
    parser.add_argument("--raw", default=str(RESULTS_DIR / "llm_raw.jsonl"))
    parser.add_argument("--out-dir", default=str(RESULTS_DIR))
    args = parser.parse_args()
    summary, _ = aggregate_results(Path(args.raw), Path(args.out_dir))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
