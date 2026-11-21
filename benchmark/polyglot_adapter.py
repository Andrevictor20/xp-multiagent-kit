"""benchmark/polyglot_adapter.py — Adaptador para o formato Polyglot (Aider).

O benchmark do kit é determinístico (sem LLM no loop). Para não ser
"inventado", este adaptador exporta os resultados no formato do
benchmark Aider Polyglot (exercício + hidden tests + pytest como juiz)
e de SWE-bench (predictions.jsonl). Assim, o ganho/escape de defeito
do kit é comparável com qualquer harness de agente que publique no
mesmo formato.

Formato:
  polyglot_tasks.jsonl  — uma linha por cenário (16 no total):
    {
      "id": "D01_todo_stub",
      "language": "python",
      "kind": "defect" | "benign",
      "risk": "L1",
      "prompt": "...",
      "repo_setup": ["<arquivos>"],   # estado do repositório em cada arm
      "hidden_tests": ["tests/test_X.py"],
      "test_command": "python3 -m unittest discover -s tests -q",
      "defect_expected": true,
      "oracle": "todo_marker"
    }

  polyglot_predictions.jsonl — uma linha por (cenário × arm):
    {
      "task_id": "D01_todo_stub",
      "arm": "kit",
      "model": "deterministic_harness",
      "patch": "<git diff>",
      "resolved": false,
      "verdict": "blocked",
      "block_step": 4,
      "oracle_defect": true,
      "escape": false,
      "tokens_proxy": 1830
    }

Uso:
  python3 benchmark/aggregate.py --export-polyglot
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List

BENCH = Path(__file__).resolve().parent
RESULTS = BENCH / "results"


def load_raw() -> List[Dict[str, object]]:
    path = RESULTS / "raw.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def capture_patch(repo: Path) -> str:
    """`git diff HEAD` do sandbox após a execução do arm."""
    res = subprocess.run(
        ["git", "diff", "HEAD", "--unified=3"],
        cwd=str(repo), capture_output=True, text=True,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(repo), capture_output=True, text=True,
    )
    return res.stdout + ("\n# untracked files:\n" + untracked.stdout if untracked.stdout.strip() else "")


def export_polyglot() -> Dict[str, object]:
    """Gera `polyglot_tasks.jsonl` + `polyglot_predictions.jsonl`."""
    import scenarios as scen
    raw = load_raw()

    tasks_lines = []
    for scenario in scen.SCENARIOS:
        tasks_lines.append(json.dumps({
            "id": scenario.sid,
            "language": "python",
            "kind": scenario.kind,
            "risk": scenario.risk,
            "prompt": scenario.goal,
            "repo_setup": sorted(list(scenario.red.keys()) + list(scenario.green.keys())),
            "hidden_tests": sorted({k for m in (scenario.red, scenario.green) for k in m if k.startswith("tests/")}),
            "test_command": "python3 -m unittest discover -s tests -q",
            "defect_expected": scenario.kind == "defect",
            "oracle": scenario.oracle,
            "expected_block_step": scenario.expected_block_step,
        }, ensure_ascii=False))
    tasks_path = RESULTS / "polyglot_tasks.jsonl"
    tasks_path.write_text("\n".join(tasks_lines) + "\n", encoding="utf-8")

    pred_lines = []
    for rec in raw:
        scenario = scen.BY_ID[str(rec["scenario"])]
        is_defect = bool(rec.get("oracle_defective", False))
        escaped = is_defect and rec["verdict"] == "pass"
        tokens = 0
        for key in ("files_bytes", "process_output_bytes", "governance_bytes", "ceremony_bytes"):
            tokens += int(rec.get(key, 0))
        pred_lines.append(json.dumps({
            "task_id": scenario.sid,
            "arm": rec["arm"],
            "model": "deterministic_harness_v4",
            "verdict": rec["verdict"],
            "resolved": rec["verdict"] == "pass",
            "block_step": rec["blocked_step"],
            "oracle_defect": is_defect,
            "escape": escaped,
            "risk": scenario.risk,
            "duration_s": rec["duration_s"],
            "human_steps": rec["human_steps"],
            "commands": rec["commands"],
            "tokens_proxy": tokens // 4,
        }, ensure_ascii=False))
    pred_path = RESULTS / "polyglot_predictions.jsonl"
    pred_path.write_text("\n".join(pred_lines) + "\n", encoding="utf-8")

    return {"tasks": str(tasks_path), "predictions": str(pred_path),
            "task_count": len(tasks_lines), "prediction_count": len(pred_lines)}


def summarize(predictions: List[Dict[str, object]]) -> Dict[str, object]:
    """Score Polyglot-style: pass rate por arm, escape de defeito, tempo."""
    out: Dict[str, object] = {}
    for arm in ("baseline", "kit"):
        arm_preds = [p for p in predictions if p["arm"] == arm]
        if not arm_preds:
            continue
        total = len(arm_preds)
        defects = [p for p in arm_preds if p.get("oracle_defect")]
        benign = [p for p in arm_preds if not p.get("oracle_defect")]
        tp = sum(1 for p in defects if p["verdict"] == "blocked")
        fp = sum(1 for p in benign if p["verdict"] == "blocked")
        out[arm] = {
            "total": total,
            "defects_observed": len(defects),
            "defects_caught": tp,
            "recall_pct": round(100 * tp / len(defects), 1) if defects else 0.0,
            "false_positives": fp,
            "fpr_pct": round(100 * fp / len(benign), 1) if benign else 0.0,
            "avg_tokens_proxy": round(sum(int(p["tokens_proxy"]) for p in arm_preds) / total),
            "avg_duration_s": round(sum(float(p["duration_s"]) for p in arm_preds) / total, 3),
            "total_human_steps": sum(int(p["human_steps"]) for p in arm_preds),
        }
    return out


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="XP kit → Polyglot/SWE-bench adapter")
    sub = parser.add_subparsers(dest="action")
    sub.add_parser("export")
    sub.add_parser("score")
    args = parser.parse_args()

    if args.action == "export" or args.action is None:
        res = export_polyglot()
        print(json.dumps(res, indent=2, ensure_ascii=False))
    if args.action == "score":
        preds = [json.loads(l) for l in (RESULTS / "polyglot_predictions.jsonl").read_text().splitlines() if l.strip()]
        summary = summarize(preds)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
