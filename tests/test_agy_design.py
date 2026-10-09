#!/usr/bin/env python3
"""
tests/test_agy_design.py
Testes unitários para o integrador do OpenDesign com Antigravity (agy-design).
Cobertura integral dos Acceptance Criteria AC-1 a AC-6 (TDD RED -> GREEN).
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.agy_design import (
    check_open_design_installed,
    check_mcp_registered,
    sync_antigravity_mcp_configs,
    get_open_design_status,
    main,
)


class TestAgyDesign(unittest.TestCase):
    """Testes para o utilitário agy-design do XP Multi-Agent Kit."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_home = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_check_open_design_installed_found(self):
        with patch("shutil.which", return_value="/home/user/.local/bin/od"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="0.23.1\n", stderr="")
                res = check_open_design_installed()
                self.assertTrue(res["ok"])
                self.assertEqual(res["path"], "/home/user/.local/bin/od")
                self.assertEqual(res["version"], "0.23.1")

    def test_check_open_design_installed_missing(self):
        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.exists", return_value=False):
                res = check_open_design_installed()
                self.assertFalse(res["ok"])
                self.assertIsNone(res["path"])

    def test_check_mcp_registered_true(self):
        mcp_config_dir = self.mock_home / ".gemini" / "antigravity"
        mcp_config_dir.mkdir(parents=True, exist_ok=True)
        mcp_file = mcp_config_dir / "mcp_config.json"
        mcp_data = {
            "mcpServers": {
                "open-design": {
                    "command": "od",
                    "args": ["mcp", "serve"]
                }
            }
        }
        mcp_file.write_text(json.dumps(mcp_data), encoding="utf-8")

        with patch("pathlib.Path.home", return_value=self.mock_home):
            res = check_mcp_registered()
            self.assertTrue(res["registered"])
            self.assertIn("open-design", res["servers"])

    def test_check_mcp_registered_false_when_missing(self):
        with patch("pathlib.Path.home", return_value=self.mock_home):
            res = check_mcp_registered()
            self.assertFalse(res["registered"])

    def test_sync_antigravity_mcp_configs(self):
        source_dir = self.mock_home / ".gemini" / "antigravity"
        source_dir.mkdir(parents=True, exist_ok=True)
        source_file = source_dir / "mcp_config.json"
        test_payload = {"mcpServers": {"open-design": {"command": "od"}}}
        source_file.write_text(json.dumps(test_payload), encoding="utf-8")

        with patch("pathlib.Path.home", return_value=self.mock_home):
            synced = sync_antigravity_mcp_configs()
            self.assertGreaterEqual(len(synced), 1)

            ide_file = self.mock_home / ".gemini" / "antigravity-ide" / "mcp_config.json"
            config_file = self.mock_home / ".gemini" / "config" / "mcp_config.json"
            self.assertTrue(ide_file.exists())
            self.assertTrue(config_file.exists())
            
            data_ide = json.loads(ide_file.read_text(encoding="utf-8"))
            self.assertIn("open-design", data_ide["mcpServers"])

    def test_get_open_design_status(self):
        with patch("scripts.agy_design.check_open_design_installed") as mock_installed:
            with patch("scripts.agy_design.check_mcp_registered") as mock_mcp:
                mock_installed.return_value = {"ok": True, "path": "/bin/od", "version": "0.23.1"}
                mock_mcp.return_value = {"registered": True, "servers": ["open-design"]}
                status = get_open_design_status()
                self.assertTrue(status["installed"])
                self.assertTrue(status["mcp_registered"])
                self.assertEqual(status["version"], "0.23.1")

    def test_main_status_json_flag(self):
        with patch("scripts.agy_design.get_open_design_status") as mock_status:
            mock_status.return_value = {
                "installed": True,
                "version": "0.23.1",
                "path": "/bin/od",
                "mcp_registered": True,
                "servers": ["open-design"]
            }
            with patch("sys.argv", ["agy-design", "status", "--json"]):
                with patch("sys.stdout.write") as mock_stdout:
                    exit_code = main()
                    self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
