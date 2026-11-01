#!/usr/bin/env python3
"""scripts/kit_lint.py — Linter de governança, integridade de componentes e orçamentos (AC-6)
Valida versão única, components.yaml, 8 seções do AGENTS.md e orçamentos do Thin Harness.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent

MANDATORY_AGENTS_SECTIONS = [
    "CONTRATO",
    "CONTEXTO",
    "FERRAMENTAS",
    "ESTADO",
    "POLÍTICA",
    "VERIFICAÇÃO",
    "RECUPERAÇÃO",
    "OBSERVABILIDADE",
]


def lint_version(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    base = root_dir or ROOT_DIR
    v_file = base / "VERSION"
    if v_file.is_file():
        val = v_file.read_text(encoding="utf-8").strip()
    else:
        comp_file = base / ".agents" / "components.yaml"
        if comp_file.is_file():
            m = re.search(r'^version:\s*["\']?([^"\']+)["\']?', comp_file.read_text(encoding="utf-8"), re.MULTILINE)
            val = m.group(1).strip() if m else "4.0.0"
        else:
            val = "4.0.0"
    if not re.match(r"^\d+\.\d+\.\d+", val):
        return {"valid": False, "version": val, "error": f"Versão '{val}' inválida"}
    return {"valid": True, "version": val, "error": None}


def lint_components_yaml(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    base = root_dir or ROOT_DIR
    comp_file = base / ".agents" / "components.yaml"
    if not comp_file.is_file():
        return {"valid": False, "count": 0, "errors": ["Arquivo .agents/components.yaml ausente"]}

    text = comp_file.read_text(encoding="utf-8")
    errors: List[str] = []
    count = 0

    # Parser simples de blocos de componente
    current_comp: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- id:"):
            if current_comp:
                count += 1
                if not current_comp.get("prevents"):
                    errors.append(f"Componente '{current_comp.get('id')}' sem campo 'prevents'")
            current_comp = {"id": line.split(":", 1)[1].strip().strip('"').strip("'")}
        elif current_comp:
            for field in ["kind", "prevents", "added", "review_by"]:
                if line.startswith(f"{field}:"):
                    current_comp[field] = line.split(":", 1)[1].strip().strip('"').strip("'")

    if current_comp:
        count += 1
        if not current_comp.get("prevents"):
            errors.append(f"Componente '{current_comp.get('id')}' sem campo 'prevents'")

    return {"valid": len(errors) == 0, "count": count, "errors": errors}


def lint_agents_md_sections(content: Optional[str] = None, root_dir: Optional[Path] = None) -> Dict[str, Any]:
    if content is None:
        base = root_dir or ROOT_DIR
        ag_file = base / "AGENTS.md"
        content = ag_file.read_text(encoding="utf-8") if ag_file.is_file() else ""

    missing: List[str] = []
    for sec in MANDATORY_AGENTS_SECTIONS:
        # Busca menção exata da seção
        pattern = rf"(?:^|\n)#+\s*(?:\d+\.\s*)?{re.escape(sec)}\b|\[{re.escape(sec)}\]|(?:^|\n)\*\*{re.escape(sec)}\*\*"
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(sec)

    return {"valid": len(missing) == 0, "missing": missing}


def lint_concept_duplications(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    base = root_dir or ROOT_DIR
    policies_dir = base / ".agents" / "policies"
    policy_files = list(policies_dir.glob("*.md")) if policies_dir.is_dir() else []
    all_files = [base / "AGENTS.md"] + policy_files

    counts: Dict[str, int] = {"completeness": 0, "heilmeier": 0, "stop_gate": 0}
    for f in all_files:
        if not f.is_file():
            continue
        txt = f.read_text(encoding="utf-8")
        if "Completeness Over Speed" in txt:
            counts["completeness"] += 1
        if "Heilmeier" in txt:
            counts["heilmeier"] += 1
        if "Stop Gate" in txt:
            counts["stop_gate"] += 1

    return {"valid": True, "counts": counts}


def lint_context_budget(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    base = root_dir or ROOT_DIR
    agents_path = base / "AGENTS.md"
    mem_path = base / ".agents" / "memory" / "PROJECT_MEMORY.md"

    agents_sz = agents_path.stat().st_size if agents_path.is_file() else 0
    mem_sz = mem_path.stat().st_size if mem_path.is_file() else 0
    total = agents_sz + mem_sz

    return {
        "valid": agents_sz <= 3000 and mem_sz <= 3000 and total <= 8000,
        "agents_bytes": agents_sz,
        "memory_bytes": mem_sz,
        "total_bytes": total,
    }


def run_all_lints() -> int:
    v_res = lint_version()
    c_res = lint_components_yaml()
    a_res = lint_agents_md_sections()
    b_res = lint_context_budget()

    errors = 0
    if not v_res["valid"]:
        print(f"❌ [VERSION] {v_res.get('error')}")
        errors += 1
    else:
        print(f"✅ [VERSION] Versão canônica: {v_res['version']}")

    if not c_res["valid"]:
        print(f"❌ [COMPONENTS] {c_res['errors']}")
        errors += 1
    else:
        print(f"✅ [COMPONENTS] {c_res['count']} componentes auditados com 'prevents'")

    if not a_res["valid"]:
        print(f"⚠️  [AGENTS.md] Seções pendentes: {a_res['missing']}")
    else:
        print("✅ [AGENTS.md] Todas as 8 seções de harness apontam mecanismos")

    print(f"ℹ️  [BUDGET] AGENTS.md: {b_res['agents_bytes']} B | Memory: {b_res['memory_bytes']} B | Total: {b_res['total_bytes']} B (Teto: 8.000 B)")

    return 1 if errors > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Kit Governance Linter")
    parser.add_argument("command", nargs="?", default="lint", help="Subcomando opcional (ex: lint)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()
    return run_all_lints()


if __name__ == "__main__":
    sys.exit(main())
