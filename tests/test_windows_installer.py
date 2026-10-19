#!/usr/bin/env python3
"""
tests/test_windows_installer.py
Unit and acceptance tests for Windows-native installation and tooling.
Tests install.ps1, install.cmd, Windows shims (.cmd), and WindowsPathConfigurator.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.kit_installer import (
    WindowsPathConfigurator,
    generate_windows_shims,
    SHIM_COMMANDS,
)


class TestWindowsInstaller(unittest.TestCase):
    """Verifies Windows installation components, shims, and path configurations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.bin_dir = self.temp_path / "bin"
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_windows_shims_generation(self):
        """generate_windows_shims creates valid .cmd batch files for all core CLI tools."""
        generated = generate_windows_shims(self.bin_dir, ROOT_DIR)
        self.assertTrue(len(generated) > 0)

        required_cmds = [
            "xp-spec", "xp-kit", "xp-run", "xp-conformance",
            "agy-spec", "agy-kit", "agy-effort", "agy-smart",
        ]
        for cmd in required_cmds:
            cmd_file = self.bin_dir / f"{cmd}.cmd"
            self.assertTrue(cmd_file.is_file(), f"Expected shim missing: {cmd_file}")

            content = cmd_file.read_text(encoding="utf-8")
            self.assertIn("@echo off", content)
            self.assertIn("%*", content, f"Shim {cmd}.cmd must forward arguments %*")
            self.assertIn("python", content.lower())
            self.assertIn("py -3", content, f"Shim {cmd}.cmd must support py -3 fallback")

    def test_agy_run_windows_build_argv(self):
        """agy-run build_argv must use cmd.exe or bash on Windows without /bin/sh."""
        import importlib.machinery
        script_path = str(ROOT_DIR / "scripts" / "agy-run")
        loader = importlib.machinery.SourceFileLoader("agy_run", script_path)
        mod = loader.load_module()

        with patch("platform.system", return_value="Windows"), \
             patch("shutil.which", return_value=None):
            argv = mod.build_argv("pytest -q")
            self.assertNotIn("/bin/sh", argv[0])
            self.assertTrue("cmd.exe" in argv[0] or "cmd" in argv[0])

    def test_windows_shim_commands_list_integrity(self):
        """SHIM_COMMANDS covers all essential tools with valid script targets."""
        self.assertIsInstance(SHIM_COMMANDS, dict)
        self.assertIn("xp-conformance", SHIM_COMMANDS)
        self.assertIn("xp-spec", SHIM_COMMANDS)
        self.assertIn("xp-kit", SHIM_COMMANDS)

        for cmd, script_rel in SHIM_COMMANDS.items():
            script_path = ROOT_DIR / script_rel
            self.assertTrue(script_path.is_file(), f"Target script for {cmd} does not exist: {script_path}")

    def test_windows_path_configurator_mocked_registry(self):
        """WindowsPathConfigurator updates Windows User Environment PATH idempotently."""
        configurator = WindowsPathConfigurator()

        # Mock winreg behavior
        mock_winreg = MagicMock()
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (r"C:\Existing\Path;C:\Python310", 1)
        mock_winreg.HKEY_CURRENT_USER = 1
        mock_winreg.KEY_READ = 2
        mock_winreg.KEY_WRITE = 4
        mock_winreg.REG_EXPAND_SZ = 2

        with patch.dict("sys.modules", {"winreg": mock_winreg}):
            target_bin = r"C:\Users\User\.local\bin"
            # First addition should update the registry
            updated = configurator.ensure_path_in_user_env(target_bin)
            self.assertTrue(updated)
            mock_winreg.SetValueEx.assert_called_once()
            called_args = mock_winreg.SetValueEx.call_args[0]
            self.assertIn(target_bin, called_args[4])

            # Reset call count
            mock_winreg.SetValueEx.reset_mock()
            # Second addition should detect target_bin already present and not modify
            mock_winreg.QueryValueEx.return_value = (f"C:\\Existing\\Path;{target_bin}", 1)
            updated_again = configurator.ensure_path_in_user_env(target_bin)
            self.assertFalse(updated_again)
            mock_winreg.SetValueEx.assert_not_called()

    def test_install_ps1_script_exists_and_syntax(self):
        """install.ps1 exists in repository root with valid PowerShell structure."""
        ps1_file = ROOT_DIR / "install.ps1"
        self.assertTrue(ps1_file.is_file(), "install.ps1 must exist in repository root")

        content = ps1_file.read_text(encoding="utf-8")
        self.assertIn("param(", content)
        self.assertIn("$Target", content)
        self.assertIn("$Scope", content)
        self.assertIn("$Lang", content)
        self.assertIn("python", content.lower())

    def test_install_cmd_script_exists_and_syntax(self):
        """install.cmd exists in repository root with valid batch script structure."""
        cmd_file = ROOT_DIR / "install.cmd"
        self.assertTrue(cmd_file.is_file(), "install.cmd must exist in repository root")

        content = cmd_file.read_text(encoding="utf-8")
        self.assertIn("@echo off", content)
        self.assertIn("python", content.lower())
        self.assertIn("kit_installer.py", content)


if __name__ == "__main__":
    unittest.main()
