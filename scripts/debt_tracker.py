#!/usr/bin/env python3
"""
debt_tracker.py — Rastreador e auditor de débitos técnicos in-code (agy-debt)

Varre o código-fonte em busca de convenções de simplificações e atalhos deliberados:
    // debt: <teto da simplificação>, <gatilho para refatorar>
    # debt: <teto>, <gatilho>
    /* debt: <teto>, <gatilho> */
    <!-- debt: <teto>, <gatilho> -->

Sinaliza itens sem gatilho de upgrade como [NO-TRIGGER] (risco de apodrecimento / rot risk),
e suporta sincronização automática com a Seção 7 do PROJECT_MEMORY.md.
"""

from dataclasses import asdict, dataclass
import json
import os
import re
import sys
from typing import List, Optional

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    ".gemini",
    "brain",
    "target",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".agents/runtime",
}

IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bin",
    ".exe",
    ".so",
    ".dylib",
    ".woff",
    ".woff2",
    ".ttf",
}

DEBT_REGEX = re.compile(
    r"(?:#|//|/\*|<!--)\s*debt:\s*(.*?)(?:\*/|-->|\n|$)",
    re.IGNORECASE,
)


@dataclass
class DebtItem:
    file_path: str
    line_number: int
    raw_comment: str
    ceiling: str
    trigger: Optional[str]
    has_trigger: bool


def parse_debt_line(file_path: str, line_number: int, line: str) -> Optional[DebtItem]:
    """Analisa uma linha em busca de um marcador de débito técnico."""
    match = DEBT_REGEX.search(line)
    if not match:
        return None

    raw_text = match.group(1).strip()
    if not raw_text:
        return None

    # O formato convencional é: <teto da simplificação>, <gatilho de upgrade>
    if "," in raw_text:
        parts = raw_text.split(",", 1)
        ceiling = parts[0].strip()
        trigger = parts[1].strip() if parts[1].strip() else None
        has_trigger = trigger is not None
    else:
        ceiling = raw_text
        trigger = None
        has_trigger = False

    return DebtItem(
        file_path=file_path,
        line_number=line_number,
        raw_comment=line.strip(),
        ceiling=ceiling,
        trigger=trigger,
        has_trigger=has_trigger,
    )


def scan_debt_markers(root_dir: str = ".") -> List[DebtItem]:
    """Varre recursivamente o diretório em busca de marcadores de débito."""
    items: List[DebtItem] = []

    for root, dirs, files in os.walk(root_dir):
        # Filtra diretórios ignorados
        dirs[:] = [
            d
            for d in dirs
            if d not in IGNORED_DIRS
            and not os.path.relpath(os.path.join(root, d), root_dir).replace("\\", "/").startswith(tuple(IGNORED_DIRS))
        ]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in IGNORED_EXTENSIONS:
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, root_dir).replace("\\", "/")

            # Pula arquivos dentro de diretórios ignorados
            if any(ignored in rel_path.split("/") for ignored in IGNORED_DIRS):
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        item = parse_debt_line(rel_path, line_num, line)
                        if item:
                            items.append(item)
            except (IOError, OSError):
                continue

    return items


def format_debt_report(items: List[DebtItem]) -> str:
    """Formata o relatório textual para exibição no terminal."""
    if not items:
        return "Nenhum débito técnico encontrado. Ledger limpo."

    lines = [
        "═══════════════════════════════════════════════════════════════════════════",
        " 📋 LEDGER DE DÉBITOS TÉCNICOS & SIMPLIFICAÇÕES AUDITÁVEIS (agy-debt)",
        "═══════════════════════════════════════════════════════════════════════════",
    ]

    no_trigger_count = 0
    for item in items:
        status_tag = "✅ [TRIGGER-OK]" if item.has_trigger else "⚠️ [NO-TRIGGER]"
        if not item.has_trigger:
            no_trigger_count += 1

        trigger_text = f"gatilho: {item.trigger}" if item.has_trigger else "sem gatilho de upgrade (risco de rot)"
        lines.append(f"• {item.file_path}:{item.line_number} {status_tag}")
        lines.append(f"  ├─ Teto: {item.ceiling}")
        lines.append(f"  └─ {trigger_text}")

    lines.append("───────────────────────────────────────────────────────────────────────────")
    lines.append(f"📊 Resumo: Total de débitos: {len(items)} | {no_trigger_count} em risco de apodrecimento (no-trigger)")
    if no_trigger_count > 0:
        lines.append("💡 Dica: Adicione um gatilho após a vírgula: // debt: <teto>, <quando refatorar>")
    lines.append("═══════════════════════════════════════════════════════════════════════════")

    return "\n".join(lines)


def sync_memory_debt_section(memory_file: str, items: List[DebtItem]) -> bool:
    """Sincroniza os itens de débito na Seção 7 do PROJECT_MEMORY.md."""
    if not os.path.exists(memory_file):
        return False

    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            content = f.read()

        section_header = "## 7. Technical Debts & Known Blockers"
        if section_header not in content:
            return False

        debt_lines = [f"{section_header}\n"]
        if not items:
            debt_lines.append(
                "- **Nenhum bloqueio ou débito in-code ativo.** Ledger limpo auditado via `agy-debt`.\n"
            )
        else:
            debt_lines.append(f"- **Débitos Técnicos Auditados ({len(items)} itens ativos):**\n")
            for item in items:
                trigger_str = f" | gatilho: `{item.trigger}`" if item.has_trigger else " | ⚠️ `NO-TRIGGER`"
                debt_lines.append(f"  - [`{item.file_path}:{item.line_number}`] {item.ceiling}{trigger_str}\n")

        # Substitui a seção até o próximo header ou fim do arquivo
        pattern = re.compile(rf"{re.escape(section_header)}.*?(?=\n## |\Z)", re.DOTALL)
        new_content = pattern.sub("".join(debt_lines), content)

        with open(memory_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True
    except (IOError, OSError):
        return False


def main(argv=None) -> int:
    """Ponto de entrada do CLI agy-debt."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Rastreador e auditor de débitos técnicos in-code (agy-debt)"
    )
    parser.add_argument("--dir", default=".", help="Diretório raiz da varredura (default: .)")
    parser.add_argument("--scan", action="store_true", help="Executa a varredura e exibe o relatório")
    parser.add_argument("--json", action="store_true", help="Emite o resultado em formato JSON estruturado")
    parser.add_argument("--export", help="Exporta o relatório em formato Markdown para o caminho indicado")
    parser.add_argument(
        "--fail-on-no-trigger",
        action="store_true",
        help="Retorna código de erro 1 se houver débitos sem gatilho de upgrade",
    )
    parser.add_argument(
        "--sync-memory",
        nargs="?",
        const=".agents/memory/PROJECT_MEMORY.md",
        help="Sincroniza os débitos encontrados diretamente no PROJECT_MEMORY.md",
    )

    args = parser.parse_args(argv)

    items = scan_debt_markers(args.dir)
    no_trigger_count = sum(1 for item in items if not item.has_trigger)

    if args.json:
        payload = {
            "total_debts": len(items),
            "no_trigger_count": no_trigger_count,
            "items": [asdict(item) for item in items],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        report = format_debt_report(items)
        print(report)

    if args.export:
        try:
            with open(args.export, "w", encoding="utf-8") as f:
                f.write(f"# Ledger de Débitos Técnicos\n\n```\n{format_debt_report(items)}\n```\n")
            print(f"✅ Relatório exportado com sucesso para {args.export}")
        except (IOError, OSError) as e:
            print(f"❌ Erro ao exportar relatório: {e}", file=sys.stderr)
            return 1

    if args.sync_memory:
        target_mem = args.sync_memory
        if sync_memory_debt_section(target_mem, items):
            print(f"✅ Seção 7 do {target_mem} sincronizada com sucesso.")
        else:
            print(f"⚠️ Não foi possível sincronizar {target_mem}.", file=sys.stderr)

    if args.fail_on_no_trigger and no_trigger_count > 0:
        print(
            f"\n❌ [GATE BLOQUEADO] {no_trigger_count} débitos sem gatilho de upgrade violam a política.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
