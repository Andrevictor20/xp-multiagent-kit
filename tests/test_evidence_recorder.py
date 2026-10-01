import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts import evidence_recorder


class TestEvidenceRecorder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self._previous = os.environ.get("KIT_RUNTIME_DIR")
        os.environ["KIT_RUNTIME_DIR"] = self.temp_dir.name

    def tearDown(self):
        if self._previous is None:
            os.environ.pop("KIT_RUNTIME_DIR", None)
        else:
            os.environ["KIT_RUNTIME_DIR"] = self._previous
        self.temp_dir.cleanup()

    def test_parses_pytest_summary(self):
        counts = evidence_recorder.parse_test_summary("==== 12 passed, 2 failed in 3.1s ====")
        self.assertEqual(counts, {"total": 14, "passed": 12, "failed": 2})

    def test_parses_unittest_summary(self):
        counts = evidence_recorder.parse_test_summary("Ran 48 tests in 0.480s\n\nOK\n")
        self.assertEqual(counts, {"total": 48, "passed": 48, "failed": 0})

    def test_record_stores_log_outside_context_and_index(self):
        entry = evidence_recorder.record(
            "pytest tests/test_x.py", 0, output="Ran 3 tests in 0.1s\n\nOK\n"
        )
        self.assertEqual(entry["status"], "PASS")
        self.assertEqual(entry["tests"]["passed"], 3)
        self.assertTrue(Path(entry["log_path"]).is_file())
        self.assertIn("OK", Path(entry["log_path"]).read_text(encoding="utf-8"))

    def test_failing_command_is_marked_fail(self):
        entry = evidence_recorder.record("pytest", 1, output="1 failed, 2 passed")
        self.assertEqual(entry["status"], "FAIL")

    def test_render_markdown_has_no_raw_log(self):
        evidence_recorder.record("pytest tests/a.py", 0, output="Ran 2 tests\n\nOK\n")
        rendered = evidence_recorder.render_markdown()
        self.assertIn("| 1 |", rendered)
        self.assertIn("PASS", rendered)
        self.assertIn(".log", rendered)
        self.assertNotIn("Ran 2 tests", rendered)

    def test_empty_evidence_renders_placeholder(self):
        self.assertIn("Nenhuma evidência", evidence_recorder.render_markdown([]))

    def test_index_is_append_only_jsonl(self):
        evidence_recorder.record("cmd1", 0, output="OK")
        evidence_recorder.record("cmd2", 0, output="OK")
        entries = evidence_recorder.load_entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual([e["command"] for e in entries], ["cmd1", "cmd2"])


if __name__ == "__main__":
    unittest.main()
