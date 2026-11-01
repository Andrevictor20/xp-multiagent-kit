"""tests/test_xp_eval.py — Testes do motor de avaliação e benchmark (AC-12)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.xp_eval import calculate_metrics, compare_metrics, parse_eval_file


class TestXpEval(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

        # Baseline A (v3.9): higher tokens, more repeat failures, lower 1st gate pass
        self.file_a = self.tmp_path / "baseline_a.jsonl"
        data_a = [
            {"task_id": "t1", "risk": "L0", "gate_pass": True, "first_gate_pass": True, "total_tokens": 15000, "turns": 4, "duration_seconds": 25.0, "human_interventions": 0, "repeat_failures": 0, "gate_verdict_present": True},
            {"task_id": "t2", "risk": "L1", "gate_pass": True, "first_gate_pass": False, "total_tokens": 40000, "turns": 8, "duration_seconds": 60.0, "human_interventions": 1, "repeat_failures": 2, "gate_verdict_present": True},
            {"task_id": "t3", "risk": "L2", "gate_pass": False, "first_gate_pass": False, "total_tokens": 60000, "turns": 12, "duration_seconds": 90.0, "human_interventions": 2, "repeat_failures": 1, "gate_verdict_present": False},
        ]
        self.file_a.write_text("\n".join(json.dumps(d) for d in data_a), encoding="utf-8")

        # Target B (v4.0): fewer tokens, high 1st gate pass, zero repeat failures
        self.file_b = self.tmp_path / "target_b.jsonl"
        data_b = [
            {"task_id": "t1", "risk": "L0", "gate_pass": True, "first_gate_pass": True, "total_tokens": 5000, "turns": 2, "duration_seconds": 10.0, "human_interventions": 0, "repeat_failures": 0, "gate_verdict_present": True},
            {"task_id": "t2", "risk": "L1", "gate_pass": True, "first_gate_pass": True, "total_tokens": 16000, "turns": 4, "duration_seconds": 22.0, "human_interventions": 0, "repeat_failures": 0, "gate_verdict_present": True},
            {"task_id": "t3", "risk": "L2", "gate_pass": True, "first_gate_pass": True, "total_tokens": 24000, "turns": 5, "duration_seconds": 35.0, "human_interventions": 0, "repeat_failures": 0, "gate_verdict_present": True},
        ]
        self.file_b.write_text("\n".join(json.dumps(d) for d in data_b), encoding="utf-8")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_parse_eval_file(self):
        records = parse_eval_file(self.file_a)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["task_id"], "t1")

    def test_calculate_metrics(self):
        metrics_a = calculate_metrics(parse_eval_file(self.file_a))
        self.assertEqual(metrics_a["total_tasks"], 3)
        self.assertEqual(metrics_a["passed_tasks"], 2)
        self.assertEqual(metrics_a["total_tokens"], 115000)
        self.assertEqual(metrics_a["tokens_per_pass"], 57500.0)
        self.assertEqual(metrics_a["unverified_l1_plus_sessions"], 1)

        metrics_b = calculate_metrics(parse_eval_file(self.file_b))
        self.assertEqual(metrics_b["total_tasks"], 3)
        self.assertEqual(metrics_b["passed_tasks"], 3)
        self.assertEqual(metrics_b["total_tokens"], 45000)
        self.assertEqual(metrics_b["tokens_per_pass"], 15000.0)
        self.assertEqual(metrics_b["unverified_l1_plus_sessions"], 0)

    def test_compare_metrics(self):
        m_a = calculate_metrics(parse_eval_file(self.file_a))
        m_b = calculate_metrics(parse_eval_file(self.file_b))
        comp = compare_metrics(m_a, m_b)

        # tokens_per_pass decreased significantly
        self.assertLess(comp["tokens_per_pass"]["diff_pct"], 0)
        self.assertEqual(comp["unverified_l1_plus_sessions"]["diff_abs"], -1)

    def test_cli_xp_kit_eval_compare(self):
        cmd = [sys.executable, str(ROOT_DIR / "scripts" / "xp"), "kit", "eval", "compare", str(self.file_a), str(self.file_b)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Stdout: {res.stdout}, Stderr: {res.stderr}")
        self.assertIn("XP KIT EVALUATION & BENCHMARK COMPARISON", res.stdout)
        self.assertIn("Tokens / Tarefa PASS (Principal)", res.stdout)

    def test_cli_xp_eval_json(self):
        cmd = [sys.executable, str(ROOT_DIR / "scripts" / "xp_eval.py"), "compare", str(self.file_a), str(self.file_b), "--json"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("baseline", data)
        self.assertIn("target", data)
        self.assertIn("comparison", data)


if __name__ == "__main__":
    unittest.main()
