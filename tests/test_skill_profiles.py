#!/usr/bin/env python3
"""
tests/test_skill_profiles.py
Testes unitários para o gerenciador de perfis de skills do XP Multi-Agent Kit v4.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.skill_profiles import (
    PROFILES,
    SKILL_DESCRIPTIONS,
    apply_profile_move,
    apply_profile_symlinks,
    detect_current_profile,
    disable_skill,
    enable_skill,
    get_profile_skills,
    main,
)


class TestSkillProfilesDefinitions(unittest.TestCase):
    def test_core_profile_contains_only_existing_v4_skills(self):
        core = PROFILES["core"]
        existing = {p.parent.name for p in Path(".agents/skills").glob("*/SKILL.md")}
        self.assertTrue(core.issubset(existing), f"Skills inexistentes no CORE: {core - existing}")
        self.assertIn("tdd-safety-net", core)
        self.assertIn("spec-pyramid", core)
        self.assertIn("code-hygiene-review", core)
        self.assertIn("project-memory", core)

    def test_backend_profile_extends_core(self):
        backend = PROFILES["backend"]
        core = PROFILES["core"]
        existing = {p.parent.name for p in Path(".agents/skills").glob("*/SKILL.md")}
        self.assertTrue(core.issubset(backend))
        self.assertTrue(backend.issubset(existing))
        self.assertIn("database-architecture", backend)
        self.assertIn("api-contracts", backend)
        self.assertIn("cloud-and-iac-security", backend)

    def test_frontend_profile_extends_core(self):
        frontend = PROFILES["frontend"]
        core = PROFILES["core"]
        existing = {p.parent.name for p in Path(".agents/skills").glob("*/SKILL.md")}
        self.assertTrue(core.issubset(frontend))
        self.assertTrue(frontend.issubset(existing))
        self.assertIn("craft", frontend)
        self.assertIn("craft-setup", frontend)
        self.assertIn("craft-critique", frontend)

    def test_skill_descriptions_loaded_from_frontmatter(self):
        self.assertEqual(len(SKILL_DESCRIPTIONS), 24)
        for name, desc in SKILL_DESCRIPTIONS.items():
            self.assertTrue(desc, f"Descrição vazia para {name}")
            self.assertLessEqual(len(desc), 110, f"Descrição longa demais para {name}: {len(desc)}")

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

        self.skills = ["tdd-safety-net", "spec-pyramid", "database-architecture", "craft"]
        for s in self.skills:
            s_dir = self.master_dir / s
            s_dir.mkdir()
            (s_dir / "SKILL.md").write_text(f"---\nname: {s}\ndescription: desc\n---\nbody", encoding="utf-8")
            (self.target_dir / s).symlink_to(s_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_apply_core_profile_symlinks(self):
        active, removed = apply_profile_symlinks("core", self.master_dir, self.target_dir)
        self.assertIn("tdd-safety-net", active)
        self.assertIn("spec-pyramid", active)
        self.assertIn("database-architecture", removed)
        self.assertIn("craft", removed)
        target_items = [p.name for p in self.target_dir.iterdir()]
        self.assertIn("tdd-safety-net", target_items)
        self.assertNotIn("database-architecture", target_items)

    def test_apply_all_profile_symlinks(self):
        apply_profile_symlinks("core", self.master_dir, self.target_dir)
        active, removed = apply_profile_symlinks("all", self.master_dir, self.target_dir)
        self.assertEqual(len(removed), 0)
        self.assertEqual(set(active), set(self.skills))


class TestSkillProfilesMoveMode(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.disabled_dir = Path(self.temp_dir) / "skills_disabled"
        self.skills_dir.mkdir(parents=True)

        self.skills = ["tdd-safety-net", "spec-pyramid", "database-architecture", "craft"]
        for s in self.skills:
            s_dir = self.skills_dir / s
            s_dir.mkdir()
            (s_dir / "SKILL.md").write_text(f"---\nname: {s}\ndescription: desc\n---\nbody", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_apply_core_profile_move(self):
        active, disabled = apply_profile_move("core", self.skills_dir, self.disabled_dir)
        self.assertIn("tdd-safety-net", active)
        self.assertIn("database-architecture", disabled)
        self.assertTrue((self.disabled_dir / "database-architecture" / "SKILL.md").is_file())
        self.assertFalse((self.skills_dir / "database-architecture").exists())

    def test_enable_and_disable_individual_skill(self):
        apply_profile_move("core", self.skills_dir, self.disabled_dir)
        self.assertTrue(enable_skill("database-architecture", self.skills_dir, self.disabled_dir))
        self.assertTrue((self.skills_dir / "database-architecture" / "SKILL.md").is_file())
        self.assertTrue(disable_skill("database-architecture", self.skills_dir, self.disabled_dir))
        self.assertTrue((self.disabled_dir / "database-architecture" / "SKILL.md").is_file())

    def test_detect_profile(self):
        self.assertEqual(detect_current_profile({"tdd-safety-net", "spec-pyramid"}), "custom")


class TestSkillProfilesCLI(unittest.TestCase):
    def test_cli_list_status_and_dry_run(self):
        self.assertEqual(main(["list"]), 0)
        self.assertEqual(main(["status"]), 0)
        self.assertEqual(main(["apply", "core", "--dry-run"]), 0)


if __name__ == "__main__":
    unittest.main()
