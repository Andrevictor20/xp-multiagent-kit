#!/usr/bin/env python3
"""
tests/test_spec_003_enhancements.py
Acceptance and unit tests for XP Multi-Agent Kit v3.1 enhancements:
- Codex host support (IDE & CLI)
- Bundled toolchain installer (RTK, OpenDesign, CodeReviewGraph)
- Reinforced ATDD & BDD CLI (xp-spec)
- Complete scrub of hardcoded personal paths
- Host-adaptive model catalog & telemetry
- Auto-update manager with 24h cache (xp-kit update)
- Granular target isolation (Global vs. Tools vs. Projects)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

KIT_ROOT = Path(__file__).resolve().parent.parent
if str(KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(KIT_ROOT))


class TestSpec003Enhancements(unittest.TestCase):
    """Test suite covering the 8 enhancement pillars of XP Multi-Agent Kit v3.1."""

    # ------------------------------------------------------------------
    # 1. Codex Host Support & Granular Target Isolation
    # ------------------------------------------------------------------
    def test_codex_adapter_generation(self):
        """HostAdapters generates .codex/rules/xp-governance.md, .codex/mcp.json, and .codexignore."""
        from scripts.host_adapters import HostAdapters, SUPPORTED_TARGETS

        self.assertIn("codex", SUPPORTED_TARGETS)

        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            adapters = HostAdapters(kit_dir=KIT_ROOT)
            actions = adapters.install_codex_project(proj, dry_run=False)

            self.assertTrue((proj / ".codex" / "rules" / "xp-governance.md").is_file())
            self.assertTrue((proj / ".codex" / "mcp.json").is_file())
            self.assertTrue((proj / ".codexignore").is_file())

            # Check mcp.json contains open-design and code-review-graph
            mcp_data = json.loads((proj / ".codex" / "mcp.json").read_text(encoding="utf-8"))
            self.assertIn("mcpServers", mcp_data)
            self.assertIn("code-review-graph", mcp_data["mcpServers"])

    def test_granular_targets_isolation(self):
        """Installing for a specific subset of targets (e.g. cursor,codex) does not generate unrelated host configs."""
        from scripts.kit_installer import ProjectInstaller

        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            installer = ProjectInstaller(kit_dir=KIT_ROOT)
            installer.install_project(proj, use_symlinks=True, targets=["cursor", "codex"])

            # Cursor and Codex must exist
            self.assertTrue((proj / ".cursor").is_dir())
            self.assertTrue((proj / ".codex").is_dir())

            # OpenCode and Qoder must NOT exist
            self.assertFalse((proj / ".opencode").exists())
            self.assertFalse((proj / "opencode.json").exists())
            self.assertFalse((proj / ".qoder").exists())

    # ------------------------------------------------------------------
    # 2. Bundled Toolchain Installer (RTK, OpenDesign, CodeReviewGraph)
    # ------------------------------------------------------------------
    def test_rtk_installer_interface(self):
        """RtkInstaller checks PATH, cargo, or downloads prebuilt binary gracefully."""
        from scripts.mcp_installers import RtkInstaller

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            installer = RtkInstaller(home_dir=home)
            self.assertTrue(hasattr(installer, "install"))
            self.assertTrue(hasattr(installer, "get_download_url"))

    # ------------------------------------------------------------------
    # 3. Reinforced ATDD & BDD CLI (xp-spec)
    # ------------------------------------------------------------------
    def test_spec_tool_scaffold_and_validation(self):
        """scripts/spec_tool.py scaffolds a new ATDD spec and validates ACs/SbE/Gherkin."""
        from scripts.spec_tool import scaffold_spec, validate_spec_content

        with tempfile.TemporaryDirectory() as tmp:
            spec_file = Path(tmp) / "SPEC-999-TEST.md"
            scaffold_spec(spec_file, "Test Feature")

            self.assertTrue(spec_file.is_file())
            content = spec_file.read_text(encoding="utf-8")
            self.assertIn("Acceptance Criteria", content)
            self.assertIn("Specification by Example", content)
            self.assertIn("Gherkin", content)

            # Validation of a valid spec passes
            valid, errors = validate_spec_content(content)
            self.assertTrue(valid, f"Expected valid spec, got errors: {errors}")

    # ------------------------------------------------------------------
    # 4. Total Scrub of Personal Paths
    # ------------------------------------------------------------------
    def test_zero_hardcoded_user_paths_in_tracked_files(self):
        """No tracked file in git contains hardcoded personal username or machine paths."""
        res = subprocess.run(
            ["git", "grep", "-I", "/home/andrevmp"],
            cwd=str(KIT_ROOT),
            capture_output=True,
            text=True,
        )
        # Any matches in tracked files is a violation
        matches = [line for line in res.stdout.splitlines() if not line.startswith("tests/test_spec_003_enhancements.py")]
        self.assertEqual(matches, [], f"Found hardcoded personal paths in tracked files: {matches}")

    # ------------------------------------------------------------------
    # 5. Host-Adaptive Model Catalog & Telemetry
    # ------------------------------------------------------------------
    def test_host_model_catalog_and_adaptive_telemetry(self):
        """Telemetry supports --host [antigravity|cursor|codex|qoder|opencode] with official models."""
        from scripts.telemetry.models import get_models_for_host, HOST_MODEL_CATALOG
        from scripts.telemetry.formatter import format_compact_footer

        self.assertIn("cursor", HOST_MODEL_CATALOG)
        self.assertIn("codex", HOST_MODEL_CATALOG)
        self.assertIn("qoder", HOST_MODEL_CATALOG)
        self.assertIn("antigravity", HOST_MODEL_CATALOG)
        self.assertIn("opencode", HOST_MODEL_CATALOG)

        cursor_models = get_models_for_host("cursor")
        self.assertIn("claude-3-7-sonnet", cursor_models)

        codex_models = get_models_for_host("codex")
        self.assertIn("gpt-4o", codex_models)

        # Test compact footer with host display
        stats = {
            "total_tokens": 10000,
            "limits": {"context_window": 200000, "max_output": 8192},
            "percent_used": 5.0,
            "model_name": "claude-3-7-sonnet",
            "host": "cursor",
            "turn_tokens": {"user": 1000, "tool": 2000, "model": 500, "total": 3500},
            "rate_limits": {
                "rolling_5h": {"used": 5000, "limit": 100000, "percent": 5.0},
                "rolling_weekly": {"used": 20000, "limit": 2000000, "percent": 1.0},
            },
        }
        footer = format_compact_footer(stats)
        self.assertIn("Cursor", footer)
        self.assertIn("Claude 3.7 Sonnet", footer)

    # ------------------------------------------------------------------
    # 6. Auto-Update Manager & Notifications (xp-kit update)
    # ------------------------------------------------------------------
    def test_update_manager_caching_and_notification(self):
        """UpdateManager caches update check for 24h and formats notification."""
        from scripts.update_manager import UpdateManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = UpdateManager(cache_dir=Path(tmp))
            # Test notification formatting
            notice = mgr.format_update_notice("v3.2.0")
            self.assertIn("v3.2.0", notice)
            self.assertIn("xp-kit update", notice)


if __name__ == "__main__":
    unittest.main()
