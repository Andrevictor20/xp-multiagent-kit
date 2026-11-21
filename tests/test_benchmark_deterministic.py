"""Tests for the updated deterministic XP kit benchmark (Lean v4 + token optimizers)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BENCH_DIR = ROOT_DIR / "benchmark"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(BENCH_DIR))

import aggregate
import overhead
import runner
import scenarios


class TestDeterministicBenchmark(unittest.TestCase):
    def test_d07_and_d08_expect_step4_block(self):
        for sid in ("D07_skip_bypass", "D08_hardcoded_secret"):
            sc = scenarios.BY_ID[sid]
            self.assertEqual(sc.expected_block_step, 4, f"{sid} deve esperar bloqueio no passo 4")

    def test_measure_token_optimizers_reports_compaction_and_repo_map(self):
        res = overhead.measure_token_optimizers(ROOT_DIR)
        self.assertIn("context_compactor", res)
        self.assertIn("smart_tool_optimizer", res)
        self.assertIn("repo_map", res)
        self.assertIn("context_base_lean", res)

        comp = res["context_compactor"]
        self.assertGreater(comp["raw_bytes"], comp["compacted_bytes"])
        self.assertGreater(comp["reduction_pct"], 0.0)

        rmap = res["repo_map"]
        self.assertGreater(rmap["map_bytes"], 0)
        self.assertGreater(rmap["full_tree_bytes"], rmap["map_bytes"])
        self.assertGreater(rmap["reduction_pct"], 0.0)

        sto = res["smart_tool_optimizer"]
        self.assertGreaterEqual(sto["verbose_rewrites"], 1)
        self.assertTrue(sto["reread_blocked"])
        self.assertTrue(sto["loop_blocked"])

        base_lean = res["context_base_lean"]
        self.assertLessEqual(base_lean["fixed_bytes"], 8000)

    def test_build_report_includes_token_optimizers_section(self):
        fake_records = [
            {
                "scenario": "D01_todo_stub",
                "kind": "defect",
                "risk": "L1",
                "oracle": "todo_marker",
                "oracle_defective": True,
                "arm": "baseline",
                "verdict": "pass",
                "blocked_step": None,
                "duration_s": 0.2,
                "files_bytes": 400,
                "process_output_bytes": 100,
                "governance_bytes": 0,
                "ceremony_bytes": 0,
                "human_steps": 0,
                "commands": 2,
            },
            {
                "scenario": "D01_todo_stub",
                "kind": "defect",
                "risk": "L1",
                "oracle": "todo_marker",
                "oracle_defective": True,
                "arm": "kit",
                "verdict": "blocked",
                "blocked_step": 4,
                "duration_s": 0.6,
                "files_bytes": 400,
                "process_output_bytes": 200,
                "governance_bytes": 4000,
                "ceremony_bytes": 800,
                "human_steps": 0,
                "commands": 4,
            },
            {
                "scenario": "B01_docs_typo",
                "kind": "benign",
                "risk": "L0",
                "oracle": "clean",
                "oracle_defective": False,
                "arm": "baseline",
                "verdict": "pass",
                "blocked_step": None,
                "duration_s": 0.2,
                "files_bytes": 200,
                "process_output_bytes": 80,
                "governance_bytes": 0,
                "ceremony_bytes": 0,
                "human_steps": 0,
                "commands": 2,
            },
            {
                "scenario": "B01_docs_typo",
                "kind": "benign",
                "risk": "L0",
                "oracle": "clean",
                "oracle_defective": False,
                "arm": "kit",
                "verdict": "pass",
                "blocked_step": None,
                "duration_s": 0.5,
                "files_bytes": 200,
                "process_output_bytes": 120,
                "governance_bytes": 4000,
                "ceremony_bytes": 600,
                "human_steps": 0,
                "commands": 3,
            },
        ]
        fake_over = {
            "governance": {
                "agents_md_bytes": 1900,
                "memory_bytes": 2200,
                "policies_index_bytes": 1000,
                "policies_full_bytes": 9200,
                "fixed_context_bytes": 5100,
                "approx_tokens": 1275,
            },
            "hook": {
                "median_ms": 60.0,
                "p95_ms": 80.0,
                "projected_ms_per_50_calls": 3000.0,
                "benign_allowed": 40,
                "benign_total": 40,
                "dangerous_blocked": 8,
                "dangerous_total": 8,
            },
            "jit": {
                "corpus_bytes": 14000,
                "median_bytes": 1400.0,
                "reduction_pct": 90.0,
                "samples": [{"query": "q1", "ms": 80}],
            },
            "gate_kit": {"median_s": 0.25},
            "suite_baseline": {"median_s": 0.1},
            "token_optimizers": {
                "context_compactor": {"raw_bytes": 10000, "compacted_bytes": 2000, "reduction_pct": 80.0},
                "repo_map": {"full_tree_bytes": 8000, "map_bytes": 1200, "reduction_pct": 85.0},
                "smart_tool_optimizer": {"verbose_rewrites": 3, "reread_blocked": True, "loop_blocked": True},
                "context_base_lean": {"fixed_bytes": 5100, "approx_tokens": 1275},
            },
        }
        md = aggregate.build_report(fake_records, fake_over)
        self.assertIn("Otimizadores de Token", md)
        self.assertIn("80.0%", md)
        self.assertIn("85.0%", md)


if __name__ == "__main__":
    unittest.main()
