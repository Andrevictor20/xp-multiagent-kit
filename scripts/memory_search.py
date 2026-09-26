#!/usr/bin/env python3
"""
scripts/memory_search.py
Motor de Busca Rápida de Memória & Lições Aprendidas via SQLite FTS5 para o XP Multi-Agent Kit.
Permite consultas ultrarrápidas (<2ms) com resposta concisa (<100 tokens) para evitar leituras
completas de arquivos markdown na recuperação de contexto procedural e episódico.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_FILENAME = ".memory_index.db"


def get_db_path(workspace: Path) -> Path:
    """Retorna o caminho do banco SQLite de índice de memória."""
    return workspace.resolve() / ".agents" / "memory" / DB_FILENAME


def get_file_meta(file_path: Path) -> Tuple[float, int, str]:
    """Retorna mtime, size e hash sha256 simplificado de um arquivo."""
    stat = file_path.stat()
    content = file_path.read_bytes()
    h = hashlib.sha256(content).hexdigest()
    return stat.st_mtime, stat.st_size, h


def init_db(db_path: Path) -> sqlite3.Connection:
    """Inicializa o banco de dados com suporte a FTS5 se ainda não existir."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS indexed_files (
            file_path TEXT PRIMARY KEY,
            mtime REAL,
            size INTEGER,
            hash TEXT
        );
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            category,
            identifier,
            title,
            content,
            source_file,
            line_number UNINDEXED,
            tokenize='porter unicode61'
        );
        """
    )
    conn.commit()
    return conn


def extract_entries_from_file(file_path: Path, rel_path: str) -> List[Dict[str, Any]]:
    """Extrai lições, entradas de histórico e seções para indexação."""
    entries: List[Dict[str, Any]] = []
    if not file_path.is_file():
        return entries

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    for idx, line in enumerate(lines, 1):
        s_line = line.strip()
        if not s_line:
            continue

        # 1. Lições aprendidas [L-NNN]
        lesson_match = re.search(r"\[(L-\d+)\]\s*(?:\*\*(.*?)\*\*)?[:\s-]*(.*)", s_line)
        if lesson_match:
            lid = lesson_match.group(1)
            title = lesson_match.group(2) or lid
            body = s_line
            entries.append({
                "category": "lesson",
                "identifier": lid,
                "title": title,
                "content": body,
                "source_file": rel_path,
                "line_number": idx,
            })
            continue

        # 2. Entradas de tabela de histórico (| YYYY-MM-DD | TYPE | ...)
        if s_line.startswith("|") and not s_line.startswith("| ---") and not s_line.startswith("| Data"):
            parts = [p.strip() for p in s_line.split("|")[1:-1]]
            if len(parts) >= 3 and re.match(r"^\d{4}-\d{2}-\d{2}$", parts[0]):
                date_str = parts[0]
                type_str = parts[1].replace("`", "")
                desc = parts[2]
                entries.append({
                    "category": "history",
                    "identifier": f"{date_str}-{type_str}",
                    "title": f"[{type_str}] {date_str}",
                    "content": s_line,
                    "source_file": rel_path,
                    "line_number": idx,
                })
                continue

    return entries


def build_or_update_index(workspace: Path) -> Dict[str, int]:
    """Indexa incrementalmente os arquivos de memória do workspace."""
    workspace = workspace.resolve()
    memory_dir = workspace / ".agents" / "memory"
    if not memory_dir.exists():
        return {"indexed_items": 0, "reindexed_files": 0}

    db_path = get_db_path(workspace)
    conn = init_db(db_path)

    # Identifica arquivos candidatos para indexação
    candidate_files: List[Path] = []
    proj_mem = memory_dir / "PROJECT_MEMORY.md"
    if proj_mem.is_file():
        candidate_files.append(proj_mem)

    history_file = memory_dir / "archive" / "HISTORY.md"
    if history_file.is_file():
        candidate_files.append(history_file)

    skill_lesson = workspace / ".agents" / "skills" / "lesson-learned" / "SKILL.md"
    if skill_lesson.is_file():
        candidate_files.append(skill_lesson)

    # Coleta arquivos de ADR se existirem
    adr_dir = memory_dir / "adr"
    if adr_dir.is_dir():
        for adr in adr_dir.glob("*.md"):
            candidate_files.append(adr)

    total_indexed_items = 0
    reindexed_files_count = 0

    for fpath in candidate_files:
        rel_path = str(fpath.relative_to(workspace))
        mtime, size, fhash = get_file_meta(fpath)

        cursor = conn.cursor()
        cursor.execute("SELECT mtime, size, hash FROM indexed_files WHERE file_path = ?", (rel_path,))
        row = cursor.fetchone()

        if row and row[0] == mtime and row[1] == size and row[2] == fhash:
            # Arquivo inalterado, pula reindexação
            continue

        # Arquivo novo ou alterado -> remove entradas antigas e reindexa
        conn.execute("DELETE FROM memory_fts WHERE source_file = ?", (rel_path,))

        entries = extract_entries_from_file(fpath, rel_path)
        for e in entries:
            conn.execute(
                """
                INSERT INTO memory_fts (category, identifier, title, content, source_file, line_number)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (e["category"], e["identifier"], e["title"], e["content"], e["source_file"], e["line_number"]),
            )
            total_indexed_items += 1

        conn.execute(
            """
            INSERT OR REPLACE INTO indexed_files (file_path, mtime, size, hash)
            VALUES (?, ?, ?, ?);
            """,
            (rel_path, mtime, size, fhash),
        )
        reindexed_files_count += 1

    conn.commit()
    conn.close()

    return {
        "indexed_items": total_indexed_items,
        "reindexed_files": reindexed_files_count,
    }


def search_memory(
    workspace: Path,
    query: str,
    limit: int = 5,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Executa busca full-text com ranking FTS5 em SQLite."""
    workspace = workspace.resolve()
    db_path = get_db_path(workspace)

    # Garante que o banco está atualizado
    build_or_update_index(workspace)

    if not db_path.is_file():
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Sanitização segura para consulta FTS5
    safe_terms = [re.sub(r'[^a-zA-Z0-9_\-]', '', t) for t in query.split() if t.strip()]
    if not safe_terms:
        conn.close()
        return []

    fts_query = " OR ".join([f'"{term}"*' for term in safe_terms])

    sql = """
        SELECT category, identifier, title, content, source_file, line_number, rank
        FROM memory_fts
        WHERE memory_fts MATCH ?
    """
    params: List[Any] = [fts_query]

    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY rank LIMIT ?"
    params.append(limit)

    results: List[Dict[str, Any]] = []
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        for row in cursor.fetchall():
            results.append({
                "category": row["category"],
                "identifier": row["identifier"],
                "title": row["title"],
                "content": row["content"],
                "source_file": row["source_file"],
                "line_number": row["line_number"],
                "rank": row["rank"],
            })
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

    return results


def format_search_results(results: List[Dict[str, Any]], query: str) -> str:
    """Formata os resultados de busca em bloco ultracompacto (< 15 linhas / ~80 tokens)."""
    if not results:
        return f"ℹ️ Nenhuma entrada encontrada na memória para: '{query}'"

    lines: List[str] = [f"🔍 Memória FTS5 — Resultados para '{query}' ({len(results)} encontrados):"]
    for r in results:
        cat_badge = f"[{r['category'].upper()}]"
        ident = f"`{r['identifier']}`" if r['identifier'] else ""
        content = r['content']
        # Remove redundância de pipes em markdown se for histórico
        if r['category'] == 'history':
            parts = [p.strip() for p in content.split("|")[1:-1]]
            if len(parts) >= 3:
                content = f"{parts[0]} ({parts[1]}): {parts[2]}"

        loc = f"({r['source_file']}#L{r['line_number']})"
        lines.append(f"- {cat_badge} {ident} {content} {loc}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Motor de Busca Rápida de Memória & Lições (SQLite FTS5)")
    parser.add_argument("query", nargs="?", default="", help="Termo para buscar na memória")
    parser.add_argument("--workspace", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--limit", type=int, default=5, help="Limite de resultados (padrão: 5)")
    parser.add_argument("--category", choices=["lesson", "history", "decision"], help="Filtrar por categoria")
    parser.add_argument("--index", action="store_true", help="Apenas reindexar o banco de memória")

    args = parser.parse_args()
    ws = Path(args.workspace)

    if args.index or not args.query:
        stats = build_or_update_index(ws)
        print(f"✅ Índice de memória atualizado: {stats['indexed_items']} itens indexados em {stats['reindexed_files']} arquivos.")
        return 0

    results = search_memory(ws, args.query, limit=args.limit, category=args.category)
    print(format_search_results(results, args.query))
    return 0


if __name__ == "__main__":
    sys.exit(main())
