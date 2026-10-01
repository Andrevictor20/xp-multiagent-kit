#!/usr/bin/env python3
"""
scripts/conformance_report.py
Gerador mecânico de Conformance Report (E2).

O relatório de conformidade era escrito em prosa pelo modelo, o que consome
turnos e não é verificável. Aqui ele é DERIVADO dos artefatos: os Acceptance
Criteria do SPEC-NNN-ATDD.md, os testes que os referenciam e o resultado real
da execução (evidence_recorder ou JSON de resultados).

Regra de gate: AC sem teste, ou AC com teste em falha, é NON-COMPLIANT e
bloqueia a entrega.

Uso:
    agy-conformance --spec .agents/memory/SPEC-001-ATDD.md --tests tests/
    agy-conformance --spec SPEC.md --tests tests/ --results results.json --json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

AC_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?\*\*(AC-\d+)\*\*\s*[:\-]?\s*(.*)$", re.MULTILINE)
AC_INLINE_PATTERN = re.compile(r"\b(AC-\d+)\b")


def parse_acceptance_criteria(spec_text: str) -> List[Dict[str, str]]:
    """Extrai os Acceptance Criteria do SPEC, preservando a descrição original."""
    criteria: Dict[str, str] = {}
    for match in AC_PATTERN.finditer(spec_text):
        ac_id, description = match.group(1), match.group(2).strip()
        criteria.setdefault(ac_id, description)

    # Critérios citados apenas em tabelas SbE ou cenários Gherkin
    for match in AC_INLINE_PATTERN.finditer(spec_text):
        criteria.setdefault(match.group(1), "")

    return [
        {"id": ac_id, "description": criteria[ac_id]}
        for ac_id in sorted(criteria, key=lambda value: int(value.split("-")[1]))
    ]


TEST_DEF_PATTERN = re.compile(r"^\s*def\s+(test_\w+)\s*\(", re.MULTILINE)
NAME_AC_PATTERN = re.compile(r"(?<![a-z0-9])ac[_\-]?0*(\d+)(?!\d)", re.IGNORECASE)


def normalize_ac_id(number: str) -> str:
    """Converte o número capturado no formato canônico AC-NN."""
    return f"AC-{int(number):02d}"


def ac_ids_in_text(text: str) -> set:
    """Critérios citados literalmente (AC-01) ou no estilo de nome de teste (ac_01)."""
    ids = set(AC_INLINE_PATTERN.findall(text))
    ids.update(normalize_ac_id(number) for number in NAME_AC_PATTERN.findall(text))
    return ids


def split_test_blocks(content: str) -> List[tuple]:
    """Divide um arquivo de teste em blocos (nome_da_função, corpo)."""
    matches = list(TEST_DEF_PATTERN.finditer(content))
    blocks = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        blocks.append((match.group(1), content[match.start():end]))
    return blocks


def index_tests(test_roots: List[Path]) -> Dict[str, List[str]]:
    """
    Mapeia AC → testes que o referenciam, seja pelo nome da função
    (test_ac_01_..., test_ac01_...) seja por citação no corpo do teste
    (parametrize, docstring ou asserção).
    """
    mapping: Dict[str, List[str]] = {}
    for root in test_roots:
        files = [root] if root.is_file() else sorted(
            set(root.rglob("test_*.py")) | set(root.rglob("*_test.py"))
        )
        for path in files:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for name, body in split_test_blocks(content):
                for ac_id in ac_ids_in_text(name) | ac_ids_in_text(body):
                    qualified = f"{path.stem}::{name}"
                    mapping.setdefault(ac_id, [])
                    if qualified not in mapping[ac_id]:
                        mapping[ac_id].append(qualified)
    return mapping


def load_results(results_path: Optional[Path]) -> Dict[str, str]:
    """Carrega status por teste: {nome_do_teste: PASS|FAIL|SKIP}."""
    if not results_path or not results_path.is_file():
        return {}
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(data, dict):
        return {str(k): str(v).upper() for k, v in data.items()}
    return {}


def build_report(
    spec_text: str,
    test_roots: List[Path],
    results: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Monta a matriz AC → SbE/teste → status e o veredito de conformidade."""
    criteria = parse_acceptance_criteria(spec_text)
    mapping = index_tests(test_roots)
    results = results or {}

    rows: List[Dict[str, Any]] = []
    for criterion in criteria:
        ac_id = criterion["id"]
        tests = mapping.get(ac_id, [])
        statuses = [results.get(test, "NOT_RUN") for test in tests]

        if not tests:
            status = "NON-COMPLIANT"
            reason = "nenhum teste referencia este AC"
        elif any(value == "FAIL" for value in statuses):
            status = "NON-COMPLIANT"
            reason = "teste em falha"
        elif all(value == "PASS" for value in statuses):
            status = "COMPLIANT"
            reason = "coberto e aprovado"
        else:
            status = "PENDING"
            reason = "teste existe mas ainda sem resultado de execução"

        rows.append({
            "ac": ac_id,
            "description": criterion["description"],
            "tests": tests,
            "statuses": statuses,
            "status": status,
            "reason": reason,
        })

    compliant = sum(1 for row in rows if row["status"] == "COMPLIANT")
    return {
        "total": len(rows),
        "compliant": compliant,
        "non_compliant": sum(1 for row in rows if row["status"] == "NON-COMPLIANT"),
        "pending": sum(1 for row in rows if row["status"] == "PENDING"),
        "coverage_pct": round(compliant * 100 / len(rows), 1) if rows else 0.0,
        "gate": "BLOCKED" if any(row["status"] == "NON-COMPLIANT" for row in rows) else "OPEN",
        "rows": rows,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "## Conformance Report",
        "",
        f"**Resumo:** {report['compliant']}/{report['total']} critérios cobertos e aprovados "
        f"({report['coverage_pct']}%) • Gate: **{report['gate']}**",
        "",
        "| AC | Descrição | Teste | Status | Motivo |",
        "|----|-----------|-------|--------|--------|",
    ]
    for row in report["rows"]:
        tests = ", ".join(f"`{t}`" for t in row["tests"]) or "—"
        description = row["description"][:70] or "—"
        lines.append(
            f"| {row['ac']} | {description} | {tests} | {row['status']} | {row['reason']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Conformance Report mecânico (E2)")
    parser.add_argument("--spec", required=True, help="Caminho do SPEC-NNN-ATDD.md")
    parser.add_argument("--tests", nargs="+", default=["tests"], help="Raízes de testes")
    parser.add_argument("--results", help="JSON com {teste: PASS|FAIL}")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.is_file():
        print(f"❌ SPEC não encontrado: {spec_path}", file=sys.stderr)
        return 1

    report = build_report(
        spec_path.read_text(encoding="utf-8", errors="ignore"),
        [Path(root) for root in args.tests],
        load_results(Path(args.results)) if args.results else None,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(render_markdown(report))

    return 1 if report["gate"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
