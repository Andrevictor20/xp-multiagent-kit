#!/usr/bin/env python3
"""scripts/policy_index.py — Índice compacto de políticas para injeção JIT.

O kit carrega AGENTS.md + PROJECT_MEMORY.md em todo turno (contexto base).
As 7 políticas de `.agents/policies/` não deveriam ser injetadas integralmente:
o custo fixo era ~9.2 KB. Este índice tem uma linha por política
(gatilho + resumo) e o corpo inteiro só é carregado por gatilho
via `xp context <query>`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.kit_constants import POLICY_JIT_THRESHOLD_BYTES, kit_root  # noqa: E402

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TRIGGER_HINTS = [
    "auth", "security", "billing", "payments", "migration", "terraform", "k8s",
    "docker", "ci", "release", "deploy", "database", "sql", "frontend",
    "design", "ui", "test", "tdd", "atdd", "token", "cache", "loop", "memory",
]


def parse_policy(text: str) -> Dict[str, str]:
    """Extrai título, gatilho e resumo de um arquivo de política."""
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        # Fallback: usa o cabeçalho H1
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else text.splitlines()[0].lstrip("# ")
        return {"title": title, "trigger": "geral", "summary": ""}

    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            key, _, value = line.partition(":")
            key = key.strip()
            val = value.strip().strip("'\"")
            if val in (">-", ">", "|", "|-"):
                val = ""
            meta[key] = val
    title = meta.get("title") or meta.get("name") or "política"
    trigger = meta.get("trigger") or "geral"
    summary = meta.get("summary", "")
    if not summary:
        body = text[match.end():]
        for line in body.splitlines():
            if line.strip() and not line.startswith("#"):
                summary = " ".join(line.split())
                break
    if not trigger or trigger == "geral":
        trigger = _derive_trigger(text)
    return {"title": title, "trigger": trigger, "summary": summary}


def _derive_trigger(text: str) -> str:
    lower = text.lower()
    for hint in TRIGGER_HINTS:
        if hint in lower:
            return hint
    return "geral"


def collect_policies(policies_dir: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in sorted(policies_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_policy(text)
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
    lines = [
        "# Políticas do XP Kit (JIT Loading)",
        "",
        "> Carregue uma política completa com `xp context <query>` ou `xp policy show <id>`.",
        f"> {len(policies)} políticas indexadas • total integral: "
        f"{sum(p['bytes'] for p in policies) // 1024} KB • injetado: {len(policies) * 60} B.",
        "",
        "| ID | Gatilho | Resumo | Bytes |",
        "|----|---------|--------|-------|",
    ]
    for policy in policies:
        summary = policy["summary"]
        if len(summary) > 80:
            summary = summary[:79] + "…"
        lines.append(f"| `{policy['id']}` | {policy['trigger']} | {summary} | {policy['bytes']} |")
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
            print(f"[{jit:5}] {p['id']:<35} {p['bytes']:>6} B  {p['trigger']}")
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
