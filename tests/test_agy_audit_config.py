#!/usr/bin/env python3
"""
Unit tests for agy-audit-config utility.
Tests detection of bloated rules, eager MCP servers, and skill context budget overflow.
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AUDIT_BIN = REPO_ROOT / "scripts" / "agy-audit-config"


class TestAgyAuditConfig(unittest.TestCase):
    def setUp(self):
        self.assertTrue(AUDIT_BIN.exists(), f"Audit script not found at {AUDIT_BIN}")

    def test_clean_config_reports_healthy(self):
        """A clean configuration directory should report 0 bloat issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            (config_dir / "rules").mkdir()
            (config_dir / "skills").mkdir()

            # Create a small lean rule
            (config_dir / "rules" / "lean_rule.md").write_text("# Lean Rule\nDo good work.\n")

            proc = subprocess.run(
                [str(AUDIT_BIN), "--config-dir", str(config_dir), "--json"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "HEALTHY")
            self.assertEqual(len(data["bloat_warnings"]), 0)

    def test_bloated_rules_detected(self):
        """Rule files exceeding 150 lines should trigger a warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            (config_dir / "rules").mkdir()

            # Create a bloated rule (> 150 lines)
            bloated_lines = ["# Bloated Rule"] + [f"- Line {i}" for i in range(200)]
            (config_dir / "rules" / "bloated.md").write_text("\n".join(bloated_lines))

            proc = subprocess.run(
                [str(AUDIT_BIN), "--config-dir", str(config_dir), "--json"],
                text=True,
                capture_output=True,
            )
            data = json.loads(proc.stdout)
            self.assertIn("WARNING", data["status"])
            self.assertTrue(any("bloated.md" in w for w in data["bloat_warnings"]))

    def test_eager_mcp_detected(self):
        """MCP servers with eager tools should be flagged for optimization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            mcp_config = {
                "mcpServers": {
                    "heavy-server": {
                        "command": "node",
                        "args": ["server.js"],
                        "eager": True,
                    }
                }
            }
            (config_dir / "mcp_config.json").write_text(json.dumps(mcp_config))

            proc = subprocess.run(
                [str(AUDIT_BIN), "--config-dir", str(config_dir), "--json"],
                text=True,
                capture_output=True,
            )
            data = json.loads(proc.stdout)
            self.assertTrue(any("heavy-server" in w for w in data["bloat_warnings"]))


if __name__ == "__main__":
    unittest.main()
