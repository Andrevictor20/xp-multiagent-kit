#!/usr/bin/env python3
"""tests/test_kit_lint.py — Testes unitários para o linter de governança do kit (AC-6)"""

import os
import tempfile
import unittest
from pathlib import Path

from scripts.kit_lint import (
    audit_global_config,
    lint_agent_skill_refs,
    lint_agents_md_sections,
    lint_components_yaml,
    lint_concept_duplications,
    lint_frontmatter_descriptions,
    lint_readme_accuracy,
    lint_version,
    run_all_lints,
)


class TestKitLint(unittest.TestCase):
    def test_lint_version(self):
        res = lint_version()
        self.assertTrue(res["valid"])
        self.assertEqual(res["version"], "4.0.0")

    def test_lint_components_yaml(self):
        res = lint_components_yaml()
        self.assertTrue(res["valid"])
        self.assertGreater(res["count"], 0)
        self.assertEqual(len(res["errors"]), 0)

    def test_lint_agents_md_sections(self):
        sample = """
# AGENTS.md
## CONTRATO: xp contract
## CONTEXTO: xp context
## FERRAMENTAS: xp, hooks
## ESTADO: run.json, PROJECT_MEMORY
## POLÍTICA: policy.yaml
## VERIFICAÇÃO: xp gate
## RECUPERAÇÃO: classes de falha, parar na 2ª repetição
## OBSERVABILIDADE: eventos + recibo
"""
        res = lint_agents_md_sections(sample)
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["missing"]), 0)

    def test_lint_agents_md_missing_section(self):
        sample = """
# AGENTS.md
## CONTRATO: xp contract
"""
        res = lint_agents_md_sections(sample)
        self.assertFalse(res["valid"])
        self.assertIn("VERIFICAÇÃO", res["missing"])

    def test_lint_readme_accuracy_real(self):
        res = lint_readme_accuracy()
        self.assertTrue(res["valid"], msg=f"Errors: {res.get('errors')}")
        self.assertEqual(res["real_agents"], 6)
        self.assertEqual(res["real_skills"], 24)
        self.assertEqual(res["real_flows"], 9)
        self.assertEqual(res["real_steps"], 10)

    def test_lint_readme_accuracy_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "README.md").write_text("# Test\n99 skills\n", encoding="utf-8")
            res = lint_readme_accuracy(tmp)
            self.assertFalse(res["valid"])
            self.assertTrue(any("99 skills" in e for e in res["errors"]))

    def test_lint_agent_skill_refs_real_and_broken(self):
        real = lint_agent_skill_refs()
        self.assertTrue(real["valid"], msg=f"Broken agent->skill refs: {real['errors']}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / ".agents" / "skills" / "ok-skill").mkdir(parents=True)
            (tmp / ".agents" / "skills" / "ok-skill" / "SKILL.md").write_text("---\nname: ok-skill\n---\n", encoding="utf-8")
            (tmp / ".agents" / "agents" / "demo").mkdir(parents=True)
            (tmp / ".agents" / "agents" / "demo" / "agent.md").write_text(
                "---\nname: demo\ndescription: Demo.\nskills:\n  - ghost-skill\n---\n",
                encoding="utf-8",
            )
            bad = lint_agent_skill_refs(tmp)
            self.assertFalse(bad["valid"])
            self.assertTrue(any("ghost-skill" in e for e in bad["errors"]))

    def test_lint_frontmatter_descriptions_enforces_token_cap(self):
        real = lint_frontmatter_descriptions()
        self.assertTrue(real["valid"], msg=f"Oversized descriptions: {real['errors']}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / ".agents" / "skills" / "verbose").mkdir(parents=True)
            (tmp / ".agents" / "skills" / "verbose" / "SKILL.md").write_text(
                f"---\nname: verbose\ndescription: {'a' * 140}\n---\n",
                encoding="utf-8",
            )
            bad = lint_frontmatter_descriptions(tmp, max_chars=110)
            self.assertFalse(bad["valid"])

    def test_audit_global_config_flags_duplicate_parent_rules(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cfg = root / "config"
            cfg.mkdir()
            (root / "GEMINI.md").write_text("# duplicate", encoding="utf-8")
            res = audit_global_config(cfg)
            self.assertEqual(res["status"], "WARNING")
            self.assertTrue(any("GEMINI.md" in w for w in res["warnings"]))


if __name__ == "__main__":
    unittest.main()
