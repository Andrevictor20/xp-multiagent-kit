#!/usr/bin/env python3
"""
tests/test_skill_profiles.py
Testes unitários para o gerenciador de perfis de skills (A2 / D3).
XP Multi-Agent Kit v2
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.skill_profiles import (
    PROFILES,
    apply_profile_move,
    apply_profile_symlinks,
    detect_current_profile,
    disable_skill,
    enable_skill,
    get_profile_skills,
    list_active_and_disabled,
    main,
)


class TestSkillProfilesDefinitions(unittest.TestCase):
    def test_core_profile_contains_essential_xp_skills(self):
        core = PROFILES["core"]
        self.assertIn("tdd-safety-net", core)
        self.assertIn("acceptance-test-driven", core)
        self.assertIn("conformance-tracker", core)
        self.assertIn("systematic-debugging", core)
        self.assertIn("no-workarounds", core)
        self.assertIn("token-budget-tracker", core)
        self.assertIn("project-memory", core)
        self.assertGreaterEqual(len(core), 12)
        self.assertLessEqual(len(core), 20)

    def test_backend_profile_extends_core(self):
        backend = PROFILES["backend"]
        core = PROFILES["core"]
        for s in core:
            self.assertIn(s, backend)
        self.assertIn("database-architecture", backend)
        self.assertIn("api-contracts", backend)
        self.assertIn("cloud-security-and-zero-trust", backend)

    def test_frontend_profile_extends_core(self):
        frontend = PROFILES["frontend"]
        core = PROFILES["core"]
        for s in core:
            self.assertIn(s, frontend)
        self.assertIn("frontend-taste-engineering", frontend)
        self.assertIn("design-tokens", frontend)
        self.assertIn("component-architecture", frontend)

    def test_get_profile_skills_all(self):
        all_skills = ["skill-a", "skill-b", "skill-c"]
        res = get_profile_skills("all", all_available=all_skills)
        self.assertEqual(res, set(all_skills))


class TestSkillProfilesSymlinkMode(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.master_dir = Path(self.temp_dir) / "master_skills"
        self.target_dir = Path(self.temp_dir) / "active_skills"
        self.master_dir.mkdir(parents=True)
        self.target_dir.mkdir(parents=True)

        # Criar 5 skills mockadas no master
        self.skills = ["tdd-safety-net", "conformance-tracker", "database-architecture", "frontend-taste-engineering", "minimalist-ui"]
        for s in self.skills:
            s_dir = self.master_dir / s
            s_dir.mkdir()
            (s_dir / "SKILL.md").write_text(f"---\nname: {s}\ndescription: desc\n---\nbody", encoding="utf-8")
            # Inicialmente todas linkadas
            (self.target_dir / s).symlink_to(s_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_apply_core_profile_symlinks(self):
        # core deve conter tdd-safety-net e conformance-tracker, mas não database ou frontend
        active, removed = apply_profile_symlinks(
            profile_name="core",
            master_dir=self.master_dir,
            target_dir=self.target_dir,
        )
        self.assertIn("tdd-safety-net", active)
        self.assertIn("conformance-tracker", active)
        self.assertIn("database-architecture", removed)
        self.assertIn("frontend-taste-engineering", removed)

        target_items = [p.name for p in self.target_dir.iterdir()]
        self.assertIn("tdd-safety-net", target_items)
        self.assertNotIn("database-architecture", target_items)

    def test_apply_all_profile_symlinks(self):
        # Primeiro reduz
        apply_profile_symlinks("core", self.master_dir, self.target_dir)
        # Depois restaura all
        active, removed = apply_profile_symlinks("all", self.master_dir, self.target_dir)
        self.assertEqual(len(removed), 0)
        self.assertEqual(set(active), set(self.skills))
        target_items = [p.name for p in self.target_dir.iterdir()]
        self.assertEqual(set(target_items), set(self.skills))


class TestSkillProfilesMoveMode(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.disabled_dir = Path(self.temp_dir) / "skills_disabled"
        self.skills_dir.mkdir(parents=True)

        self.skills = ["tdd-safety-net", "conformance-tracker", "database-architecture", "frontend-taste-engineering"]
        for s in self.skills:
            s_dir = self.skills_dir / s
            s_dir.mkdir()
            (s_dir / "SKILL.md").write_text(f"---\nname: {s}\ndescription: desc\n---\nbody", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_apply_core_profile_move(self):
        active, disabled = apply_profile_move(
            profile_name="core",
            skills_dir=self.skills_dir,
            disabled_dir=self.disabled_dir,
        )
        self.assertIn("tdd-safety-net", active)
        self.assertIn("database-architecture", disabled)
        self.assertTrue((self.disabled_dir / "database-architecture" / "SKILL.md").is_file())
        self.assertFalse((self.skills_dir / "database-architecture").exists())

    def test_enable_and_disable_individual_skill(self):
        # Desabilita database
        apply_profile_move("core", self.skills_dir, self.disabled_dir)
        # Reabilita database
        ok = enable_skill("database-architecture", self.skills_dir, self.disabled_dir)
        self.assertTrue(ok)
        self.assertTrue((self.skills_dir / "database-architecture" / "SKILL.md").is_file())

        # Desabilita manualmente
        ok = disable_skill("database-architecture", self.skills_dir, self.disabled_dir)
        self.assertTrue(ok)
        self.assertTrue((self.disabled_dir / "database-architecture" / "SKILL.md").is_file())

    def test_detect_profile(self):
        active = {"tdd-safety-net", "conformance-tracker"}
        # Se for subset do core
        prof = detect_current_profile(active)
        self.assertEqual(prof, "custom")


class TestSkillProfilesCLI(unittest.TestCase):
    def test_cli_list_runs_without_error(self):
        exit_code = main(["list"])
        self.assertEqual(exit_code, 0)

    def test_cli_status_runs_without_error(self):
        exit_code = main(["status"])
        self.assertEqual(exit_code, 0)

    def test_cli_apply_dry_run_runs_without_error(self):
        exit_code = main(["apply", "core", "--dry-run"])
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
