#!/usr/bin/env python3
"""scripts/policy_index.py — Índice compacto de políticas para injeção JIT.

O kit carrega AGENTS.md + PROJECT_MEMORY.md em todo turno (contexto base).
As políticas de `.agents/policies/` são indexadas em 1 linha cada (gatilho + resumo)
e o corpo inteiro só é carregado sob demanda via `xp context <query>` ou `xp policy show <id>`.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.kit_constants import POLICY_JIT_THRESHOLD_BYTES, kit_root

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
POLICY_TRIGGER_MAP: Dict[str, str] = {
    "architecture-and-persistence": "db, sql, migration, n+1, stdlib",
    "frontend-and-design-system": "ui, css, design, tokens, wcag",
    "memory-and-context": "memory, context, dead-ends, archive",
    "release-and-deployment": "release, deploy, rollback, canary",
    "security-and-zero-trust": "auth, security, stride, secrets, pii",
    "testing-and-quality": "tdd, atdd, test, spec, conformance",
    "token-economy": "token, budget, batch, debt, loop",
}
TRIGGER_HINTS = [
    "auth", "security", "billing", "payments", "migration", "terraform", "k8s",
    "docker", "ci", "release", "deploy", "database", "sql", "frontend",
    "design", "ui", "test", "tdd", "atdd", "token", "cache", "loop", "memory",
]


def _extract_first_summary(body: str) -> str:
    """Extrai resumo curto da primeira regra ou parágrafo útil do corpo Markdown."""
    headings: List[str] = []
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(">"):
            continue
        if s.startswith("## "):
            headings.append(re.sub(r"^##\s+\d+\.\s*", "", s).strip())
            if len(headings) >= 2:
                break
    if headings:
        return "; ".join(headings)
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">"):
            return " ".join(s.split())
    return ""


def _derive_trigger(text: str, policy_id: str = "") -> str:
    if policy_id in POLICY_TRIGGER_MAP:
        return POLICY_TRIGGER_MAP[policy_id]
    lower = f"{policy_id} {text}".lower()
    hits = [hint for hint in TRIGGER_HINTS if hint in lower]
    return ", ".join(hits[:4]) if hits else "geral"


def parse_policy(text: str, policy_id: str = "") -> Dict[str, str]:
    """Extrai título, gatilho e resumo de um arquivo de política (com ou sem frontmatter)."""
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else (text.splitlines()[0].lstrip("# ") if text.splitlines() else "política")
        return {
            "title": title,
            "trigger": _derive_trigger(text, policy_id),
            "summary": _extract_first_summary(text),
        }

    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            key, _, value = line.partition(":")
            key = key.strip()
            val = value.strip().strip("'\"")
            if val in (">-", ">", "|", "|-"):
                val = ""
            meta[key] = val
    body = text[match.end():]
    title = meta.get("title") or meta.get("name") or "política"
    trigger = meta.get("trigger") or _derive_trigger(body, policy_id)
    summary = meta.get("summary") or _extract_first_summary(body)
    return {"title": title, "trigger": trigger, "summary": summary}


def collect_policies(policies_dir: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in sorted(policies_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_policy(text, policy_id=path.stem)
        out.append({
            "id": path.stem,
            "path": path,
            "title": parsed["title"],
            "trigger": parsed["trigger"],
            "summary": parsed["summary"],
            "bytes": len(text.encode("utf-8")),
        })
    return out


def render_policy_index(policies: List[Dict[str, Any]]) -> str:
    total_kb = sum(p["bytes"] for p in policies) // 1024
    lines = [
        "# Políticas JIT (`xp policy show <id>` | `xp context <query>`)",
        f"> {len(policies)} políticas ({total_kb} KB total, carregadas sob demanda).",
        "",
        "| ID | Gatilho | Resumo |",
        "|---|---|---|",
    ]
    for policy in policies:
        summary = policy["summary"]
        if len(summary) > 68:
            summary = summary[:67] + "…"
        lines.append(f"| `{policy['id']}` | {policy['trigger']} | {summary} |")
    return "\n".join(lines) + "\n"


def write_policy_index(policies_dir: Path, output: Path) -> int:
    policies = collect_policies(policies_dir)
    if not policies:
        return 0
    content = render_policy_index(policies)
    output.write_text(content, encoding="utf-8")
    return len(policies)


def main() -> int:
    parser = argparse.ArgumentParser(description="Índice JIT de políticas do XP Kit")
    parser.add_argument("action", choices=["generate", "show", "list"])
    parser.add_argument("--dir", default=None, help="Diretório de políticas (padrão: .agents/policies)")
    parser.add_argument("--out", default=None, help="Saída para generate")
    parser.add_argument("policy_id", nargs="?", help="ID para show")
    args = parser.parse_args()

    root = kit_root()
    policies_dir = Path(args.dir) if args.dir else root / ".agents" / "policies"
    if not policies_dir.is_dir():
        print(f"❌ Diretório de políticas não encontrado: {policies_dir}", file=sys.stderr)
        return 1

    policies = collect_policies(policies_dir)

    if args.action == "generate":
        out = Path(args.out) if args.out else root / ".agents" / "policies" / "INDEX.md"
        count = write_policy_index(policies_dir, out)
        print(f"✅ {count} políticas indexadas em {out}")
        return 0
    if args.action == "list":
        for p in policies:
            jit = "JIT" if p["bytes"] > POLICY_JIT_THRESHOLD_BYTES else "fixo"
            print(f"[{jit:5}] {p['id']:<32} {p['bytes']:>5} B  {p['trigger']}")
        return 0
    if args.action == "show":
        target = next((p for p in policies if p["id"] == args.policy_id), None)
        if target:
            print(Path(target["path"]).read_text(encoding="utf-8"))
        else:
            print(f"❌ Política '{args.policy_id}' não encontrada", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
