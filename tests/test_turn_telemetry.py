import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.kit_constants import CHARS_PER_TOKEN, TURN_BUDGET
from scripts.turn_telemetry import (
    estimate_tokens,
    load_turns,
    measure_context_base,
    preflight,
    record_turn,
    summarize,
    top_offenders,
)


class TestTurnTelemetry(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.log = self.root / "turn_log.jsonl"
        (self.root / ".agents" / "memory").mkdir(parents=True)
        (self.root / "AGENTS.md").write_text("regra " * 200, encoding="utf-8")
        (self.root / ".agents" / "memory" / "PROJECT_MEMORY.md").write_text(
            "memória " * 100, encoding="utf-8"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_estimate_tokens_is_deterministic(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("a" * 400), 400 // CHARS_PER_TOKEN)

    def test_context_base_measures_rules_and_memory(self):
        base = measure_context_base(self.root)
        self.assertIn("AGENTS.md", base)
        self.assertIn(".agents/memory/PROJECT_MEMORY.md", base)
        self.assertEqual(base["total"], base["AGENTS.md"] + base[".agents/memory/PROJECT_MEMORY.md"])

    def test_record_turn_computes_resend_and_cumulative(self):
        first = record_turn(risk_level="L1", tool_calls=2, tool_chars=4000,
                            history_chars=8000, session_id="s1",
                            log_path=self.log, root=self.root)
        second = record_turn(risk_level="L1", tool_calls=1, tool_chars=1000,
                             history_chars=12000, session_id="s1",
                             log_path=self.log, root=self.root)

        expected_resend = first["context_base_tokens"] + 8000 // CHARS_PER_TOKEN
        self.assertEqual(first["resend_tokens"], expected_resend)
        self.assertEqual(first["turn_index"], 1)
        self.assertEqual(second["turn_index"], 2)
        self.assertEqual(second["cumulative_resend"], first["resend_tokens"] + second["resend_tokens"])
        self.assertEqual(second["turn_budget"], TURN_BUDGET["L1"])

    def test_log_is_jsonl_and_reloadable(self):
        record_turn(session_id="s2", log_path=self.log, root=self.root)
        turns = load_turns(self.log)
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0]["session_id"], "s2")

    def test_summarize_exposes_resend_share(self):
        for i in range(3):
            record_turn(risk_level="L0", tool_calls=1, tool_chars=500,
                        response_chars=500, session_id="s3",
                        log_path=self.log, root=self.root)
        stats = summarize("s3", self.log)
        self.assertEqual(stats["turns"], 3)
        self.assertGreater(stats["resend_share_pct"], 50.0)
        self.assertEqual(stats["total_tokens"],
                         stats["resend_tokens"] + stats["tool_output_tokens"] + stats["response_tokens"])

    def test_preflight_alerts_on_turn_budget_overflow(self):
        for _ in range(TURN_BUDGET["L0"] + 1):
            record_turn(risk_level="L0", tool_calls=1, session_id="s4",
                        log_path=self.log, root=self.root)
        result = preflight(session_id="s4", log_path=self.log)
        self.assertEqual(result["status"], "CRITICAL")
        self.assertTrue(any("Orçamento de turnos" in a for a in result["alerts"]))

    def test_preflight_ok_within_budget(self):
        record_turn(risk_level="L2", tool_calls=1, session_id="s5",
                    log_path=self.log, root=self.root)
        result = preflight(session_id="s5", log_path=self.log)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["alerts"], [])

    def test_top_offenders_ranks_by_resend(self):
        record_turn(tool_calls=1, history_chars=1000, session_id="s6",
                    log_path=self.log, root=self.root)
        record_turn(tool_calls=1, history_chars=40000, session_id="s6",
                    log_path=self.log, root=self.root)
        ranked = top_offenders(2, self.log)
        self.assertEqual(len(ranked), 2)
        self.assertGreater(ranked[0]["resend_tokens"], ranked[1]["resend_tokens"])

    def test_corrupted_log_lines_are_skipped(self):
        self.log.write_text('{"turn_index": 1, "resend_tokens": 10}\nnot-json\n', encoding="utf-8")
        self.assertEqual(len(load_turns(self.log)), 1)


if __name__ == "__main__":
    unittest.main()
