"""Tests for the LLM-in-the-loop A/B benchmark suite."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BENCH_DIR = ROOT_DIR / "benchmark"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(BENCH_DIR))

import llm_adapters
import llm_aggregate
import llm_runner
import llm_tasks
from scripts.xp_eval import calculate_metrics, parse_eval_file


class TestLLMAdapters(unittest.TestCase):
    def test_parse_claude_style_json(self):
        payload = json.dumps({
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "duration_ms": 4200,
            "num_turns": 3,
            "result": "Done",
            "total_cost_usd": 0.0125,
            "usage": {
                "input_tokens": 1200,
                "cache_creation_input_tokens": 300,
                "cache_read_input_tokens": 800,
                "output_tokens": 250,
            },
        })
        parsed = llm_adapters.parse_runner_output("claude", payload, exit_code=0, elapsed_s=4.2)
        self.assertEqual(parsed.input_tokens, 1200)
        self.assertEqual(parsed.cache_creation_tokens, 300)
        self.assertEqual(parsed.cache_read_tokens, 800)
        self.assertEqual(parsed.output_tokens, 250)
        self.assertEqual(parsed.total_tokens, 2550)
        self.assertEqual(parsed.turns, 3)
        self.assertAlmostEqual(parsed.cost_usd, 0.0125)

    def test_parse_agy_ndjson_or_json(self):
        ndjson = "\n".join([
            json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "view_file"}]}}),
            json.dumps({
                "type": "result",
                "num_turns": 2,
                "total_cost_usd": 0.004,
                "usage": {"input_tokens": 900, "output_tokens": 150, "cache_read_input_tokens": 400},
            }),
        ])
        parsed = llm_adapters.parse_runner_output("agy", ndjson, exit_code=0, elapsed_s=2.1)
        self.assertEqual(parsed.input_tokens, 900)
        self.assertEqual(parsed.output_tokens, 150)
        self.assertEqual(parsed.cache_read_tokens, 400)
        self.assertEqual(parsed.total_tokens, 1450)
        self.assertEqual(parsed.turns, 2)
        self.assertEqual(parsed.tool_calls, 1)

    def test_parse_codex_jsonl(self):
        jsonl = "\n".join([
            json.dumps({"type": "thread.started", "thread_id": "t1"}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution"}}),
            json.dumps({"type": "item.completed", "item": {"type": "file_change"}}),
            json.dumps({
                "type": "turn.completed",
                "usage": {"input_tokens": 1000, "cached_input_tokens": 600, "output_tokens": 180},
            }),
        ])
        parsed = llm_adapters.parse_runner_output("codex", jsonl, exit_code=0, elapsed_s=3.0)
        self.assertEqual(parsed.input_tokens, 1000)
        self.assertEqual(parsed.cache_read_tokens, 600)
        self.assertEqual(parsed.output_tokens, 180)
        self.assertEqual(parsed.total_tokens, 1180)
        self.assertEqual(parsed.tool_calls, 2)
        self.assertEqual(parsed.turns, 1)

    def test_parse_gemini_stats_json(self):
        payload = json.dumps({
            "response": "OK",
            "stats": {
                "models": {
                    "gemini-2.5-pro": {
                        "api": {"totalRequests": 2},
                        "tokens": {"input": 500, "candidates": 100, "cached": 200, "thoughts": 50, "total": 650},
                    }
                }
            },
        })
        parsed = llm_adapters.parse_runner_output("gemini", payload, exit_code=0, elapsed_s=1.5)
        self.assertEqual(parsed.input_tokens, 500)
        self.assertEqual(parsed.output_tokens, 150)
        self.assertEqual(parsed.cache_read_tokens, 200)
        self.assertEqual(parsed.total_tokens, 650)
        self.assertEqual(parsed.turns, 2)

    def test_build_command_uses_non_interactive_flags(self):
        cmd_agy = llm_adapters.build_command("agy", "Fix bug", model="gemini-3.8-flash-low", effort="low")
        self.assertTrue(any("agy" in part for part in cmd_agy[:2]))
        self.assertIn("--output-format", cmd_agy)
        self.assertTrue(any(part.startswith("--print=") for part in cmd_agy))

        cmd_claude = llm_adapters.build_command("claude", "Fix bug")
        self.assertIn("-p", cmd_claude)
        self.assertIn("--output-format", cmd_claude)

        cmd_codex = llm_adapters.build_command("codex", "Fix bug")
        self.assertEqual(Path(cmd_codex[0]).name, "codex")
        self.assertEqual(cmd_codex[1], "exec")
        self.assertIn("--json", cmd_codex)


class TestLLMTasksAndRunner(unittest.TestCase):
    def test_tasks_have_identical_prompts_and_hidden_tests(self):
        self.assertGreaterEqual(len(llm_tasks.TASKS), 6)
        for task in llm_tasks.TASKS:
            self.assertTrue(task.tid)
            self.assertIn(task.risk, ("L0", "L1", "L2", "L3"))
            self.assertTrue(task.prompt.strip())
            self.assertTrue(task.hidden_tests)

    def test_sandbox_isolation_baseline_vs_kit(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_repo = llm_runner.prepare_arm_sandbox(Path(tmp) / "base", with_kit=False)
            kit_repo = llm_runner.prepare_arm_sandbox(Path(tmp) / "kit", with_kit=True)
            self.assertFalse((base_repo / "AGENTS.md").exists())
            self.assertFalse((base_repo / ".agents").exists())
            self.assertFalse((base_repo / "scripts").exists())
            self.assertTrue((kit_repo / "AGENTS.md").is_file())
            self.assertTrue((kit_repo / ".agents" / "policies" / "INDEX.md").is_file())
            self.assertTrue((kit_repo / "scripts" / "xp").is_file())

    def test_dry_run_paired_pipeline_and_xp_eval_compat(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "results"
            workdir = Path(tmp) / "work"
            records = llm_runner.run_benchmark(
                task_ids=["T01_l0_docs_typo", "T02_l1_bugfix_tdd"],
                runner_name="agy",
                workdir=workdir,
                out_dir=out_dir,
                dry_run=True,
            )
            self.assertEqual(len(records), 4)
            summary, md = llm_aggregate.aggregate_results(
                raw_path=out_dir / "llm_raw.jsonl",
                out_dir=out_dir,
            )
            self.assertIn("baseline", summary["arms"])
            self.assertIn("kit", summary["arms"])
            self.assertIn("Consumo Real de Tokens", md)

            # Compatível com scripts/xp_eval.py
            m_base = calculate_metrics(parse_eval_file(out_dir / "llm_baseline.jsonl"))
            m_kit = calculate_metrics(parse_eval_file(out_dir / "llm_kit.jsonl"))
            self.assertEqual(m_base["total_tasks"], 2)
            self.assertEqual(m_kit["total_tasks"], 2)


if __name__ == "__main__":
    unittest.main()
