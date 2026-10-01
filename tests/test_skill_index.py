import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.skill_index import (
    audit_context_budget,
    collect_skills,
    parse_frontmatter,
    render_index,
    split_skill,
)

SKILL_SMALL = """---
name: tdd-safety-net
description: Ciclo RED-GREEN-REFACTOR e Anti-Test-Bypass estrito.
---

# TDD Safety Net

Corpo curto.
"""

SKILL_BIG = """---
name: big-skill
description: Skill grande para teste de fatiamento.
---

# Big Skill

Introdução da skill.

## Seção Alfa

""" + ("conteúdo alfa " * 200) + """

## Seção Beta

""" + ("conteúdo beta " * 200) + """
"""


class TestSkillIndex(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.skills = self.root / ".agents" / "skills"
        (self.skills / "tdd-safety-net").mkdir(parents=True)
        (self.skills / "tdd-safety-net" / "SKILL.md").write_text(SKILL_SMALL, encoding="utf-8")
        (self.skills / "big-skill").mkdir(parents=True)
        self.big_path = self.skills / "big-skill" / "SKILL.md"
        self.big_path.write_text(SKILL_BIG, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parses_frontmatter_and_body(self):
        meta, body = parse_frontmatter(SKILL_SMALL)
        self.assertEqual(meta["name"], "tdd-safety-net")
        self.assertIn("RED-GREEN", meta["description"])
        self.assertNotIn("---", body)

    def test_collect_skills_reports_sizes(self):
        skills = collect_skills(self.skills)
        self.assertEqual([s["dir"] for s in skills], ["big-skill", "tdd-safety-net"])
        self.assertGreater(skills[0]["body_bytes"], skills[1]["body_bytes"])

    def test_render_index_is_one_line_per_skill(self):
        index = render_index(collect_skills(self.skills))
        self.assertIn("| `tdd-safety-net` |", index)
        self.assertIn("| `big-skill` |", index)
        self.assertNotIn("conteúdo alfa", index)
        self.assertLess(len(index), 1200)

    def test_render_index_truncates_long_descriptions(self):
        skills = collect_skills(self.skills)
        skills[0]["description"] = "x" * 500
        index = render_index(skills, max_line_chars=60)
        self.assertTrue(any(len(line) < 120 for line in index.splitlines() if "big-skill" in line))
        self.assertIn("…", index)

    def test_split_moves_sections_out_of_skill_body(self):
        result = split_skill(self.big_path)
        self.assertEqual(result["sections"], 2)

        new_body = self.big_path.read_text(encoding="utf-8")
        self.assertIn("name: big-skill", new_body)
        self.assertIn("[Seção Alfa](sections/secao-alfa.md)", new_body)
        self.assertNotIn("conteúdo alfa", new_body)

        section_file = self.big_path.parent / "sections" / "secao-alfa.md"
        self.assertTrue(section_file.is_file())
        self.assertIn("conteúdo alfa", section_file.read_text(encoding="utf-8"))
        self.assertLess(len(new_body.encode("utf-8")), result["original_bytes"])

    def test_split_dry_run_does_not_touch_disk(self):
        before = self.big_path.read_text(encoding="utf-8")
        split_skill(self.big_path, dry_run=True)
        self.assertEqual(self.big_path.read_text(encoding="utf-8"), before)
        self.assertFalse((self.big_path.parent / "sections").exists())

    def test_audit_flags_oversized_skill_and_memory(self):
        (self.root / ".agents" / "memory").mkdir(parents=True)
        (self.root / ".agents" / "memory" / "PROJECT_MEMORY.md").write_text(
            "x" * 20000, encoding="utf-8"
        )
        report = audit_context_budget(self.root)
        self.assertTrue(report["blocking"])
        self.assertIn("big-skill", [s["skill"] for s in report["oversized_skills"]])
        memory = next(f for f in report["findings"] if f["artifact"] == "PROJECT_MEMORY.md")
        self.assertEqual(memory["status"], "OVER")

    def test_audit_ok_for_lean_project(self):
        (self.root / "AGENTS.md").write_text("# Regras enxutas\n", encoding="utf-8")
        (self.big_path).write_text(SKILL_SMALL, encoding="utf-8")
        report = audit_context_budget(self.root)
        self.assertEqual(report["oversized_skills"], [])
        self.assertFalse(report["blocking"])


if __name__ == "__main__":
    unittest.main()
