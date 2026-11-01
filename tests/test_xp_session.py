#!/usr/bin/env python3
"""tests/test_xp_session.py — Testes unitários para xp_session.py (AC-11)"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.xp_session import compact_session_text, create_handoff_contract, resume_session


class TestXpSession(unittest.TestCase):
    def test_compact_session_text(self) -> None:
        short = "linha 1\nlinha 2\nlinha 3"
        self.assertEqual(compact_session_text(short), short)

        long_text = "\n".join(f"log line {i} with some content" for i in range(100))
        compacted = compact_session_text(long_text, max_chars=200)
        self.assertIn("linhas compactadas", compacted)
        self.assertLess(len(compacted), len(long_text))

    def test_resume_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tfile = Path(tmp) / "transcript.jsonl"
            tfile.write_text(
                json.dumps({"type": "USER_INPUT", "content": "Olá assistente"}) + "\n" +
                json.dumps({"type": "PLANNER_RESPONSE", "content": "Olá!"}) + "\n",
                encoding="utf-8"
            )
            res = resume_session(str(tfile))
            self.assertEqual(res["status"], "RESUMED")
            self.assertEqual(res["steps_count"], 2)
            self.assertIn("Olá assistente", res["latest_prompt"])

    def test_create_handoff_contract(self) -> None:
        contract = create_handoff_contract(
            task_id="task-01",
            risk_level="L2",
            spec_path=".agents/specs/SPEC-001.md",
            tests_status="RED",
            files_touched=["src/app.py"],
        )
        self.assertEqual(contract["task_id"], "task-01")
        self.assertEqual(contract["risk_level"], "L2")
        self.assertEqual(contract["tests"]["status"], "RED")
        self.assertIn("src/app.py", contract["files_touched"])


if __name__ == "__main__":
    unittest.main()
