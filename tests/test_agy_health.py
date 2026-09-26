#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.agy_health import (
    check_plugin_directories,
    check_memory_health,
    evaluate_quota_health,
    check_symlinks_health,
    run_system_health_check,
)


class TestAgyHealth(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_check_plugin_directories_heals_when_missing(self):
        fake_plugin = self.temp_path / ".gemini" / "config" / "plugins" / "googlecloudtools.datacloud_telemetry"
        self.assertFalse(fake_plugin.exists())

        res = check_plugin_directories(target_dir=fake_plugin)
        self.assertTrue(res["ok"])
        self.assertTrue(fake_plugin.is_dir())
        self.assertEqual(res["status"], "RECOVERED")

    def test_check_plugin_directories_ok_when_exists(self):
        fake_plugin = self.temp_path / ".gemini" / "config" / "plugins" / "googlecloudtools.datacloud_telemetry"
        fake_plugin.mkdir(parents=True, exist_ok=True)

        res = check_plugin_directories(target_dir=fake_plugin)
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "OK")

    def test_check_memory_health_healthy(self):
        fake_memory = self.temp_path / "PROJECT_MEMORY.md"
        fake_memory.write_text("Small memory content", encoding="utf-8")

        res = check_memory_health(memory_path=fake_memory, warn_kb=25)
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "OK")

    def test_check_memory_health_warn_on_bloat(self):
        fake_memory = self.temp_path / "PROJECT_MEMORY.md"
        # 30 KB file
        fake_memory.write_text("X" * 30 * 1024, encoding="utf-8")

        res = check_memory_health(memory_path=fake_memory, warn_kb=25)
        self.assertFalse(res["ok"])
        self.assertEqual(res["status"], "WARN")
        self.assertIn("agy-memory-archive", res["recommendation"])

    def test_evaluate_quota_health_healthy(self):
        quotas = {
            "gemini_5h_used_pct": 15.0,
            "gemini_weekly_used_pct": 60.0,
            "3p_5h_used_pct": 0.0,
            "3p_weekly_used_pct": 30.0,
        }
        res = evaluate_quota_health(quotas, threshold=80.0)
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "OK")

    def test_evaluate_quota_health_warns_on_critical_quota(self):
        quotas = {
            "gemini_5h_used_pct": 88.0,
            "gemini_weekly_used_pct": 85.0,
        }
        res = evaluate_quota_health(quotas, threshold=80.0)
        self.assertFalse(res["ok"])
        self.assertEqual(res["status"], "WARN")
        self.assertIn("88.0%", res["details"])

    def test_run_system_health_check(self):
        fake_plugin = self.temp_path / "plugins" / "googlecloudtools.datacloud_telemetry"
        fake_plugin.mkdir(parents=True, exist_ok=True)
        fake_memory = self.temp_path / "PROJECT_MEMORY.md"
        fake_memory.write_text("Small memory", encoding="utf-8")

        report = run_system_health_check(
            plugin_dir=fake_plugin,
            memory_file=fake_memory,
            mock_rpc={"gemini_5h_used_pct": 10.0, "gemini_weekly_used_pct": 40.0},
        )
        self.assertTrue(report["overall_healthy"])
        self.assertIn("checks", report)


if __name__ == "__main__":
    unittest.main()
