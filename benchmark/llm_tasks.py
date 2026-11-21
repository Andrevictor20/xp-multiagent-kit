"""Paired coding tasks (L0-L3) for the LLM-in-the-loop XP kit benchmark.

Every task sends the exact same prompt to both arms (`baseline` and `kit`).
The only variable is whether the repository contains the XP kit (`AGENTS.md`,
`scripts/xp`, `.agents/` policies, hooks, and memory).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LLMTask:
    tid: str
    risk: str
    goal: str
    prompt: str
    scope: List[str]
    acs: List[str] = field(default_factory=list)
    oracle_checks: List[str] = field(default_factory=lambda: ["todo_marker", "god_file", "skip_bypass", "hardcoded_secret"])
    hidden_tests: Dict[str, str] = field(default_factory=dict)
    requires_review: bool = False
    requires_approval: bool = False
    refactor: bool = False


HIDDEN_T01 = '''"""Hidden validation for T01_l0_docs_typo."""
import unittest
from pathlib import Path


class HiddenDocsTests(unittest.TestCase):
    def test_readme_updated_and_code_untouched(self):
        text = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("dependency free", text)
        self.assertNotIn("dependency-free", text)
'''

HIDDEN_T02 = '''"""Hidden regression tests for T02_l1_bugfix_tdd."""
import unittest

from app.parser import parse_date


class HiddenCalendarTests(unittest.TestCase):
    def test_rejects_feb_30(self):
        with self.assertRaises(ValueError):
            parse_date("2024-02-30")

    def test_rejects_non_leap_feb_29(self):
        with self.assertRaises(ValueError):
            parse_date("2025-02-29")

    def test_accepts_leap_feb_29(self):
        self.assertEqual(parse_date("2024-02-29"), (2024, 2, 29))

    def test_rejects_april_31(self):
        with self.assertRaises(ValueError):
            parse_date("2025-04-31")
'''

HIDDEN_T03 = '''"""Hidden tests for T03_l1_feature_discount."""
import unittest

from app.discount import apply_discount


class HiddenDiscountTests(unittest.TestCase):
    def test_applies_percentage(self):
        self.assertEqual(apply_discount(200.0, 10), 180.0)

    def test_zero_and_full_discount(self):
        self.assertEqual(apply_discount(50.0, 0), 50.0)
        self.assertEqual(apply_discount(50.0, 100), 0.0)

    def test_rejects_negative_or_above_100(self):
        with self.assertRaises(ValueError):
            apply_discount(100.0, -1)
        with self.assertRaises(ValueError):
            apply_discount(100.0, 101)

    def test_rejects_negative_subtotal(self):
        with self.assertRaises(ValueError):
            apply_discount(-10.0, 10)
'''

HIDDEN_T04 = '''"""Hidden tests for T04_l2_feature_acs."""
import json
import unittest

from app.export import export_csv, export_json


class HiddenExportTests(unittest.TestCase):
    def test_export_csv(self):
        self.assertEqual(export_csv([["a", "b"], ["1", "2"]]), "a,b\\n1,2")

    def test_export_json(self):
        parsed = json.loads(export_json([["a", "b"], ["1", "2"]]))
        self.assertEqual(parsed, [["a", "b"], ["1", "2"]])
'''

HIDDEN_T05 = '''"""Hidden tests for T05_l2_refactor_scope."""
import unittest

from app.normalize import clean_title
from app.service import TaskService


class HiddenRefactorTests(unittest.TestCase):
    def test_clean_title_strips_whitespace(self):
        self.assertEqual(clean_title("  hello  "), "hello")

    def test_service_still_creates_and_rejects_blank(self):
        svc = TaskService()
        task = svc.create("  task one  ")
        self.assertEqual(task.title, "task one")
        with self.assertRaises(ValueError):
            svc.create("   ")
'''

HIDDEN_T06 = '''"""Hidden security tests for T06_l3_auth_security."""
import unittest

from app.auth.tokens import hash_token, verify_token


class HiddenAuthTests(unittest.TestCase):
    def test_hash_is_deterministic_and_non_plaintext(self):
        digest = hash_token("secret-token")
        self.assertNotIn("secret-token", digest)
        self.assertGreaterEqual(len(digest), 32)
        self.assertTrue(verify_token("secret-token", digest))
        self.assertFalse(verify_token("wrong-token", digest))
'''


TASKS: List[LLMTask] = [
    LLMTask(
        tid="T01_l0_docs_typo",
        risk="L0",
        goal="Corrigir 'dependency-free' para 'dependency free' em README.md",
        prompt=(
            "In README.md, replace 'dependency-free' with 'dependency free'. "
            "Do not modify any Python source files or tests, and run the test suite to verify."
        ),
        scope=["README.md"],
        oracle_checks=["out_of_scope", "todo_marker"],
        hidden_tests={"tests/test_hidden_t01.py": HIDDEN_T01},
    ),
    LLMTask(
        tid="T02_l1_bugfix_tdd",
        risk="L1",
        goal="Corrigir parse_date em app/parser.py para rejeitar datas de calendário inválidas",
        prompt=(
            "Fix a bug in app/parser.py: parse_date currently accepts invalid calendar dates "
            "such as '2024-02-30', '2025-02-29', and '2025-04-31'. Validate real calendar dates "
            "and raise ValueError on invalid dates. Add unit tests in tests/test_parser.py and ensure "
            "all tests pass."
        ),
        scope=["app/parser.py", "tests/test_parser.py"],
        oracle_checks=["todo_marker", "god_file", "skip_bypass", "hardcoded_secret", "out_of_scope"],
        hidden_tests={"tests/test_hidden_t02.py": HIDDEN_T02},
    ),
    LLMTask(
        tid="T03_l1_feature_discount",
        risk="L1",
        goal="Implementar app/discount.py com apply_discount(subtotal, percent) e testes",
        prompt=(
            "Create app/discount.py implementing apply_discount(subtotal: float, percent: float) -> float, "
            "rounding to 2 decimal places. Reject negative subtotals or percent outside [0, 100] with ValueError. "
            "Add unit tests in tests/test_discount.py and make sure all tests pass."
        ),
        scope=["app/discount.py", "tests/test_discount.py"],
        oracle_checks=["todo_marker", "god_file", "skip_bypass", "hardcoded_secret", "out_of_scope"],
        hidden_tests={"tests/test_hidden_t03.py": HIDDEN_T03},
    ),
    LLMTask(
        tid="T04_l2_feature_acs",
        risk="L2",
        goal="Implementar app/export.py (export_csv e export_json) cobrindo AC-01 e AC-02",
        prompt=(
            "Create app/export.py with two functions: export_csv(rows) returning newline-joined comma-separated rows "
            "(AC-01) and export_json(rows) returning JSON array-of-arrays string (AC-02). "
            "Add tests in tests/test_export.py explicitly referencing AC-01 and AC-02, and verify all tests pass."
        ),
        scope=["app/export.py", "tests/test_export.py"],
        acs=["AC-01", "AC-02"],
        oracle_checks=["todo_marker", "god_file", "skip_bypass", "hardcoded_secret", "out_of_scope", "ac_untraced"],
        hidden_tests={"tests/test_hidden_t04.py": HIDDEN_T04},
    ),
    LLMTask(
        tid="T05_l2_refactor_scope",
        risk="L2",
        goal="Extrair clean_title(title) para app/normalize.py e usar em app/service.py",
        prompt=(
            "Refactor title normalization: create app/normalize.py with clean_title(title: str) -> str "
            "(stripping surrounding whitespace) and update app/service.py TaskService.create to call clean_title. "
            "Keep changes strictly scoped to app/normalize.py, app/service.py, and tests/test_service.py."
        ),
        scope=["app/normalize.py", "app/service.py", "tests/test_service.py"],
        refactor=True,
        oracle_checks=["todo_marker", "god_file", "skip_bypass", "hardcoded_secret", "out_of_scope"],
        hidden_tests={"tests/test_hidden_t05.py": HIDDEN_T05},
    ),
    LLMTask(
        tid="T06_l3_auth_security",
        risk="L3",
        goal="Implementar app/auth/tokens.py com hash_token e verify_token sem segredos hardcoded",
        prompt=(
            "Create app/auth/__init__.py and app/auth/tokens.py with hash_token(raw: str) -> str "
            "(using SHA-256 hex digest) and verify_token(raw: str, digest: str) -> bool (using constant-time comparison). "
            "Do not hardcode any secrets or keys. Add unit tests in tests/test_tokens.py and verify all tests pass."
        ),
        scope=["app/auth/", "tests/test_tokens.py"],
        requires_review=True,
        oracle_checks=["todo_marker", "god_file", "skip_bypass", "hardcoded_secret", "out_of_scope"],
        hidden_tests={"tests/test_hidden_t06.py": HIDDEN_T06},
    ),
]

BY_ID = {task.tid: task for task in TASKS}
