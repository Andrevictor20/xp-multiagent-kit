#!/usr/bin/env python3
"""tests/test_kit_lint.py — Testes unitários para o linter de governança do kit (AC-6)"""

import os
import tempfile
import unittest
from pathlib import Path

from scripts.kit_lint import (
    lint_version,
    lint_components_yaml,
    lint_agents_md_sections,
    lint_concept_duplications,
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


if __name__ == "__main__":
    unittest.main()
