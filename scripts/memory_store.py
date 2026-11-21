#!/usr/bin/env python3
"""scripts/memory_store.py — Memória Multi-Repositório com Escopos (user: / repo: / session:)
e auto-consolidação determinística inspirada nos escopos e MemoryBank do Google ADK.
100% Python stdlib, sem aumento de contexto fixo por turno (user: é puramente JIT).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.memory_archiver import archive_memory
from scripts.xp_contract import load_contract

USER_MEMORY_TEMPLATE = """# User Memory — XP Multi-Agent Kit (Cross-Repo)

## 1. PREFERÊNCIAS & PADRÕES GLOBAIS
- Respostas ao usuário em Português (PT-BR).

## 2. DECISÕES UNIVERSAIS

## 4. LIÇÕES & REGRAS 'NEVER'
"""

GLOBAL_DEAD_ENDS_TEMPLATE = """# Global Dead-Ends — XP Multi-Agent Kit (Cross-Repo)

## 5. TENTATIVAS QUE FALHARAM (DEAD-ENDS)
"""

CATEGORY_SECTION_PATTERNS: Dict[str, List[str]] = {
    "dead_end": [r"^##\s+\d+\.\s+[^\n]*(?:DEAD-END|FALHARAM)[^\n]*$", r"^##\s+5\.[^\n]*$"],
    "never": [r"^##\s+\d+\.\s+[^\n]*(?:NEVER|LIÇÕES|PROCEDURAL)[^\n]*$", r"^##\s+4\.[^\n]*$"],
    "lesson": [r"^##\s+\d+\.\s+[^\n]*(?:LIÇÕES|NEVER|PROCEDURAL)[^\n]*$", r"^##\s+4\.[^\n]*$"],
    "decision": [r"^##\s+\d+\.\s+[^\n]*(?:DECIS|ARCHITECTURAL)[^\n]*$", r"^##\s+2\.[^\n]*$"],
}


def get_user_memory_dir(override: Optional[Path] = None) -> Path:
    if override is not None:
        return Path(override).expanduser().resolve()
    env_dir = os.environ.get("XP_USER_MEMORY_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / ".xp-kit" / "memory").resolve()


def ensure_user_memory(user_dir: Optional[Path] = None) -> Path:
    base = get_user_memory_dir(user_dir)
    base.mkdir(parents=True, exist_ok=True)
    user_mem = base / "USER_MEMORY.md"
    if not user_mem.is_file():
        user_mem.write_text(USER_MEMORY_TEMPLATE, encoding="utf-8")
    dead_ends = base / "GLOBAL_DEAD_ENDS.md"
    if not dead_ends.is_file():
        dead_ends.write_text(GLOBAL_DEAD_ENDS_TEMPLATE, encoding="utf-8")
    return base


def _norm_fingerprint(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", re.sub(r"[`*_#\[\]-]+", " ", text.lower())).strip()
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]


def _already_present(doc: str, text: str) -> bool:
    target_fp = _norm_fingerprint(text)
    if text.strip().lower() in doc.lower():
        return True
    for line in doc.splitlines():
        s = line.strip()
        if s.startswith(("- ", "* ")):
            candidate = re.sub(r"^[-*]\s+(?:`never`\s+)?(?:\[\d{4}-\d{2}-\d{2}\]\s+)?", "", s)
            if _norm_fingerprint(candidate) == target_fp:
                return True
    return False


def _format_entry(text: str, category: str) -> str:
    clean = " ".join(text.strip().split())
    if category == "never":
        if clean.lower().startswith("`never`") or clean.lower().startswith("never "):
            return f"- {clean}"
        return f"- `never` {clean}"
    if category == "dead_end":
        today = datetime.date.today().isoformat()
        return f"- [{today}] {clean}"
    return f"- {clean}"


def _insert_into_section(doc: str, entry_line: str, category: str) -> str:
    patterns = CATEGORY_SECTION_PATTERNS.get(category, CATEGORY_SECTION_PATTERNS["lesson"])
    for pat in patterns:
        match = re.search(pat, doc, re.IGNORECASE | re.MULTILINE)
        if match:
            after = doc[match.end():]
            # Remove placeholder line if it's the only entry under Dead-Ends
            placeholder = re.search(r"^\s*-\s*Nenhum dead-end registrado[^\n]*\n?", after, re.IGNORECASE | re.MULTILINE)
            if category == "dead_end" and placeholder and placeholder.start() < 120:
                after = after[: placeholder.start()] + after[placeholder.end():]
            return doc[: match.end()] + "\n" + entry_line + after
    sep = "" if doc.endswith("\n") else "\n"
    return f"{doc}{sep}\n{entry_line}\n"


def promote_memory(
    text: str,
    scope: str = "repo",
    category: str = "lesson",
    workspace: Optional[Path] = None,
    user_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Promove um fato, decisão, lição, regra never ou dead-end para repo: ou user: com dedup."""
    if scope not in ("repo", "user"):
        raise ValueError(f"Escopo inválido: {scope!r}. Use 'repo' ou 'user'.")
    if category not in ("lesson", "decision", "never", "dead_end"):
        raise ValueError(f"Categoria inválida: {category!r}.")

    if scope == "user":
        u_dir = ensure_user_memory(user_dir)
        target_file = (u_dir / "GLOBAL_DEAD_ENDS.md") if category == "dead_end" else (u_dir / "USER_MEMORY.md")
    else:
        ws = (workspace or Path.cwd()).resolve()
        target_file = ws / ".agents" / "memory" / "PROJECT_MEMORY.md"
        if not target_file.is_file():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(
                "# Project Memory\n\n## 2. DECISÕES\n\n## 3. PROGRESSO\n\n"
                "## 4. LIÇÕES & REGRAS 'NEVER'\n\n## 5. TENTATIVAS QUE FALHARAM (DEAD-ENDS)\n",
                encoding="utf-8",
            )

    content = target_file.read_text(encoding="utf-8")
    if _already_present(content, text):
        return {"added": False, "duplicate": True, "scope": scope, "category": category, "file": str(target_file)}

    entry = _format_entry(text, category)
    updated = _insert_into_section(content, entry, category)
    target_file.write_text(updated, encoding="utf-8")
    return {"added": True, "duplicate": False, "scope": scope, "category": category, "file": str(target_file), "entry": entry}


def consolidate_session_memory(
    workspace: Optional[Path] = None,
    user_dir: Optional[Path] = None,
    promote_global: bool = False,
) -> Dict[str, Any]:
    """Consolida dead-ends (`tried[]`) e regras `never[]` do run.json na memória durável."""
    ws = (workspace or Path.cwd()).resolve()
    contract = load_contract()
    scope = "user" if promote_global else "repo"

    dead_ends_added = 0
    never_added = 0

    for item in contract.get("tried", []):
        if isinstance(item, dict):
            sig = item.get("signature", "failure")
            reason = item.get("reason", "")
            text = f"`{sig}`: {reason}".strip(": ")
        else:
            text = str(item)
        if text:
            res = promote_memory(text, scope=scope, category="dead_end", workspace=ws, user_dir=user_dir)
            if res["added"]:
                dead_ends_added += 1

    for rule in contract.get("never", []):
        if str(rule).strip():
            res = promote_memory(str(rule), scope=scope, category="never", workspace=ws, user_dir=user_dir)
            if res["added"]:
                never_added += 1

    proj_mem = ws / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if scope == "repo" and proj_mem.is_file():
        archive_memory(proj_mem, max_bytes=3000)

    return {
        "scope": scope,
        "dead_ends_added": dead_ends_added,
        "never_added": never_added,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="XP Multi-Repo Scoped Memory Store (user:/repo:/session:)")
    sub = parser.add_subparsers(dest="action")

    p_prom = sub.add_parser("promote", help="Promove uma entrada para memória repo: ou user:")
    p_prom.add_argument("text", help="Texto da lição, decisão, regra never ou dead-end")
    p_prom.add_argument("--scope", choices=["repo", "user"], default="repo")
    p_prom.add_argument("--category", choices=["lesson", "decision", "never", "dead_end"], default="lesson")
    p_prom.add_argument("--workspace", default=".")

    p_cons = sub.add_parser("consolidate", help="Consolida run.json (tried[]/never[]) na memória durável")
    p_cons.add_argument("--global", dest="promote_global", action="store_true", help="Promover para escopo user: global")
    p_cons.add_argument("--workspace", default=".")

    args = parser.parse_args(argv)
    if args.action == "promote":
        res = promote_memory(args.text, scope=args.scope, category=args.category, workspace=Path(args.workspace))
        status = "Promovido" if res["added"] else "Já existente (deduplicado)"
        print(f"✅ [{res['scope'].upper()}|{res['category']}] {status}: {res['file']}")
        return 0
    if args.action == "consolidate":
        res = consolidate_session_memory(workspace=Path(args.workspace), promote_global=args.promote_global)
        print(
            f"✅ Consolidação ({res['scope']}): "
            f"+{res['dead_ends_added']} dead-end(s), +{res['never_added']} regra(s) never."
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
