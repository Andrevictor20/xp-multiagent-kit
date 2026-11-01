#!/usr/bin/env python3
"""
scripts/goldfish_review.py
Goldfish Multi-Pass Review & Completeness Engine (xp-goldfish / agy-goldfish).
Enforces Elephant-Goldfish Model (EGM) standards, Heilmeier Catechism,
Zero-Decision Implementation Readiness, Code Completeness (<500 lines, zero TODO/stubs),
and Spec-vs-Code Drift auditing across the XP Multi-Agent Kit (SPEC-005).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HEILMEIER_QUESTIONS = [
    ("goal", re.compile(r"(o que estamos tentando fazer|what are we trying to do|objetivo|problem statement|por que estamos construindo)", re.I)),
    ("current_state", re.compile(r"(como isso é feito hoje|how is it done today|estado atual|current practice|limites da prática)", re.I)),
    ("novelty", re.compile(r"(o que há de novo|what is new|nova abordagem|rationale|arquitetura proposta)", re.I)),
    ("impact", re.compile(r"(quem se importa|who cares|impacto|business value)", re.I)),
    ("risks_and_costs", re.compile(r"(riscos|custos|risks and costs|trade-offs|tradeoffs|restrições)", re.I)),
    ("metrics_and_tests", re.compile(r"(métricas|testes|criterios de sucesso|critérios de sucesso|success metrics|evaluation|acceptance criteria)", re.I)),
]

GLAZING_WORDS = [
    "brilliant", "brilhante", "seamless", "seamlessly", "blazingly fast",
    "spot-on", "perfeito", "perfect", "excelente", "excellent", "flawless",
    "magically", "effortlessly", "world-class", "revolucionário",
]

ALTERNATIVES_PATTERN = re.compile(
    r"(alternativas consideradas|alternatives considered|alternativa\s+[a1]|rejected options|opções descartadas)",
    re.I,
)
TARGET_FILES_OP_PATTERN = re.compile(
    r"(?:\|[^\n]*\b(?:Create|Modify|Delete|Criar|Modificar|Remover)\b[^\n]*\||`(?:Create|Modify|Delete)`)",
    re.I,
)
AC_HEADER_PATTERN = re.compile(r"^#{2,4}\s+(AC-\d+)\b", re.M)


def _strip_inline_quotes(line: str) -> str:
    """Removes backtick spans and single/double-quoted literals from a single line."""
    return re.sub(r"`[^`]*`|\"[^\"]*\"|'[^']*'", "", line)


def check_anti_glazing(content: str) -> List[str]:
    """Detects sycophantic / buzzword phrasing banned by Goldfish protocols."""
    findings: List[str] = []
    for idx, line in enumerate(content.splitlines(), 1):
        cleaned_line = _strip_inline_quotes(line)
        for word in GLAZING_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", cleaned_line, re.IGNORECASE):
                findings.append(
                    f"Linha {idx}: Palavra desaconselhada detectada ('{word}'). Elimine adjetivos vazios/elogios."
                )
    return findings


def check_placeholders(content: str) -> List[str]:
    """Detects unfinished placeholders (TODO, TBD, FIXME, {{...}}) outside inline code/quotes."""
    findings: List[str] = []
    for idx, line in enumerate(content.splitlines(), 1):
        cleaned = _strip_inline_quotes(line)
        if re.search(r"\{\{[^{}]+\}\}", cleaned):
            findings.append(f"Linha {idx}: Placeholder de template não preenchido ('{{{{...}}}}').")
        if re.search(r"\b(TODO|TBD|FIXME|XXX)\b", cleaned):
            findings.append(f"Linha {idx}: Marcador de decisão incompleta (TODO/TBD/FIXME) detectado.")
    return findings


def validate_heilmeier_compliance(content: str) -> Dict[str, Any]:
    """Verifies if a spec answers the core Heilmeier Catechism dimensions."""
    results: Dict[str, bool] = {}
    missing: List[str] = []
    for key, regex in HEILMEIER_QUESTIONS:
        matched = bool(regex.search(content))
        results[key] = matched
        if not matched:
            missing.append(key)
    return {
        "compliant": len(missing) == 0,
        "score": (len(HEILMEIER_QUESTIONS) - len(missing)) / len(HEILMEIER_QUESTIONS) * 100.0,
        "results": results,
        "missing": missing,
    }


def validate_implementation_readiness(content: str) -> Dict[str, Any]:
    """
    Pass 1 (EGM Spec & Zero-Decision Implementation Readiness):
    Validates Heilmeier Catechism, Alternatives Considered, Zero-Decision Target Files,
    Acceptance Criteria (AC-N), Anti-Glazing, and Zero Placeholders.
    """
    heilmeier = validate_heilmeier_compliance(content)
    placeholders = check_placeholders(content)
    glazing = check_anti_glazing(content)
    has_alternatives = bool(ALTERNATIVES_PATTERN.search(content))
    has_target_files = bool(TARGET_FILES_OP_PATTERN.search(content))
    acs = AC_HEADER_PATTERN.findall(content)
    target_matches = TARGET_FILES_OP_PATTERN.findall(content)
    touches_more_than_8 = len(target_matches) > 8

    checks = {
        "heilmeier_catechism": heilmeier["compliant"],
        "alternatives_considered": has_alternatives,
        "zero_decision_target_files": has_target_files,
        "acceptance_criteria": len(acs) > 0,
        "no_placeholders": len(placeholders) == 0,
        "anti_glazing": len(glazing) == 0,
    }
    missing = [k for k, ok in checks.items() if not ok]
    score = (len(checks) - len(missing)) / len(checks) * 100.0

    return {
        "compliant": len(missing) == 0,
        "score": score,
        "checks": checks,
        "results": checks,
        "missing": missing,
        "heilmeier": heilmeier,
        "placeholders": placeholders,
        "glazing": glazing,
        "declared_acs": acs,
        "touches_more_than_8_files": touches_more_than_8,
    }


def should_trigger_llm_review(risk: str = "L1", p1_result: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """
    Decides whether an LLM Goldfish review is triggered (AC-9).
    EGM_LLM_REVIEW = {"L2": "on_warning", "L3": "single"}
    Rollback: XP_EGM_LLM=always|off
    Extra trigger: spec touches >8 files
    """
    env_override = os.environ.get("XP_EGM_LLM", "").strip().lower()
    if env_override == "always":
        return True, "override_always"
    if env_override == "off":
        return False, "override_off"

    if risk == "L3":
        return True, "L3_single"
    if risk == "L2":
        if p1_result and not p1_result.get("compliant"):
            return True, "L2_on_warning"
        if p1_result and p1_result.get("touches_more_than_8_files"):
            return True, "L2_touches_more_than_8_files"
    return False, "no_trigger"


def audit_code_completeness(code_paths: List[Path], max_lines: int = 500) -> Dict[str, Any]:
    """
    Pass 2 (EGM Codebase Details & Implementation Completeness):
    Verifies all target code files exist, respect the <500-line No-God-Files rule,
    and contain zero unfinished TODOs, NotImplementedError stubs, or type workarounds.
    """
    missing_files: List[str] = []
    incomplete_findings: List[str] = []

    for p in code_paths:
        path_obj = Path(p)
        if not path_obj.is_file():
            missing_files.append(str(path_obj))
            incomplete_findings.append(f"{path_obj}: Arquivo planejado não encontrado no disco.")
            continue

        lines = path_obj.read_text(encoding="utf-8", errors="ignore").splitlines()
        if len(lines) > max_lines:
            incomplete_findings.append(
                f"{path_obj.name}: Arquivo com {len(lines)} linhas excede o limite No-God-Files ({max_lines} linhas)."
            )

        for idx, line in enumerate(lines, 1):
            cleaned = _strip_inline_quotes(line)
            if re.search(r"(?:#|//)\s*(?:TODO|FIXME|TBD|HACK)\b", cleaned, re.I):
                incomplete_findings.append(f"{path_obj.name}:{idx}: Comentário de código incompleto (TODO/FIXME).")
            if re.search(r"^\s*raise\s+NotImplementedError\b", line):
                incomplete_findings.append(f"{path_obj.name}:{idx}: Stub NotImplementedError deixado na implementação.")
            if re.search(r"(?:@ts-ignore|@ts-expect-error|\bas\s+any\b)", cleaned):
                incomplete_findings.append(f"{path_obj.name}:{idx}: Workaround de supressão de tipo detectado.")

    compliant = len(missing_files) == 0 and len(incomplete_findings) == 0
    return {
        "compliant": compliant,
        "files_checked": len(code_paths),
        "missing_files": missing_files,
        "findings": incomplete_findings,
    }


def audit_spec_code_drift(
    spec_content: str,
    code_paths: List[Path],
    test_paths: List[Path],
) -> Dict[str, Any]:
    """
    Pass 3 (EGM Spec-vs-Code Drift & AC Traceability):
    Verifies at least 1 AC-N is declared and 100% of AC-N items are covered in test_paths.
    """
    declared_acs = AC_HEADER_PATTERN.findall(spec_content)
    combined_tests = ""
    for tp in test_paths:
        p = Path(tp)
        if p.is_file():
            combined_tests += "\n" + p.read_text(encoding="utf-8", errors="ignore")

    uncovered_acs: List[str] = []
    for ac in declared_acs:
        num = ac.split("-")[1]
        pat = re.compile(rf"(?:\bAC-{num}\b|\bac[_-]?{num}\b)", re.I)
        if not pat.search(combined_tests):
            uncovered_acs.append(ac)

    compliant = len(declared_acs) > 0 and len(uncovered_acs) == 0
    return {
        "compliant": compliant,
        "declared_acs": declared_acs,
        "uncovered_acs": uncovered_acs,
        "test_files_checked": len(test_paths),
    }


def run_multipass_egm_review(
    spec_path: Path,
    code_paths: Optional[List[Path]] = None,
    test_paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    """Executes all 3 passes of the Elephant-Goldfish Model (EGM) Review."""
    spec_file = Path(spec_path)
    content = spec_file.read_text(encoding="utf-8") if spec_file.is_file() else ""
    p1 = validate_implementation_readiness(content) if content else {"compliant": False, "missing": ["spec_file_missing"]}
    p2 = audit_code_completeness(code_paths or [])
    p3 = audit_spec_code_drift(content, code_paths or [], test_paths or [])

    overall = bool(p1.get("compliant") and p2.get("compliant") and p3.get("compliant"))
    return {
        "spec_file": str(spec_file),
        "passes_completed": 3,
        "pass1_spec": p1,
        "pass2_code": p2,
        "pass3_drift": p3,
        "overall_compliant": overall,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Goldfish Multi-Pass EGM Review & Completeness Validator (xp-goldfish / agy-goldfish)"
    )
    parser.add_argument("doc_path", nargs="?", help="Caminho para o documento de especificação (.md)")
    parser.add_argument("--multipass", action="store_true", help="Executa as 3 passadas completas de revisão EGM")
    parser.add_argument("--check-readiness", action="store_true", help="Valida Pass 1 (Zero-Decision Implementation Readiness)")
    parser.add_argument("--check-code", action="store_true", help="Valida Pass 2 (Code Completeness & No-God-Files)")
    parser.add_argument("--code-files", nargs="*", default=[], help="Arquivos de código implementados para auditoria Pass 2")
    parser.add_argument("--test-files", nargs="*", default=[], help="Arquivos de teste para auditoria de drift Pass 3")
    parser.add_argument("--json", action="store_true", help="Emite relatório estruturado em JSON")

    args = parser.parse_args(argv)
    if not args.doc_path and not args.check_code:
        parser.print_help()
        return 1

    if args.check_code and not args.multipass:
        p2 = audit_code_completeness([Path(p) for p in args.code_files])
        if args.json:
            print(json.dumps(p2, indent=2, ensure_ascii=False))
        else:
            print(f"=== Relatório EGM Pass 2 (Code Completeness): {'PASS' if p2['compliant'] else 'FAIL'} ===")
            for f_msg in p2.get("findings", []):
                print(f"  - [Blocker] {f_msg}")
        return 0 if p2["compliant"] else 2

    doc_path = Path(args.doc_path)
    if not doc_path.exists():
        print(f"Erro: Arquivo '{doc_path}' não encontrado.", file=sys.stderr)
        return 1

    content = doc_path.read_text(encoding="utf-8")

    if args.check_readiness and not args.multipass:
        p1 = validate_implementation_readiness(content)
        if args.json:
            print(json.dumps(p1, indent=2, ensure_ascii=False))
        else:
            print(f"=== Relatório EGM Pass 1 (Zero-Decision Readiness): {doc_path.name} ===")
            print(f" • Status: {'PASS' if p1['compliant'] else 'FAIL'} ({p1.get('score', 0.0):.1f}%)")
            if not p1["compliant"]:
                print(f" • Bloqueios: {', '.join(p1.get('missing', []))}")
        return 0 if p1["compliant"] else 2

    if args.multipass:
        report = run_multipass_egm_review(
            spec_path=doc_path,
            code_paths=[Path(p) for p in args.code_files],
            test_paths=[Path(p) for p in args.test_files],
        )
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            p1, p2, p3 = report["pass1_spec"], report["pass2_code"], report["pass3_drift"]
            print(f"=== Relatório Multi-Pass EGM (Goldfish Review): {doc_path.name} ===")
            print(f" • Pass 1 (Spec & Zero-Decision Readiness): {'PASS' if p1['compliant'] else 'FAIL'} ({p1.get('score', 0.0):.1f}%)")
            if not p1["compliant"]:
                print(f"   - Ausente/Bloqueado: {', '.join(p1.get('missing', []))}")
            print(f" • Pass 2 (Codebase Details & Completeness): {'PASS' if p2['compliant'] else 'FAIL'} ({p2['files_checked']} arquivos)")
            for f_msg in p2.get("findings", []):
                print(f"   - [Blocker] {f_msg}")
            print(f" • Pass 3 (Spec-vs-Code Drift & ACs)      : {'PASS' if p3['compliant'] else 'FAIL'} ({len(p3['declared_acs']) - len(p3['uncovered_acs'])}/{len(p3['declared_acs'])} ACs)")
            if p3.get("uncovered_acs"):
                print(f"   - [Blocker] ACs sem cobertura de teste: {', '.join(p3['uncovered_acs'])}")
            verdict = "COMPLIANT (3/3 PASSES GREEN)" if report["overall_compliant"] else "NON-COMPLIANT (BLOCKED)"
            print(f"\nVeredito Final EGM: {verdict}")
        return 0 if report["overall_compliant"] else 2

    glazing_issues = check_anti_glazing(content)
    heilmeier = validate_heilmeier_compliance(content)
    print(f"=== Relatório Goldfish Review: {doc_path.name} ===")
    print(f"Score Heilmeier: {heilmeier['score']:.1f}%")
    if heilmeier["compliant"]:
        print(" [PASS] Todas as dimensões do Catecismo de Heilmeier foram endereçadas.")
    else:
        print(f" [FAIL] Dimensões ausentes no documento: {', '.join(heilmeier['missing'])}")
    if glazing_issues:
        print(f"\n[ALERTA ANTI-GLAZING] {len(glazing_issues)} ocorrências encontradas:")
        for issue in glazing_issues:
            print(f"  - {issue}")
    else:
        print(" [PASS] Conformidade Anti-Glazing: Zero adjetivos vazios ou bajulação.")
    return 0 if heilmeier["compliant"] else 2


if __name__ == "__main__":
    sys.exit(main())
