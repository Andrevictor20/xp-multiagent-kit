#!/usr/bin/env python3
"""
tests/test_multi_host_telemetry.py
TDD tests for multi-host adaptive telemetry (OpenCode SQLite parsing,
model catalogs for Muse Spark, host auto-detection, and ProjectInstaller AGENTS.md sync).
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.telemetry.catalogs import (
    MODEL_DISPLAY_NAMES,
    MODEL_LIMITS,
    HOST_MODEL_CATALOG,
    get_models_for_host,
)
from scripts.telemetry.parser import (
    find_active_opencode_session,
    parse_opencode_session,
    find_active_host_session,
)
from scripts.telemetry.formatter import format_message_footer
from scripts.kit_installer import ProjectInstaller


class TestMultiHostTelemetry(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.home_dir = Path(self.tmp_dir.name)
        self.opencode_dir = self.home_dir / ".local" / "share" / "opencode"
        self.opencode_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.opencode_dir / "opencode.db"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _create_sample_opencode_db(self, project_dir: str = "/tmp/test-project"):
        con = sqlite3.connect(str(self.db_path))
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE session (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                directory TEXT,
                title TEXT,
                time_created INTEGER,
                time_updated INTEGER
            );
        """)
        cur.execute("""
            CREATE TABLE message (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                time_created INTEGER,
                time_updated INTEGER,
                data TEXT
            );
        """)

        # Insert session
        session_id = "ses_test123"
        now_ms = 1792187607000
        cur.execute(
            "INSERT INTO session VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, "proj_abc", project_dir, "Test Chat", now_ms - 10000, now_ms),
        )

        # Insert user message
        cur.execute(
            "INSERT INTO message VALUES (?, ?, ?, ?, ?)",
            (
                "msg_user1",
                session_id,
                now_ms - 5000,
                now_ms - 5000,
                json.dumps({"role": "user", "content": "o kit está instalado?"}),
            ),
        )

        # Insert assistant message with real OpenCode token schema
        msg_data = {
            "role": "assistant",
            "modelID": "muse-spark-1.3-contributor-free",
            "providerID": "opencode",
            "tokens": {
                "total": 52687,
                "input": 933,
                "output": 360,
                "reasoning": 337,
                "cache": {"write": 0, "read": 51057},
            },
        }
        cur.execute(
            "INSERT INTO message VALUES (?, ?, ?, ?, ?)",
            ("msg_ast1", session_id, now_ms, now_ms, json.dumps(msg_data)),
        )
        con.commit()
        con.close()

    def test_muse_spark_model_catalog(self):
        """Muse Spark models must be registered in MODEL_LIMITS and MODEL_DISPLAY_NAMES."""
        self.assertIn("muse-spark-1.3-contributor-free", MODEL_LIMITS)
        self.assertIn("muse-spark", MODEL_LIMITS)
        self.assertEqual(MODEL_LIMITS["muse-spark-1.3-contributor-free"]["context_window"], 1_048_576)
        self.assertEqual(MODEL_DISPLAY_NAMES.get("muse-spark-1.3-contributor-free"), "Muse Spark 1.3 Free")
        self.assertIn("opencode", HOST_MODEL_CATALOG)
        self.assertIn("muse-spark-1.3-contributor-free", HOST_MODEL_CATALOG["opencode"]["models"])

    def test_find_and_parse_opencode_session(self):
        """find_active_opencode_session detects session from db and calculates accurate TokenStats."""
        project_dir = "/tmp/saturn-test"
        self._create_sample_opencode_db(project_dir=project_dir)

        session_info = find_active_opencode_session(
            home_dir=self.home_dir,
            current_dir=Path(project_dir),
        )
        self.assertIsNotNone(session_info)
        session_id, db_file, mtime = session_info
        self.assertEqual(session_id, "ses_test123")
        self.assertEqual(db_file, self.db_path)
        self.assertGreater(mtime, 0)

        stats, turn = parse_opencode_session(self.db_path, session_id)
        self.assertEqual(stats.model_name, "muse-spark-1.3-contributor-free")
        self.assertEqual(stats.total_tokens, 52687)
        self.assertEqual(stats.context_window, 1_048_576)
        self.assertAlmostEqual(stats.percent_used, 5.02, delta=0.1)
        self.assertEqual(turn.user_input_tokens, 933)
        self.assertEqual(turn.model_output_tokens, 360)
        self.assertEqual(turn.tool_tokens, 337)

        footer = format_message_footer(stats, turn, compact=True)
        self.assertIn("Contexto:", footer)
        self.assertIn("Muse Spark", footer)
        self.assertIn("1.05M", footer)

    def test_find_active_host_session_opencode_auto(self):
        """find_active_host_session automatically routes to opencode when matching cwd session exists."""
        project_dir = "/tmp/saturn-test"
        self._create_sample_opencode_db(project_dir=project_dir)

        stats, turn, host_found = find_active_host_session(
            host="auto",
            home_dir=self.home_dir,
            current_dir=Path(project_dir),
        )
        self.assertEqual(host_found, "opencode")
        self.assertEqual(stats.total_tokens, 52687)
        self.assertEqual(turn.total_tokens, 933 + 360 + 337)

    def test_project_installer_updates_agents_md(self):
        """ProjectInstaller must update AGENTS.md in target project and remove outdated kit_constants references."""
        kit_dir = Path(__file__).resolve().parent.parent
        target_dir = self.home_dir / "my_project"
        target_dir.mkdir(parents=True, exist_ok=True)
        # Create an outdated AGENTS.md in target_dir
        old_agents_md = target_dir / "AGENTS.md"
        old_agents_md.write_text("old content with scripts/kit_constants.py and SKILLS_INDEX.md na raiz", encoding="utf-8")

        installer = ProjectInstaller(kit_dir=kit_dir)
        res = installer.install_project(target_dir, use_symlinks=True, dry_run=False, targets=["all"])
        self.assertTrue(res["ok"])
        new_content = old_agents_md.read_text(encoding="utf-8")
        self.assertNotIn("scripts/kit_constants.py", new_content)
        self.assertIn("Global Agent Governance", new_content)


    def test_find_active_host_session_cursor_marker(self):
        """When current directory has .cursor, auto-detection selects cursor even if global transcript exists."""
        proj_dir = self.home_dir / "cursor_project"
        (proj_dir / ".cursor" / "rules").mkdir(parents=True, exist_ok=True)
        stats, turn, host_found = find_active_host_session(
            host="auto",
            home_dir=self.home_dir,
            current_dir=proj_dir,
        )
        self.assertEqual(host_found, "cursor")
        self.assertIn("claude", stats.model_name.lower())

    def test_find_active_host_session_codex_marker(self):
        """When current directory has .codex, auto-detection selects codex."""
        proj_dir = self.home_dir / "codex_project"
        (proj_dir / ".codex" / "rules").mkdir(parents=True, exist_ok=True)
        stats, turn, host_found = find_active_host_session(
            host="auto",
            home_dir=self.home_dir,
            current_dir=proj_dir,
        )
        self.assertEqual(host_found, "codex")
        self.assertIn("gpt-4o", stats.model_name.lower())

    def test_find_active_host_session_qoder_marker(self):
        """When current directory has .qoder, auto-detection selects qoder."""
        proj_dir = self.home_dir / "qoder_project"
        (proj_dir / ".qoder" / "rules").mkdir(parents=True, exist_ok=True)
        stats, turn, host_found = find_active_host_session(
            host="auto",
            home_dir=self.home_dir,
            current_dir=proj_dir,
        )
        self.assertEqual(host_found, "qoder")
        self.assertIn("deepseek", stats.model_name.lower())

    def test_project_installer_syncs_skills_and_agents(self):
        """ProjectInstaller must sync .agents/skills and .agents/agents to make SKILLS_INDEX.md available."""
        kit_dir = Path(__file__).resolve().parent.parent
        target_dir = self.home_dir / "target_proj_skills"
        installer = ProjectInstaller(kit_dir=kit_dir)
        res = installer.install_project(target_dir, use_symlinks=True, dry_run=False, targets=["all"])
        self.assertTrue(res["ok"])
        skills_dir = target_dir / ".agents" / "skills"
        self.assertTrue(skills_dir.is_dir() or skills_dir.is_symlink())
        skills_index = skills_dir / "SKILLS_INDEX.md"
        self.assertTrue(skills_index.is_file(), "SKILLS_INDEX.md must be accessible in injected project")
        agents_dir = target_dir / ".agents" / "agents"
        self.assertTrue(agents_dir.is_dir() or agents_dir.is_symlink())


if __name__ == "__main__":
    unittest.main()
