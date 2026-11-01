#!/usr/bin/env python3
"""tests/test_xp_cli.py — Testes unitários para o CLI scripts/xp"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestXpCLI(unittest.TestCase):
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

    def test_xp_cli_contract_init(self):
        cmd = [sys.executable, "scripts/xp", "contract", "init", "--risk", "L0", "--goal", "CLI test"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Contract initialized", res.stdout)

    def test_xp_cli_approve(self):
        cmd = [sys.executable, "scripts/xp", "approve", "migration_123"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Aprovação humana registrada", res.stdout)


if __name__ == "__main__":
    unittest.main()
