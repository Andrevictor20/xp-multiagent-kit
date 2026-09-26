#!/usr/bin/env python3
"""
scripts/memory_archiver.py
Motor de Rotação Automática e Arquivamento de Memória Episódica (Sliding Window).
Mantém PROJECT_MEMORY.md enxuto (< 15 KB / ~3.5k tokens) arquivando entregas
antigas em archive/HISTORY.md sem perda de rastreabilidade histórica.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union

DEFAULT_MAX_EPISODIC_ENTRIES = 8
SECTION_3_HEADER_PATTERN = re.compile(
    r"(##\s+3\.\s+[^\n]*\n+)",
    re.IGNORECASE,
)
NEXT_SECTION_PATTERN = re.compile(
    r"(\n+---\s*\n+##\s+[4-9]\.|\n+##\s+[4-9]\.)",
    re.IGNORECASE,
)


def parse_episodic_entries(content: str) -> List[str]:
    """Extrai todas as linhas individuais de entregas da Seção 3."""
    match = SECTION_3_HEADER_PATTERN.search(content)
    if not match:
        return []

    after_sec3 = content[match.end():]
    next_match = NEXT_SECTION_PATTERN.search(after_sec3)
    sec3_body = after_sec3[:next_match.start()] if next_match else after_sec3

    entries: List[str] = []
    for line in sec3_body.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("|") and line_stripped.endswith("|"):
            # Ignora cabeçalhos genéricos de tabela markdown se houver
            if "Data" in line_stripped and "Tipo" in line_stripped:
                continue
            if re.match(r"^\|[\s\-:|]+\|$", line_stripped):
                continue
            entries.append(line_stripped)

    if not entries and "### " in sec3_body:
        blocks = re.split(r"(?m)(?=^### )", sec3_body)
        for b in blocks:
            b_str = b.strip()
            if b_str.startswith("### "):
                entries.append(b_str)

    return entries


def split_memory_sections(content: str) -> Tuple[str, List[str], str]:
    """
    Divide o conteúdo do PROJECT_MEMORY.md em 3 partes:
    1. prefix: tudo até o início do conteúdo da Seção 3 (inclusive o cabeçalho ## 3).
    2. entries: lista de linhas de entregas da Seção 3.
    3. suffix: tudo a partir da próxima seção (## 4...) até o fim do arquivo.
    """
    match = SECTION_3_HEADER_PATTERN.search(content)
    if not match:
        return content, [], ""

    prefix = content[:match.end()]
    after_sec3 = content[match.end():]

    next_match = NEXT_SECTION_PATTERN.search(after_sec3)
    if next_match:
        sec3_body = after_sec3[:next_match.start()]
        suffix = after_sec3[next_match.start():]
    else:
        sec3_body = after_sec3
        suffix = ""

    entries: List[str] = []
    for line in sec3_body.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("|") and line_stripped.endswith("|"):
            if "Data" in line_stripped and "Tipo" in line_stripped:
                continue
            if re.match(r"^\|[\s\-:|]+\|$", line_stripped):
                continue
            entries.append(line_stripped)

    if not entries and "### " in sec3_body:
        blocks = re.split(r"(?m)(?=^### )", sec3_body)
        intro_blocks = []
        for b in blocks:
            b_str = b.strip()
            if b_str.startswith("### "):
                entries.append(b_str)
            elif b_str:
                intro_blocks.append(b_str)
        if intro_blocks:
            prefix = prefix.rstrip() + "\n\n" + "\n\n".join(intro_blocks)

    return prefix, entries, suffix


def archive_memory(
    memory_path: Union[str, Path],
    history_path: Optional[Union[str, Path]] = None,
    max_entries: int = DEFAULT_MAX_EPISODIC_ENTRIES,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    Executa a rotação da Seção 3 do arquivo de memória.
    Retorna uma tupla (retained_count, archived_count).
    """
    mem_file = Path(memory_path)
    if not mem_file.is_file():
        return 0, 0

    if history_path is None:
        hist_file = mem_file.parent / "archive" / "HISTORY.md"
    else:
        hist_file = Path(history_path)

    raw_content = mem_file.read_text(encoding="utf-8")
    prefix, entries, suffix = split_memory_sections(raw_content)

    total_entries = len(entries)
    if total_entries <= max_entries:
        return total_entries, 0

    retained_entries = entries[:max_entries]
    archived_entries = entries[max_entries:]

    # Monta novo conteúdo do PROJECT_MEMORY.md
    if suffix.strip():
        new_memory_content = prefix.rstrip() + "\n\n" + "\n\n".join(retained_entries) + "\n\n" + suffix.lstrip()
    else:
        new_memory_content = prefix.rstrip() + "\n\n" + "\n\n".join(retained_entries) + "\n"

    # Prepara o append ordenado no HISTORY.md
    history_header = (
        "# 📜 Historical Archive — Project Memory Archive\n\n"
        "> Registro permanente de entregas rotacionadas da memória viva (Sliding Window).\n\n"
        "---\n\n"
        "## Arquivo Histórico de Entregas\n\n"
    )

    if hist_file.is_file():
        existing_history = hist_file.read_text(encoding="utf-8")
        # Injeta as novas entregas arquivadas no topo do arquivo histórico
        if "## Arquivo Histórico de Entregas" in existing_history:
            parts = existing_history.split("## Arquivo Histórico de Entregas\n\n", 1)
            new_history_content = (
                parts[0]
                + "## Arquivo Histórico de Entregas\n\n"
                + "\n\n".join(archived_entries)
                + "\n\n"
                + parts[1].strip()
                + "\n"
            )
        else:
            new_history_content = (
                existing_history.strip()
                + "\n\n---\n\n"
                + "\n\n".join(archived_entries)
                + "\n"
            )
    else:
        new_history_content = history_header + "\n\n".join(archived_entries) + "\n"

    if not dry_run:
        hist_file.parent.mkdir(parents=True, exist_ok=True)
        hist_file.write_text(new_history_content, encoding="utf-8")
        mem_file.write_text(new_memory_content, encoding="utf-8")

    return len(retained_entries), len(archived_entries)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="XP Kit — Motor de Rotação e Arquivamento de Memória Episódica"
    )
    parser.add_argument(
        "--file", "-f",
        default=".agents/memory/PROJECT_MEMORY.md",
        help="Caminho do arquivo PROJECT_MEMORY.md (padrão: .agents/memory/PROJECT_MEMORY.md)",
    )
    parser.add_argument(
        "--history",
        default=None,
        help="Caminho do arquivo archive/HISTORY.md (padrão: .agents/memory/archive/HISTORY.md)",
    )
    parser.add_argument(
        "--max-entries", "-m",
        type=int,
        default=DEFAULT_MAX_EPISODIC_ENTRIES,
        help=f"Número máximo de entregas na memória viva (padrão: {DEFAULT_MAX_EPISODIC_ENTRIES})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas simula o arquivamento sem modificar arquivos no disco",
    )

    args = parser.parse_args()
    mem_path = Path(args.file)

    if not mem_path.is_file():
        # Tenta localizar a partir da raiz do repositório
        candidate = Path.cwd() / args.file
        if candidate.is_file():
            mem_path = candidate
        else:
            print(f"❌ Arquivo de memória não encontrado: {args.file}", file=sys.stderr)
            return 1

    orig_size = mem_path.stat().st_size
    retained, archived = archive_memory(
        mem_path,
        history_path=args.history,
        max_entries=args.max_entries,
        dry_run=args.dry_run,
    )

    new_size = mem_path.stat().st_size if not args.dry_run else orig_size
    saved_bytes = max(0, orig_size - new_size)

    if archived > 0:
        mode = "[DRY-RUN] " if args.dry_run else ""
        print(f"✅ {mode}Memória rotacionada com sucesso:")
        print(f"   • Entregas retidas na memória viva : {retained}")
        print(f"   • Entregas arquivadas em HISTORY.md: {archived}")
        print(f"   • Tamanho anterior : {orig_size / 1024:.1f} KB")
        print(f"   • Tamanho novo     : {new_size / 1024:.1f} KB (economia: ~{saved_bytes / 1024:.1f} KB / ~{saved_bytes // 4} tokens)")
    else:
        print(f"ℹ️ Memória já está dentro do limite ({retained}/{args.max_entries} entregas). Nenhuma rotação necessária.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
