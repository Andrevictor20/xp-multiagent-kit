#!/usr/bin/env python3
"""tests/test_xp_gate.py — Testes unitários para scripts/xp_gate.py (AC-3)"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.xp_contract import init_contract
from scripts.xp_gate import (
    run_gate,
    build_receipt,
    format_failure_block,
)


class TestXpGate(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_env = os.environ.get("KIT_RUNTIME_DIR")
        os.environ["KIT_RUNTIME_DIR"] = self.test_dir

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["KIT_RUNTIME_DIR"] = self.orig_env
        else:
            os.environ.pop("KIT_RUNTIME_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_gate_pass_minimal_l0(self):
        init_contract(risk="L0", goal="Fix typo in doc", scope_files=["README.md"])
        code, line, failure = run_gate(dry_run=True, changed_files=["README.md"])
        self.assertEqual(code, 0)
        self.assertIn("GATE PASS", line)

    def test_gate_fail_scope_fence(self):
        # Diff touches a file outside scope_files
        init_contract(risk="L1", goal="Fix parser", scope_files=["scripts/parser.py"])
        code, line, failure = run_gate(
            dry_run=True, changed_files=["scripts/parser.py", "scripts/other.py"]
        )
        self.assertEqual(code, 1)
        self.assertIn("GATE FAIL", line)
        self.assertIn("scope_files", failure)

    def test_gate_fail_stubs_or_god_files(self):
        dummy_file = Path(self.test_dir) / "stub_code.py"
        dummy_file.write_text("# TODO: finish this later\nprint('hello')\n", encoding="utf-8")

        init_contract(risk="L1", goal="Test stub detection", scope_files=[str(dummy_file)])
        code, line, failure = run_gate(dry_run=True, changed_files=[str(dummy_file)])
        self.assertEqual(code, 1)
        self.assertIn("GATE FAIL", line)
        self.assertIn("TODO", failure)

    def test_gate_block_human_tier_without_approval(self):
        # File is a migration, tier becomes human
        init_contract(
            risk="L1",
            goal="Add migration",
            scope_files=["db/migrations/001.sql"],
        )
        code, line, failure = run_gate(
            dry_run=True, changed_files=["db/migrations/001.sql"]
        )
        self.assertEqual(code, 2)  # BLOCK
        self.assertIn("GATE BLOCK", line)
        self.assertTrue("aprovação" in failure.lower() or "approve" in failure.lower())

    def test_gate_receipt_formatting(self):
        init_contract(
            risk="L1",
            goal="Refactor helper",
            acs=["AC-1: Parse"],
            scope_files=["scripts/helper.py"],
        )
        receipt = build_receipt(
            contract={"goal": "Refactor helper", "risk": "L1"},
            changed_files=["scripts/helper.py"],
            tier="auto",
            tests_run=5,
        )
        self.assertIn("OBJETIVO:", receipt)
        self.assertIn("ALTERADO:", receipt)
        self.assertIn("VERIFICADO:", receipt)
        self.assertIn("NÃO VERIFICADO:", receipt)
        self.assertIn("DECISÕES:", receipt)
        self.assertIn("RISCOS:", receipt)
        self.assertIn("APROVAÇÃO NECESSÁRIA:", receipt)
        self.assertLessEqual(len(receipt.splitlines()), 15)

    def test_gate_self_sufficient_hints_for_step1_step7_step9(self):
        # Step 1: no contract -> hint must include exact xp contract init command
        code1, line1, fail1 = run_gate(dry_run=True, changed_files=[])
        self.assertEqual(code1, 1)
        self.assertIn("step=1", line1)
        self.assertIn("--risk", fail1)
        self.assertIn("--verify", fail1)

        # Step 9: untraced AC -> hint must explain AC-01 / test_ac_01 format explicitly
        untraced_ac = "AC-" + "9876"
        init_contract(
            risk="L1",
            goal="Export CSV",
            acs=[untraced_ac],
            scope_files=["README.md"],
            verify_cmd="python3 -m unittest discover -s tests -q",
        )
        code9, line9, fail9 = run_gate(dry_run=True, changed_files=["README.md"])
        self.assertEqual(code9, 1)
        self.assertIn("step=9", line9)
        self.assertIn("test_ac_", fail9)
        self.assertIn(untraced_ac, fail9)


if __name__ == "__main__":
    unittest.main()
