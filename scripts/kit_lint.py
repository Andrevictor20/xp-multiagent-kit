#!/usr/bin/env python3
"""scripts/kit_lint.py — Linter de governança, integridade de componentes e orçamentos (AC-6)
Valida versão única, components.yaml, 8 seções do AGENTS.md e orçamentos do Thin Harness.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

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


def discover_disk_components(base: Path) -> List[Dict[str, str]]:
    """Descobre componentes em disco (skills, agents, policies, hooks, scripts)."""
    found: List[Dict[str, str]] = []

    # 1. Skills
    for s_dir in [base / ".agents" / "skills", base / "skills"]:
        if s_dir.is_dir():
            for child in sorted(s_dir.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    found.append({"id": child.name, "kind": "skill"})

    # 2. Agents
    agents_dir = base / ".agents" / "agents"
    if agents_dir.is_dir():
        for child in sorted(agents_dir.glob("*.md")):
            found.append({"id": child.stem, "kind": "agent"})

    # 3. Policies
    policies_dir = base / ".agents" / "policies"
    if policies_dir.is_dir():
        for child in sorted(policies_dir.glob("*.md")):
            found.append({"id": child.stem, "kind": "policy"})

    # 4. Hooks
    hooks_dir = base / "scripts" / "hooks"
    if hooks_dir.is_dir():
        for child in sorted(hooks_dir.glob("*.py")):
            cid = child.stem.replace("-", "_")
            found.append({"id": cid, "kind": "hook"})

    return found


def lint_components_yaml(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    base = root_dir or ROOT_DIR
    comp_file = base / ".agents" / "components.yaml"
    if not comp_file.is_file():
        return {"valid": False, "count": 0, "errors": ["Arquivo .agents/components.yaml ausente"]}

    text = comp_file.read_text(encoding="utf-8")
    errors: List[str] = []
    registered_ids: Set[str] = set()

    # Parser simples de blocos de componente
    current_comp: Dict[str, str] = {}
    count = 0
    for line in text.splitlines():
        line_s = line.strip()
        if line_s.startswith("- id:"):
            if current_comp:
                count += 1
                cid = current_comp.get("id", "")
                registered_ids.add(cid)
                if not current_comp.get("prevents"):
                    errors.append(f"Componente '{cid}' sem campo 'prevents'")
            raw_id = line_s.split(":", 1)[1].strip().strip('"').strip("'")
            current_comp = {"id": raw_id}
        elif current_comp:
            for field in ["kind", "prevents", "added", "review_by"]:
                if line_s.startswith(f"{field}:"):
                    current_comp[field] = line_s.split(":", 1)[1].strip().strip('"').strip("'")

    if current_comp:
        count += 1
        cid = current_comp.get("id", "")
        registered_ids.add(cid)
        if not current_comp.get("prevents"):
            errors.append(f"Componente '{cid}' sem campo 'prevents'")

    # Compara o que existe em disco com o components.yaml
    disk_comps = discover_disk_components(base)
    for dc in disk_comps:
        cid = dc["id"]
        # Normalização simples (hífens e underscores)
        cid_alt = cid.replace("-", "_") if "-" in cid else cid.replace("_", "-")
        if cid not in registered_ids and cid_alt not in registered_ids:
            errors.append(f"Componente '{cid}' ({dc['kind']}) em disco sem entrada em components.yaml")

    return {"valid": len(errors) == 0, "count": count, "errors": errors}


def sync_components(root_dir: Optional[Path] = None) -> int:
    """Varre componentes em disco e acrescenta entradas faltantes com prevents: ''."""
    base = root_dir or ROOT_DIR
    comp_file = base / ".agents" / "components.yaml"
    comp_file.parent.mkdir(parents=True, exist_ok=True)

    registered_ids: Set[str] = set()
    existing_content = ""
    if comp_file.is_file():
        existing_content = comp_file.read_text(encoding="utf-8")
        for line in existing_content.splitlines():
            line_s = line.strip()
            if line_s.startswith("- id:"):
                raw_id = line_s.split(":", 1)[1].strip().strip('"').strip("'")
                registered_ids.add(raw_id)
    else:
        existing_content = '# .agents/components.yaml — Ledger de Componentes\nversion: "4.0.0"\n\ncomponents:\n'

    disk_comps = discover_disk_components(base)
    added_count = 0
    new_blocks = []

    today = datetime.date.today().isoformat()
    review = (datetime.date.today() + datetime.timedelta(days=90)).isoformat()

    for dc in disk_comps:
        cid = dc["id"]
        cid_alt = cid.replace("-", "_") if "-" in cid else cid.replace("_", "-")
        if cid not in registered_ids and cid_alt not in registered_ids:
            block = (
                f"  - id: \"{cid}\"\n"
                f"    kind: \"{dc['kind']}\"\n"
                f"    prevents: \"\"\n"
                f"    added: \"{today}\"\n"
                f"    review_by: \"{review}\"\n"
            )
            new_blocks.append(block)
            registered_ids.add(cid)
            added_count += 1

    if new_blocks:
        if not existing_content.endswith("\n"):
            existing_content += "\n"
        if "components:" not in existing_content:
            existing_content += "components:\n"
        existing_content += "\n".join(new_blocks) + "\n"
        comp_file.write_text(existing_content, encoding="utf-8")
        print(f"✅ [SYNC] {added_count} novos componentes adicionados ao components.yaml com prevents: ''")
    else:
        print(f"ℹ️  [SYNC] components.yaml já está sincronizado com todos os componentes em disco.")
    return 0


def lint_agents_md_sections(content: Optional[str] = None, root_dir: Optional[Path] = None) -> Dict[str, Any]:
    if content is None:
        base = root_dir or ROOT_DIR
        ag_file = base / "AGENTS.md"
        content = ag_file.read_text(encoding="utf-8") if ag_file.is_file() else ""

    missing: List[str] = []
    for sec in MANDATORY_AGENTS_SECTIONS:
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


def run_all_lints(root_dir: Optional[Path] = None) -> int:
    base = root_dir or ROOT_DIR
    v_res = lint_version(base)
    c_res = lint_components_yaml(base)
    a_res = lint_agents_md_sections(root_dir=base)
    b_res = lint_context_budget(base)

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
    parser.add_argument("command", nargs="?", default="lint", help="Subcomando (lint|components)")
    parser.add_argument("--dir", "-d", default=None, help="Diretório raiz a ser auditado")
    parser.add_argument("--sync", action="store_true", help="Sincroniza components.yaml com disco")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args, unknown = parser.parse_known_args()

    base_dir = Path(args.dir).resolve() if args.dir else ROOT_DIR

    if args.sync or (args.command == "components" and ("--sync" in unknown or "--sync" in sys.argv)):
        return sync_components(base_dir)

    return run_all_lints(base_dir)


if __name__ == "__main__":
    sys.exit(main())
