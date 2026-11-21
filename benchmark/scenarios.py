"""Benchmark scenarios: defective changes and benign changes.

Every scenario is a paired unit of work. The same final state is produced in
both arms; the only difference is whether the XP kit's gates and hooks are
present. `red` files define the failing test that must exist before the fix
(strict TDD), and `green` files define the delivered state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

UNITTEST = "python3 -m unittest discover -s tests -q"
FileMap = Dict[str, Union[str, Callable[[Path], None], None]]


@dataclass
class Scenario:
    sid: str
    kind: str
    risk: str
    goal: str
    oracle: str
    scope: List[str] = field(default_factory=lambda: ["app/", "tests/"])
    acs: List[str] = field(default_factory=list)
    needs_red: bool = True
    freeze_tests: bool = False
    refactor: bool = False
    requires_review: bool = False
    requires_approval: bool = False
    red: FileMap = field(default_factory=dict)
    green: FileMap = field(default_factory=dict)
    expected_block_step: Optional[int] = None
    hypothesis: str = ""


def _replace(rel: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(repo: Path) -> None:
        path = repo / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise RuntimeError(f"anchor not found in {rel}: {old!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    return apply


def _append(rel: str, extra: str) -> Callable[[Path], None]:
    def apply(repo: Path) -> None:
        path = repo / rel
        path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n" + extra, encoding="utf-8")

    return apply


def _god_module(lines: int = 520) -> str:
    rows = [
        f"    ({index}, \"region-{index:03d}\", {index * 7 % 97}),"
        for index in range(1, lines - 20)
    ]
    body = "\n".join(rows)
    return (
        '"""Generated regional table (deliberately oversized fixture)."""\n'
        "from __future__ import annotations\n\n"
        "REGIONS = [\n"
        f"{body}\n"
        "]\n\n\n"
        "def render_report(limit: int = 3) -> str:\n"
        '    """Render the first N regions as a compact line."""\n'
        "    head = REGIONS[:limit]\n"
        '    return " | ".join(f"{code}:{name}" for code, name, _ in head)\n'
    )


def _delete(rel: str) -> Callable[[Path], None]:
    def apply(repo: Path) -> None:
        path = repo / rel
        if path.is_file():
            path.unlink()

    return apply


def _patch(rel: str, *pairs: Tuple[str, str]) -> Callable[[Path], None]:
    def apply(repo: Path) -> None:
        path = repo / rel
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            if old not in text:
                raise RuntimeError(f"anchor not found in {rel}: {old!r}")
            text = text.replace(old, new, 1)
        path.write_text(text, encoding="utf-8")

    return apply


DISCOUNT_TEST = '''"""Tests for app.discount (AC-01)."""
import unittest

from app.discount import apply_discount


class DiscountTests(unittest.TestCase):
    def test_applies_percentage(self):
        """AC-01: a 10% discount on 200 yields 180."""
        self.assertEqual(apply_discount(200.0, 10), 180.0)

    def test_rejects_out_of_range_percent(self):
        with self.assertRaises(ValueError):
            apply_discount(10.0, 120)
'''

DISCOUNT_GOOD = '''"""Discount rules (AC-01)."""
from __future__ import annotations


def apply_discount(subtotal: float, percent: float) -> float:
    """Apply a percentage discount to a subtotal."""
    if percent < 0 or percent > 100:
        raise ValueError("percent out of range")
    return round(subtotal * (1 - percent / 100.0), 2)
'''

DISCOUNT_TODO = '''"""Discount rules (AC-01)."""
from __future__ import annotations


def apply_discount(subtotal: float, percent: float) -> float:
    """Apply a percentage discount to a subtotal."""
    if percent < 0 or percent > 100:
        raise ValueError("percent out of range")
    # TODO: suportar cupons expirados antes do lancamento
    return round(subtotal * (1 - percent / 100.0), 2)
'''

DISCOUNT_BUGGY = '''"""Discount rules (AC-01)."""
from __future__ import annotations


def apply_discount(subtotal: float, percent: float) -> float:
    """Apply a percentage discount to a subtotal."""
    if percent < 0 or percent > 100:
        raise ValueError("percent out of range")
    if percent == 100:
        return round(subtotal, 2)
    return round(subtotal * (1 - percent / 100.0), 2)
'''

EXPORT_TEST = '''"""Tests for app.export."""
import unittest

from app.export import export_csv


class ExportTests(unittest.TestCase):
    def test_exports_csv(self):
        """AC-01: rows are rendered as CSV."""
        self.assertEqual(export_csv([["a", "b"], ["1", "2"]]), "a,b\\n1,2")
'''

EXPORT_IMPL = '''"""Export helpers (AC-01, AC-02)."""
from __future__ import annotations

from typing import Iterable, List


def export_csv(rows: Iterable[List[str]]) -> str:
    """AC-01: render rows as CSV."""
    return "\\n".join(",".join(str(cell) for cell in row) for row in rows)


def export_json(rows: Iterable[List[str]]) -> str:
    """AC-02: render rows as a JSON matrix."""
    import json

    return json.dumps([list(row) for row in rows], ensure_ascii=False)
'''

TOKENS_TEST = '''"""Tests for app.auth.tokens."""
import unittest

from app.auth.tokens import hash_token


class TokenTests(unittest.TestCase):
    def test_hash_is_stable(self):
        self.assertEqual(hash_token("abc"), hash_token("abc"))

    def test_hash_hides_secret(self):
        self.assertNotIn("abc", hash_token("abc"))
'''

TOKENS_IMPL = '''"""Token helpers."""
from __future__ import annotations

import hashlib


def hash_token(raw: str) -> str:
    """Return a stable, non-reversible digest for a token."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
'''

FORMAT_TEST = '''"""Tests for app.format."""
import unittest

from app.format import format_percent


class FormatTests(unittest.TestCase):
    def test_renders_one_decimal(self):
        """AC-01: percentages use one decimal place."""
        self.assertEqual(format_percent(12.345), "12.3%")
'''

FORMAT_IMPL = '''"""Formatting helpers (AC-01)."""
from __future__ import annotations


def format_percent(value: float) -> str:
    """AC-01: render a percentage with one decimal place."""
    return f"{value:.1f}%"
'''

CONFIG_TEST = '''"""Tests for app.config."""
import unittest

from app.config import load_settings


class ConfigTests(unittest.TestCase):
    def test_loads_two_keys(self):
        settings = load_settings()
        self.assertEqual(sorted(settings), ["api_key", "region"])
'''

CONFIG_IMPL = '''"""Runtime settings."""
from __future__ import annotations

API_KEY = "sk_live_9f8a7b6c5d4e3f2a"
REGION = "sa-east-1"


def load_settings() -> dict:
    return {"api_key": API_KEY, "region": REGION}
'''

SKIP_TEST_EXTRA = '''
    @unittest.skip("falha intermitente no CI")
    def test_rejects_negative_percent(self):
        with self.assertRaises(ValueError):
            apply_discount(10.0, -5)
'''

DISCOUNT_NEGATIVE_BUG = '''"""Discount rules (AC-01)."""
from __future__ import annotations


def apply_discount(subtotal: float, percent: float) -> float:
    """Apply a percentage discount to a subtotal."""
    if percent > 100:
        raise ValueError("percent out of range")
    return round(subtotal * (1 - percent / 100.0), 2)
'''

MIGRATION_TEST = r'''"""Tests for the delivery index migration."""
import unittest
from pathlib import Path


class MigrationTests(unittest.TestCase):
    def test_migration_creates_index(self):
        sql = Path("migrations/0001_add_task_index.sql")
        self.assertTrue(sql.is_file())
        self.assertIn("CREATE INDEX", sql.read_text(encoding="utf-8"))
'''

MIGRATION_SQL = """CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks (done);
"""


SCENARIOS: List[Scenario] = [
    Scenario(
        sid="D01_todo_stub", kind="defect", risk="L1", oracle="todo_marker",
        goal="Adicionar regra de desconto percentual", acs=["AC-01"],
        red={"tests/test_discount.py": DISCOUNT_TEST},
        green={"app/discount.py": DISCOUNT_TODO},
        expected_block_step=4,
        hypothesis="Gate step 4 bloqueia entrega incompleta com TODO.",
    ),
    Scenario(
        sid="D02_god_file", kind="defect", risk="L1", oracle="god_file",
        goal="Adicionar relatorio de regioes",
        red={"tests/test_reports.py":
             "import unittest\nfrom app.reports import render_report\n\n\n"
             "class ReportTests(unittest.TestCase):\n"
             "    def test_renders_head(self):\n"
             "        self.assertIn('region-001', render_report(1))\n"},
        green={"app/reports.py": _god_module()},
        expected_block_step=4,
        hypothesis="Gate step 4 bloqueia God-file > 499 linhas.",
    ),
    Scenario(
        sid="D03_test_deleted", kind="defect", risk="L1", oracle="test_removed",
        goal="Ajustar arredondamento de totais", needs_red=False, freeze_tests=True,
        green={
            "app/pricing.py": _replace(
                "app/pricing.py",
                '    return f"{amount:.2f}"',
                '    return f"{amount:.0f}"',
            ),
            "tests/test_pricing.py": _delete("tests/test_pricing.py"),
        },
        expected_block_step=3,
        hypothesis="Gate step 3 bloqueia remocao de teste congelado (anti-bypass).",
    ),
    Scenario(
        sid="D04_ac_untraced", kind="defect", risk="L2", oracle="ac_untraced",
        goal="Exportar relatorios em CSV e JSON", acs=["AC-01", "AC-02"],
        red={"tests/test_export.py": EXPORT_TEST},
        green={"app/export.py": EXPORT_IMPL},
        expected_block_step=9,
        hypothesis="Gate step 9 bloqueia AC declarado sem teste rastreavel.",
    ),
    Scenario(
        sid="D05_regression_shipped", kind="defect", risk="L1", oracle="failing_tests",
        goal="Tratar desconto de 100 por cento",
        red={"tests/test_discount.py": DISCOUNT_TEST.replace(
            "    def test_rejects_out_of_range_percent(self):",
            "    def test_full_discount_zeroes_total(self):\n"
            "        self.assertEqual(apply_discount(50.0, 100), 0.0)\n\n"
            "    def test_rejects_out_of_range_percent(self):",
        )},
        green={"app/discount.py": DISCOUNT_BUGGY},
        expected_block_step=8,
        hypothesis="Gate step 8 bloqueia regressao; baseline tambem falha (paridade).",
    ),
    Scenario(
        sid="D06_out_of_scope", kind="defect", risk="L1", oracle="out_of_scope",
        goal="Aceitar sufixo k em inteiros",
        scope=["app/parser.py", "tests/test_parser.py"],
        red={"tests/test_parser.py": _append(
            "tests/test_parser.py",
            "\n\nclass ParseScaledTests(unittest.TestCase):\n"
            "    def test_parses_k_suffix(self):\n"
            "        from app.parser import parse_scaled\n\n"
            "        self.assertEqual(parse_scaled(\"5k\"), 5000)\n",
        )},
        green={
            "app/parser.py": _append(
                "app/parser.py",
                "\n\ndef parse_scaled(raw: object) -> int:\n"
                "    \"\"\"Parse integers with k/m suffixes.\"\"\"\n"
                "    text = str(raw).strip().lower()\n"
                "    scale = {\"k\": 1000, \"m\": 1000000}\n"
                "    if text and text[-1] in scale:\n"
                "        return int(text[:-1]) * scale[text[-1]]\n"
                "    return int(text)\n",
            ),
            "app/pricing.py": _append(
                "app/pricing.py",
                "\n\ndef bulk_discount(total: float) -> float:\n"
                "    \"\"\"Undeclared side change outside the task scope.\"\"\"\n"
                "    return round(total * 0.9, 2)\n",
            ),
        },
        expected_block_step=2,
        hypothesis="Gate step 2 contem diff fora do scope declarado.",
    ),
    Scenario(
        sid="D07_skip_bypass", kind="defect", risk="L1", oracle="skip_bypass",
        goal="Validar desconto percentual",
        red={"tests/test_discount.py": DISCOUNT_TEST.replace(
            "    def test_rejects_out_of_range_percent(self):",
            "    def test_rejects_negative_percent(self):\n"
            "        with self.assertRaises(ValueError):\n"
            "            apply_discount(10.0, -5)\n\n"
            "    def test_rejects_out_of_range_percent(self):",
        )},
        green={
            "app/discount.py": DISCOUNT_NEGATIVE_BUG,
            "tests/test_discount.py": _replace(
                "tests/test_discount.py",
                "    def test_rejects_negative_percent(self):\n"
                "        with self.assertRaises(ValueError):\n"
                "            apply_discount(10.0, -5)\n",
                "    @unittest.skip(\"intermitente no CI\")\n"
                "    def test_rejects_negative_percent(self):\n"
                "        with self.assertRaises(ValueError):\n"
                "            apply_discount(10.0, -5)\n",
            ),
        },
        expected_block_step=None,
        hypothesis="Lacuna esperada: skip nao e detectado por gate nem baseline.",
    ),
    Scenario(
        sid="D08_hardcoded_secret", kind="defect", risk="L1", oracle="hardcoded_secret",
        goal="Carregar configuracao de ambiente",
        red={"tests/test_config.py": CONFIG_TEST},
        green={"app/config.py": CONFIG_IMPL},
        expected_block_step=None,
        hypothesis="Lacuna esperada: segredo hardcoded nao e detectado mecanicamente.",
    ),
    Scenario(
        sid="D09_no_red_evidence", kind="defect", risk="L1", oracle="no_red_evidence",
        goal="Adicionar formatador de percentual", needs_red=False,
        scope=["app/format.py", "tests/test_format.py"],
        green={
            "app/format.py": FORMAT_IMPL,
            "tests/test_format.py": FORMAT_TEST,
        },
        expected_block_step=7,
        hypothesis="Gate step 7 bloqueia GREEN sem RED registrado.",
    ),
    Scenario(
        sid="D10_review_tier_bypass", kind="defect", risk="L2", oracle="review_not_recorded",
        goal="Adicionar hash de tokens de sessao",
        scope=["app/auth/", "tests/test_tokens.py"],
        red={"tests/test_tokens.py": TOKENS_TEST},
        green={"app/auth/tokens.py": TOKENS_IMPL, "app/auth/__init__.py": ""},
        expected_block_step=10,
        hypothesis="Gate step 10 exige revisor independente para tier review.",
    ),
    Scenario(
        sid="B01_docs_typo", kind="benign", risk="L0", oracle="clean",
        goal="Corrigir erro de digitacao na documentacao", needs_red=False,
        scope=["README.md"],
        green={"README.md": _replace("README.md", "dependency-free", "dependency free")},
        hypothesis="Controle: mudanca L0 trivial deve passar nos dois bracos.",
    ),
    Scenario(
        sid="B02_small_feature", kind="benign", risk="L1", oracle="clean",
        goal="Adicionar formatador de percentual", acs=["AC-01"],
        scope=["app/format.py", "tests/test_format.py"],
        red={"tests/test_format.py": FORMAT_TEST},
        green={"app/format.py": FORMAT_IMPL},
        hypothesis="Feature pequena com TDD completo passa nos dois bracos.",
    ),
    Scenario(
        sid="B03_bugfix_red_green", kind="benign", risk="L1", oracle="clean",
        goal="Rejeitar datas de calendario invalidas",
        scope=["app/parser.py", "tests/test_parser.py"],
        red={"tests/test_parser.py": _append(
            "tests/test_parser.py",
            "\n\nclass CalendarValidationTests(unittest.TestCase):\n"
            "    def test_rejects_february_30(self):\n"
            "        with self.assertRaises(ValueError):\n"
            "            parse_date(\"2024-02-30\")\n",
        )},
        green={"app/parser.py": _replace(
            "app/parser.py",
            "    if not 1 <= day <= 31:\n        raise ValueError(f\"invalid day: {raw!r}\")\n    return year, month, day",
            "    if not 1 <= day <= 31:\n        raise ValueError(f\"invalid day: {raw!r}\")\n"
            "    import datetime\n\n"
            "    datetime.date(year, month, day)\n"
            "    return year, month, day",
        )},
        hypothesis="Bugfix com RED->GREEN passa nos dois bracos.",
    ),
    Scenario(
        sid="B04_refactor", kind="benign", risk="L1", oracle="clean",
        goal="Renomear estado interno do servico", needs_red=False, refactor=True,
        scope=["app/service.py", "app/normalize.py"],
        green={
            "app/normalize.py": '"""Title normalization (extracted during refactor)."""\n'
            "from __future__ import annotations\n\n\n"
            "def clean_title(title: str) -> str:\n"
            '    """Strip surrounding whitespace from a title."""\n'
            "    return title.strip()\n",
            "app/service.py": _patch(
                "app/service.py",
                ("from typing import Dict, List, Optional",
                 "from typing import Dict, List, Optional\n\nfrom app.normalize import clean_title"),
                ("        cleaned = title.strip()", "        cleaned = clean_title(title)"),
            ),
        },
        hypothesis="Refactor declarado dispensa RED e passa nos dois bracos.",
    ),
    Scenario(
        sid="B05_auth_review_ok", kind="benign", risk="L2", oracle="clean",
        goal="Adicionar hash de tokens de sessao", requires_review=True,
        scope=["app/auth/", "tests/test_tokens.py"],
        red={"tests/test_tokens.py": TOKENS_TEST},
        green={"app/auth/tokens.py": TOKENS_IMPL, "app/auth/__init__.py": ""},
        hypothesis="Tier review passa com revisao registrada (custo: 1 passo humano).",
    ),
    Scenario(
        sid="B06_migration_human_ok", kind="benign", risk="L3", oracle="clean",
        goal="Adicionar indice de tarefas concluidas", requires_approval=True,
        scope=["migrations/", "tests/test_migration.py"],
        red={"tests/test_migration.py": MIGRATION_TEST},
        green={"migrations/0001_add_task_index.sql": MIGRATION_SQL},
        hypothesis="Tier human passa com aprovacao registrada (custo: 1 aprovacao humana).",
    ),
]

BY_ID = {scenario.sid: scenario for scenario in SCENARIOS}
