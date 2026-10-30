#!/usr/bin/env python3
"""
Goldfish Review Protocol Validator & Helper.
Enforces Elephant-Goldfish Model (EGM) standards and Heilmeier Catechism compliance
on design documents and specifications within the XP Multi-Agent Kit.
"""

import sys
import os
import re
from pathlib import Path

HEILMEIER_QUESTIONS = [
    ("goal", re.compile(r"(o que estamos tentando fazer|what are we trying to do|objetivo|problem statement)", re.I)),
    ("current_state", re.compile(r"(como isso é feito hoje|how is it done today|estado atual|current practice)", re.I)),
    ("novelty", re.compile(r"(o que há de novo|what is new|nova abordagem|rationale)", re.I)),
    ("impact", re.compile(r"(quem se importa|who cares|impacto|business value)", re.I)),
    ("risks_and_costs", re.compile(r"(riscos|custos|risks and costs|trade-offs|tradeoffs)", re.I)),
    ("metrics_and_tests", re.compile(r"(métricas|testes|criterios de sucesso|success metrics|evaluation)", re.I)),
]

GLAZING_WORDS = [
    "brilliant", "brilhante", "seamless", "seamlessly", "blazingly fast",
    "spot-on", "perfeito", "perfect", "excelente", "excellent", "flawless"
]

def check_anti_glazing(content: str) -> list:
    """Detects sycophantic / buzzword phrasing banned by Goldfish protocols."""
    findings = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        for word in GLAZING_WORDS:
            pattern = rf"\b{re.escape(word)}\b"
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(f"Linha {idx}: Palavra desaconselhada detectada ('{word}'). Elimine adjetivos vazios/elogios.")
    return findings

def validate_heilmeier_compliance(content: str) -> dict:
    """Verifies if a spec answers the core Heilmeier Catechism dimensions."""
    results = {}
    missing = []
    for key, regex in HEILMEIER_QUESTIONS:
        matched = bool(regex.search(content))
        results[key] = matched
        if not matched:
            missing.append(key)
    return {
        "compliant": len(missing) == 0,
        "score": (len(HEILMEIER_QUESTIONS) - len(missing)) / len(HEILMEIER_QUESTIONS) * 100,
        "results": results,
        "missing": missing
    }

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 goldfish_review.py <caminho_do_documento.md>")
        sys.exit(1)

    doc_path = Path(sys.argv[1])
    if not doc_path.exists():
        print(f"Erro: Arquivo '{doc_path}' não encontrado.")
        sys.exit(1)

    content = doc_path.read_text(encoding="utf-8")
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

    # Return exit code based on compliance
    if not heilmeier["compliant"]:
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
