#!/usr/bin/env python3
"""tests/test_xp_contract.py — Testes unitários para scripts/xp_contract.py (AC-1)"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.xp_contract import (
    init_contract,
    load_contract,
    save_contract,
    record_dead_end,
    add_never,
    get_runtime_contract_path,
)


class TestXpContract(unittest.TestCase):
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

    def test_init_contract_full(self):
        contract = init_contract(
            risk="L1",
            goal="Fix parser error",
            acs=["AC-1: Parse cleanly", "AC-2: Catch malformed"],
            scope_files=["scripts/parser.py", "tests/test_parser.py"],
            constraints=["No external deps", "File < 500 lines"],
            verify_cmd="python3 -m unittest tests/test_parser.py",
            checks=["flake8"],
            refactor=False,
        )
        self.assertEqual(contract["risk"], "L1")
        self.assertEqual(contract["goal"], "Fix parser error")
        self.assertEqual(len(contract["acs"]), 2)
        self.assertEqual(len(contract["scope_files"]), 2)
        self.assertEqual(contract["max_attempts"], 3)
        self.assertFalse(contract["refactor"])
        self.assertEqual(contract["tried"], [])
        self.assertEqual(contract["never"], [])

        # Check file on disk
        contract_path = get_runtime_contract_path()
        self.assertTrue(contract_path.is_file())
        with open(contract_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["goal"], "Fix parser error")

    def test_init_contract_l0_minimal(self):
        contract = init_contract(risk="L0", goal="Fix typo in README")
        self.assertEqual(contract["risk"], "L0")
        self.assertEqual(contract["goal"], "Fix typo in README")
        self.assertEqual(contract["acs"], [])
        self.assertEqual(contract["scope_files"], [])

    def test_record_dead_end_deduplication(self):
        init_contract(risk="L1", goal="Test dead ends")
        record_dead_end(signature="a1b2c3d4e5", reason="AssertionError on line 42")
        contract = load_contract()
        self.assertEqual(len(contract["tried"]), 1)
        self.assertEqual(contract["tried"][0]["signature"], "a1b2c3d4e5")

        # Recording exact same signature should not duplicate
        record_dead_end(signature="a1b2c3d4e5", reason="AssertionError on line 42")
        contract = load_contract()
        self.assertEqual(len(contract["tried"]), 1)

        # Different signature should append
        record_dead_end(signature="f6g7h8i9j0", reason="TimeoutError")
        contract = load_contract()
        self.assertEqual(len(contract["tried"]), 2)

    def test_add_never(self):
        init_contract(risk="L1", goal="Test never")
        add_never("never delete failing tests")
        contract = load_contract()
        self.assertIn("never delete failing tests", contract["never"])

    def test_cli_show_alias_and_free_text_acs_rejected(self):
        import subprocess
        import sys
        script = str(Path(__file__).resolve().parent.parent / "scripts" / "xp_contract.py")
        # Free-text AC without AC-NN ID should fail fast with clear format instruction
        bad = subprocess.run(
            [sys.executable, script, "init", "--risk", "L1", "--goal", "Fix bug", "--acs", "Validate dates"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("AC-01", bad.stderr + bad.stdout)

        # Valid init + 'show' alias for 'get'
        ok = subprocess.run(
            [sys.executable, script, "init", "--risk", "L1", "--goal", "Fix bug", "--acs", "AC-01"],
            capture_output=True, text=True,
        )
        self.assertEqual(ok.returncode, 0)
        show = subprocess.run([sys.executable, script, "show"], capture_output=True, text=True)
        self.assertEqual(show.returncode, 0)
        self.assertIn("Fix bug", show.stdout)


if __name__ == "__main__":
    unittest.main()
