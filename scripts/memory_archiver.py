#!/usr/bin/env python3
"""
scripts/memory_archiver.py
Motor de Rotação Automática e Arquivamento de Memória Episódica (Sliding Window).

Mantém PROJECT_MEMORY.md dentro do orçamento do Fast Bootstrap (Passo 0). A
rotação é governada por DOIS critérios, o mais restritivo vence:
  1. contagem máxima de entregas (DEFAULT_MAX_EPISODIC_ENTRIES)
  2. teto duro de bytes (MEMORY_INDEX_MAX_BYTES) - porque o que custa no
     contexto é o tamanho, não o número de itens

O excedente vai para archive/HISTORY.md; detalhes longos podem ser derramados
em memory/details/ para leitura sob demanda.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import List, Optional, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from scripts.kit_constants import MEMORY_DETAILS_DIR, MEMORY_INDEX_MAX_BYTES
except ImportError:  # pragma: no cover - execução direta
    from kit_constants import (  # type: ignore
        MEMORY_DETAILS_DIR,
        MEMORY_INDEX_MAX_BYTES,
    )

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


def _compose_memory(prefix: str, entries: List[str], suffix: str) -> str:
    """Remonta o conteúdo do PROJECT_MEMORY.md com as entregas retidas."""
    body = prefix.rstrip() + "\n\n" + "\n\n".join(entries)
    if suffix.strip():
        return body + "\n\n" + suffix.lstrip()
    return body + "\n"


def enforce_byte_budget(
    prefix: str,
    entries: List[str],
    suffix: str,
    max_bytes: int,
) -> Tuple[List[str], List[str]]:
    """
    Reduz as entregas retidas até o conteúdo caber em max_bytes.
    Retorna (retidas, excedentes). Sempre preserva ao menos a entrada mais recente.
    """
    keep = len(entries)
    while keep > 1:
        candidate = _compose_memory(prefix, entries[:keep], suffix)
        if len(candidate.encode("utf-8")) <= max_bytes:
            break
        keep -= 1
    return entries[:keep], entries[keep:]


SECTION_HEADER_PATTERN = re.compile(r"(?m)^(##\s+[^\n]+)$")
# Seções que permanecem SEMPRE no índice (memória de trabalho + episódica recente):
# resumo, saúde, entregas recentes e backlog/handoff. O restante (semântica,
# procedural, dívidas, logs de versão) vira detalhe sob demanda.
PROTECTED_SECTION_PREFIXES = ("## 1.", "## 2.", "## 3.", "## 4.")


def split_top_level_sections(content: str) -> List[Tuple[str, str]]:
    """Divide o documento em blocos (cabeçalho, corpo) por seção de nível 2."""
    matches = list(SECTION_HEADER_PATTERN.finditer(content))
    if not matches:
        return [("", content)]

    blocks: List[Tuple[str, str]] = []
    if matches[0].start() > 0:
        blocks.append(("", content[: matches[0].start()]))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        blocks.append((match.group(1), content[match.end():end]))
    return blocks


def _slugify(title: str) -> str:
    ascii_title = (
        unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    return slug or "secao"


def spill_sections_to_details(
    memory_path: Union[str, Path],
    max_bytes: int = MEMORY_INDEX_MAX_BYTES,
    details_dir: Optional[Union[str, Path]] = None,
    dry_run: bool = False,
) -> Tuple[int, List[str]]:
    """
    Derrama as seções volumosas para memory/details/, deixando um ponteiro no
    índice. A poda da Seção 3 não basta quando o grosso do arquivo está nas
    seções semânticas/procedurais: o índice é o que custa no Passo 0.

    Retorna (novo_tamanho_em_bytes, seções_movidas).
    """
    mem_file = Path(memory_path)
    content = mem_file.read_text(encoding="utf-8")
    details = Path(details_dir) if details_dir else mem_file.parent / MEMORY_DETAILS_DIR

    moved: List[str] = []
    while len(content.encode("utf-8")) > max_bytes:
        previous_length = len(content)
        blocks = split_top_level_sections(content)
        candidates = [
            (header, body) for header, body in blocks
            if header.strip() and not header.startswith(PROTECTED_SECTION_PREFIXES)
        ]
        if not candidates:
            break

        header, body = max(candidates, key=lambda pair: len(pair[1].encode("utf-8")))
        if len(body.encode("utf-8")) < 512:
            break

        slug = _slugify(header.lstrip("# ").strip())
        target_name = f"{slug}.md"
        pointer = (
            f"\n> Conteúdo movido para [{MEMORY_DETAILS_DIR}/{target_name}]"
            f"({MEMORY_DETAILS_DIR}/{target_name}) (leitura sob demanda).\n"
        )

        if not dry_run:
            details.mkdir(parents=True, exist_ok=True)
            (details / target_name).write_text(
                f"{header}\n{body.strip()}\n", encoding="utf-8"
            )

        # body já inicia com a quebra de linha do cabeçalho: não duplicar "\n"
        content = content.replace(f"{header}{body}", f"{header}\n{pointer}\n", 1)
        if len(content) >= previous_length:
            # Guarda de convergência: se a substituição não reduziu o documento,
            # parar em vez de entrar em loop infinito.
            break
        moved.append(target_name)

    if not dry_run and moved:
        mem_file.write_text(content, encoding="utf-8")

    return len(content.encode("utf-8")), moved


def archive_memory(
    memory_path: Union[str, Path],
    history_path: Optional[Union[str, Path]] = None,
    max_entries: int = DEFAULT_MAX_EPISODIC_ENTRIES,
    dry_run: bool = False,
    max_bytes: Optional[int] = MEMORY_INDEX_MAX_BYTES,
    details_path: Optional[Union[str, Path]] = None,
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
    retained_entries = entries[:max_entries]
    archived_entries = entries[max_entries:]

    within_count = total_entries <= max_entries
    if max_bytes:
        retained_entries, byte_overflow = enforce_byte_budget(
            prefix, retained_entries, suffix, max_bytes
        )
        archived_entries = byte_overflow + archived_entries
    elif within_count:
        return total_entries, 0

    if not archived_entries:
        return len(retained_entries), 0

    new_memory_content = _compose_memory(prefix, retained_entries, suffix)

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
        if details_path:
            det_file = Path(details_path)
            det_file.parent.mkdir(parents=True, exist_ok=True)
            with det_file.open("a", encoding="utf-8") as f:
                f.write("\n\n".join(archived_entries) + "\n")

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
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=MEMORY_INDEX_MAX_BYTES,
        help=f"Teto duro de bytes do índice de memória (padrão: {MEMORY_INDEX_MAX_BYTES}; 0 desativa)",
    )
    parser.add_argument(
        "--details",
        default=None,
        help=f"Arquivo de detalhes sob demanda (padrão: memory/{MEMORY_DETAILS_DIR}/EPISODES.md)",
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
    details_target = args.details or (
        mem_path.parent / MEMORY_DETAILS_DIR / "EPISODES.md"
    )
    retained, archived = archive_memory(
        mem_path,
        history_path=args.history,
        max_entries=args.max_entries,
        dry_run=args.dry_run,
        max_bytes=args.max_bytes or None,
        details_path=details_target,
    )

    new_size = mem_path.stat().st_size if not args.dry_run else orig_size
    moved_sections: List[str] = []

    if args.max_bytes:
        spilled_size, moved_sections = spill_sections_to_details(
            mem_path,
            max_bytes=args.max_bytes,
            details_dir=mem_path.parent / MEMORY_DETAILS_DIR,
            dry_run=args.dry_run,
        )
        new_size = spilled_size

    saved_bytes = max(0, orig_size - new_size)

    if archived > 0 or moved_sections:
        mode = "[DRY-RUN] " if args.dry_run else ""
        print(f"✅ {mode}Memória rotacionada com sucesso:")
        print(f"   • Entregas retidas na memória viva : {retained}")
        print(f"   • Entregas arquivadas em HISTORY.md: {archived}")
        if moved_sections:
            print(f"   • Seções movidas para {MEMORY_DETAILS_DIR}/ : {len(moved_sections)} "
                  f"({', '.join(moved_sections)})")
        print(f"   • Tamanho anterior : {orig_size / 1024:.1f} KB")
        print(f"   • Tamanho novo     : {new_size / 1024:.1f} KB (economia: ~{saved_bytes / 1024:.1f} KB / ~{saved_bytes // 4} tokens)")
    else:
        print(
            f"ℹ️ Memória dentro do orçamento ({retained} entregas, "
            f"{orig_size / 1024:.1f} KB / teto {args.max_bytes / 1024:.1f} KB). Nenhuma rotação necessária."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
