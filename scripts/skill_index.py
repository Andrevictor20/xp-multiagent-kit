#!/usr/bin/env python3
"""
scripts/skill_index.py
Índice compacto de skills (A2), auditor de orçamento de contexto (A1/A2/A3/E4)
e fatiador mecânico de skills acima do teto (E4).

Problema resolvido: o catálogo de 74 skills é injetado no contexto em todo
turno. Um índice de 1 linha por skill custa uma fração disso, e as skills
gigantes (>SKILL_BODY_MAX_BYTES) passam a carregar só a seção necessária.

Uso:
    agy-skill-index generate            # grava .agents/skills/SKILLS_INDEX.md
    agy-skill-index audit               # relatório de orçamento do contexto base
    agy-skill-index split --dry-run     # mostra o que seria fatiado (E4)
    agy-skill-index split               # fatia skills acima do teto em sections/
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kit_constants import (  # noqa: E402
    AGENTS_MD_MAX_BYTES,
    MEMORY_INDEX_MAX_BYTES,
    SKILL_BODY_MAX_BYTES,
    SKILL_INDEX_LINE_MAX_CHARS,
    kit_root,
)

INDEX_FILE = "SKILLS_INDEX.md"
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SECTION_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Separa o frontmatter YAML simples do corpo da skill."""
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, text
    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    return meta, text[match.end():]


def slugify(title: str) -> str:
    """Slug estável e legível, com acentos normalizados (Seção → secao)."""
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    return slug or "secao"


def collect_skills(skills_dir: Path) -> List[Dict[str, Any]]:
    """Inventaria as skills com tamanho de corpo e descrição."""
    skills = []
    for path in sorted(skills_dir.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta, body = parse_frontmatter(text)
        skills.append({
            "name": meta.get("name") or path.parent.name,
            "dir": path.parent.name,
            "description": meta.get("description", ""),
            "body_bytes": len(body.encode("utf-8")),
            "total_bytes": len(text.encode("utf-8")),
            "path": path,
        })
    return skills


def render_index(skills: List[Dict[str, Any]], max_line_chars: int = SKILL_INDEX_LINE_MAX_CHARS) -> str:
    """
    Gera o índice compacto: 1 linha por skill (nome + gatilho truncado).
    É este arquivo que deve ser injetado no contexto, não os 74 SKILL.md.
    """
    lines = [
        "# Índice de Skills (carregamento sob demanda)",
        "",
        "> Catálogo compacto. O corpo de cada skill só entra no contexto quando ativada.",
        f"> {len(skills)} skills • teto por skill: {SKILL_BODY_MAX_BYTES // 1024} KB",
        "",
        "| Skill | Gatilho |",
        "|-------|---------|",
    ]
    for skill in skills:
        description = " ".join(skill["description"].split())
        if len(description) > max_line_chars:
            description = description[: max_line_chars - 1].rstrip() + "…"
        lines.append(f"| `{skill['dir']}` | {description or '—'} |")
    return "\n".join(lines) + "\n"


def split_skill(path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Fatia uma skill grande em sections/<slug>.md, mantendo SKILL.md como índice
    (frontmatter + introdução + ponteiros). O frontmatter original é preservado
    para que a IDE continue descobrindo a skill.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    frontmatter_match = FRONTMATTER_PATTERN.match(text)
    frontmatter = frontmatter_match.group(0) if frontmatter_match else ""
    body = text[len(frontmatter):]

    matches = list(SECTION_PATTERN.finditer(body))
    if len(matches) < 2:
        return {"skill": path.parent.name, "sections": 0, "skipped": "menos de 2 seções"}

    sections: List[Tuple[str, str]] = []
    intro = body[: matches[0].start()].strip()
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        title = match.group(1).strip()
        sections.append((title, body[match.start():end].rstrip()))

    if not dry_run:
        sections_dir = path.parent / "sections"
        sections_dir.mkdir(exist_ok=True)
        for title, content in sections:
            (sections_dir / f"{slugify(title)}.md").write_text(content + "\n", encoding="utf-8")

        index_lines = [frontmatter.rstrip(), "", intro, "", "## Seções (carregar sob demanda)", ""]
        for title, _ in sections:
            index_lines.append(f"- [{title}](sections/{slugify(title)}.md)")
        path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    return {
        "skill": path.parent.name,
        "sections": len(sections),
        "original_bytes": len(text.encode("utf-8")),
        "skipped": None,
    }


def audit_context_budget(root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Mede o contexto base pago em todo turno contra os tetos do kit.
    É o gate de regressão de bloat: nenhum PR pode aumentar esses números
    sem justificativa explícita.
    """
    base = root or kit_root()
    findings: List[Dict[str, Any]] = []

    agents_md = base / "AGENTS.md"
    if agents_md.is_file():
        size = agents_md.stat().st_size
        findings.append({
            "artifact": "AGENTS.md",
            "bytes": size,
            "budget": AGENTS_MD_MAX_BYTES,
            "over": max(0, size - AGENTS_MD_MAX_BYTES),
            "status": "OVER" if size > AGENTS_MD_MAX_BYTES else "OK",
        })

    memory = base / ".agents" / "memory" / "PROJECT_MEMORY.md"
    if memory.is_file():
        size = memory.stat().st_size
        findings.append({
            "artifact": "PROJECT_MEMORY.md",
            "bytes": size,
            "budget": MEMORY_INDEX_MAX_BYTES,
            "over": max(0, size - MEMORY_INDEX_MAX_BYTES),
            "status": "OVER" if size > MEMORY_INDEX_MAX_BYTES else "OK",
        })

    skills_dir = base / ".agents" / "skills"
    oversized = []
    catalog_bytes = 0
    if skills_dir.is_dir():
        for skill in collect_skills(skills_dir):
            catalog_bytes += min(skill["total_bytes"], 1200)
            if skill["body_bytes"] > SKILL_BODY_MAX_BYTES:
                oversized.append({
                    "skill": skill["dir"],
                    "body_bytes": skill["body_bytes"],
                    "over": skill["body_bytes"] - SKILL_BODY_MAX_BYTES,
                })

    index_path = skills_dir / INDEX_FILE
    findings.append({
        "artifact": "skills_catalog (injetado por turno)",
        "bytes": catalog_bytes,
        "budget": None,
        "over": 0,
        "status": "INFO",
        "index_exists": index_path.is_file(),
        "index_bytes": index_path.stat().st_size if index_path.is_file() else 0,
    })

    return {
        "findings": findings,
        "oversized_skills": oversized,
        "blocking": any(f["status"] == "OVER" for f in findings) or bool(oversized),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Índice e auditoria de skills do XP Kit")
    parser.add_argument("action", choices=["generate", "audit", "split"])
    parser.add_argument("--root", default=None, help="Raiz do projeto (padrão: raiz do kit)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=SKILL_BODY_MAX_BYTES)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    base = Path(args.root) if args.root else kit_root()
    skills_dir = base / ".agents" / "skills"
    if not skills_dir.is_dir():
        print(f"❌ Diretório de skills não encontrado: {skills_dir}", file=sys.stderr)
        return 1

    if args.action == "generate":
        index_path = skills_dir / INDEX_FILE
        content = render_index(collect_skills(skills_dir))
        if not args.dry_run:
            index_path.write_text(content, encoding="utf-8")
        print(f"{'[dry-run] ' if args.dry_run else ''}Índice gravado em {index_path} "
              f"({len(content.encode('utf-8'))} bytes)")
        return 0

    if args.action == "audit":
        report = audit_context_budget(base)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            for finding in report["findings"]:
                budget = finding["budget"] or "—"
                print(f"  {finding['status']:5} {finding['artifact']}: {finding['bytes']} bytes "
                      f"(orçamento: {budget})")
            for skill in report["oversized_skills"]:
                print(f"  OVER  skill {skill['skill']}: {skill['body_bytes']} bytes "
                      f"(+{skill['over']} acima do teto)")
        return 1 if report["blocking"] else 0

    # split
    results = []
    for skill in collect_skills(skills_dir):
        if skill["body_bytes"] > args.max_bytes:
            results.append(split_skill(skill["path"], dry_run=args.dry_run))
    if not results:
        print("Nenhuma skill acima do teto. Nada a fatiar.")
        return 0
    for result in results:
        mode = "[dry-run] " if args.dry_run else ""
        print(f"{mode}{result['skill']}: {result['sections']} seções "
              f"({result.get('original_bytes', 0)} bytes originais)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
