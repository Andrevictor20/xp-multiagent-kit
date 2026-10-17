#!/usr/bin/env python3
"""
scripts/spec_tool.py — ATDD & BDD Specification CLI (xp-spec / agy-spec)
XP Multi-Agent Kit v3.1

Subcommands:
    xp-spec new <feature-name>       # Scaffolds .agents/specs/SPEC-NNN-<name>.md
    xp-spec validate <spec-file>     # Validates ACs, SbE tables, and Gherkin scenarios
    xp-spec matrix <spec-file>       # Previews the AC -> test traceability matrix
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

AC_PATTERN = re.compile(r"^###\s+AC-\d+:\s*(.+)$", re.MULTILINE)
TABLE_PATTERN = re.compile(r"^\|.+\|\s*\n\|[-:\|\s]+\|\s*\n(\|.+\|\s*\n)+", re.MULTILINE)
GHERKIN_PATTERN = re.compile(r"(Scenario|Cenário|Given|Dado|When|Quando|Then|Então)", re.IGNORECASE)


def find_next_spec_id(specs_dir: Path) -> str:
    """Finds the next incremental SPEC ID (e.g. 004)."""
    existing_ids = []
    if specs_dir.is_dir():
        for f in specs_dir.glob("SPEC-*.md"):
            m = re.match(r"SPEC-(\d+)", f.name)
            if m:
                existing_ids.append(int(m.group(1)))
    next_num = max(existing_ids, default=0) + 1
    return f"{next_num:03d}"


def scaffold_spec(spec_file: Path, title: str) -> Path:
    """Scaffolds a new ATDD specification document from template or canonical fallback."""
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    template_path = ROOT_DIR / ".agents" / "templates" / "SPEC-NNN-ATDD.md"

    if template_path.is_file():
        raw = template_path.read_text(encoding="utf-8")
        raw = raw.replace("{{FEATURE_TITLE}}", title)
        raw = raw.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
        raw = raw.replace("SPEC-NNN", spec_file.stem)
        spec_file.write_text(raw, encoding="utf-8")
        return spec_file

    canonical = f"""# {spec_file.stem}: {title}

> **Status:** DRAFT (Awaiting Stop Gate approval)  
> **Risk:** L2 (Feature)  
> **Date:** {datetime.now().strftime("%Y-%m-%d")}  

---

## 1. Context & Business Problem
Why is this feature required and what is the expected behavioral contract?

---

## 2. Acceptance Criteria (Contract)

### AC-1: Successful Execution
- **Given:** valid input and authenticated user
- **When:** action is triggered
- **Then:** state updates and return 200/OK
- **Metric:** deterministic output

### AC-2: Error Handling & Invariant Enforcement
- **Given:** invalid or missing input
- **When:** action is triggered
- **Then:** returns structured error without side effects

---

## 3. Specification by Example (SbE)

| Input | Precondition | Action | Expected Output | Status |
|-------|--------------|--------|-----------------|--------|
| valid_case | active | execute | success | Happy Path |
| empty_case | active | execute | validation_error | Boundary |

---

## 4. BDD / Gherkin Scenarios

### Scenario 1: Happy Path
Given an initialized environment
When execution starts
Then all assertions pass cleanly
"""
    spec_file.write_text(canonical, encoding="utf-8")
    return spec_file


def validate_spec_content(content: str) -> Tuple[bool, List[str]]:
    """Validates that a specification document contains mandatory ATDD/BDD sections."""
    errors = []
    if "Acceptance Criteria" not in content and "Critérios de Aceite" not in content:
        errors.append("Missing 'Acceptance Criteria' section.")

    acs = AC_PATTERN.findall(content)
    if not acs:
        errors.append("No '### AC-N:' items found in Acceptance Criteria section.")

    if not TABLE_PATTERN.search(content):
        errors.append("Missing markdown table for Specification by Example (SbE).")

    if not GHERKIN_PATTERN.search(content):
        errors.append("Missing BDD Gherkin scenarios (Given/When/Then).")

    return (len(errors) == 0, errors)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="XP Multi-Agent Kit — ATDD/BDD Specification CLI (xp-spec)")
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")

    new_p = subparsers.add_parser("new", help="Scaffold a new ATDD spec")
    new_p.add_argument("name", help="Feature name or slug (e.g. user-auth)")
    new_p.add_argument("--dir", default=".agents/specs", help="Target specs directory")

    val_p = subparsers.add_parser("validate", help="Validate an existing ATDD spec")
    val_p.add_argument("spec_file", help="Path to SPEC-*.md")

    args = parser.parse_args(argv)

    if args.subcommand == "new":
        specs_dir = Path(args.dir)
        next_id = find_next_spec_id(specs_dir)
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", args.name).strip("-").upper()
        target_file = specs_dir / f"SPEC-{next_id}-{slug}.md"
        scaffold_spec(target_file, args.name)
        print(f"✅ Specification created at {target_file}")
        return 0

    if args.subcommand == "validate":
        spec_path = Path(args.spec_file)
        if not spec_path.is_file():
            print(f"❌ File not found: {spec_path}", file=sys.stderr)
            return 1
        content = spec_path.read_text(encoding="utf-8")
        valid, errors = validate_spec_content(content)
        if valid:
            print(f"✅ Specification {spec_path.name} is COMPLIANT with ATDD/BDD standards.")
            return 0
        print(f"❌ Specification {spec_path.name} is NON-COMPLIANT:", file=sys.stderr)
        for err in errors:
            print(f"   • {err}", file=sys.stderr)
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
