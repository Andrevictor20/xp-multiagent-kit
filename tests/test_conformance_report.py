import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.conformance_report import (
    build_report,
    index_tests,
    parse_acceptance_criteria,
    render_markdown,
)

SPEC = """# SPEC-001-ATDD

## Acceptance Criteria
- **AC-01**: Login aceita credenciais válidas
- **AC-02**: Login rejeita senha incorreta
- **AC-03**: Sessão expira em 30 minutos

## SbE
| AC-01 | user@x.com | ok |
"""

TESTS = '''
def test_ac_01_login_valid_credentials():
    assert login("user@x.com", "ok") is True


def test_ac02_rejects_wrong_password():
    """Cobre AC-02."""
    assert login("user@x.com", "bad") is False
'''


class TestConformanceReport(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.spec = self.root / "SPEC-001-ATDD.md"
        self.spec.write_text(SPEC, encoding="utf-8")
        self.tests_dir = self.root / "tests"
        self.tests_dir.mkdir()
        (self.tests_dir / "test_login.py").write_text(TESTS, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parses_all_acceptance_criteria_including_sbe_references(self):
        criteria = parse_acceptance_criteria(SPEC)
        self.assertEqual([c["id"] for c in criteria], ["AC-01", "AC-02", "AC-03"])
        self.assertIn("Login aceita", criteria[0]["description"])

    def test_index_tests_maps_by_name_and_body_reference(self):
        mapping = index_tests([self.tests_dir])
        self.assertIn("test_login::test_ac_01_login_valid_credentials", mapping["AC-01"])
        self.assertIn("test_login::test_ac02_rejects_wrong_password", mapping["AC-02"])
        self.assertNotIn("AC-03", mapping)

    def test_uncovered_ac_blocks_the_gate(self):
        report = build_report(SPEC, [self.tests_dir])
        row = next(r for r in report["rows"] if r["ac"] == "AC-03")
        self.assertEqual(row["status"], "NON-COMPLIANT")
        self.assertEqual(report["gate"], "BLOCKED")

    def test_passing_results_mark_compliant(self):
        report = build_report(SPEC, [self.tests_dir], results={
            "test_login::test_ac_01_login_valid_credentials": "PASS",
            "test_login::test_ac02_rejects_wrong_password": "PASS",
        })
        row = next(r for r in report["rows"] if r["ac"] == "AC-01")
        self.assertEqual(row["status"], "COMPLIANT")
        self.assertEqual(report["compliant"], 2)

    def test_failing_result_blocks_gate(self):
        report = build_report(SPEC, [self.tests_dir], results={
            "test_login::test_ac_01_login_valid_credentials": "FAIL",
        })
        row = next(r for r in report["rows"] if r["ac"] == "AC-01")
        self.assertEqual(row["status"], "NON-COMPLIANT")
        self.assertEqual(report["gate"], "BLOCKED")

    def test_test_without_result_is_pending(self):
        report = build_report(SPEC, [self.tests_dir])
        row = next(r for r in report["rows"] if r["ac"] == "AC-01")
        self.assertEqual(row["status"], "PENDING")

    def test_render_markdown_contains_summary_and_gate(self):
        rendered = render_markdown(build_report(SPEC, [self.tests_dir]))
        self.assertIn("## Conformance Report", rendered)
        self.assertIn("0/3 critérios cobertos e aprovados", rendered)
        self.assertIn("Gate: **BLOCKED**", rendered)


if __name__ == "__main__":
    unittest.main()
