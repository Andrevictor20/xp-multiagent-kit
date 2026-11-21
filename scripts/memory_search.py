#!/usr/bin/env python3
"""
scripts/memory_search.py
Motor de Busca Rápida de Memória & Contexto via SQLite FTS5 para o XP Multi-Agent Kit v4.
Suporta escopos `repo:` (isolado por projeto) e `user:` (cross-repo em ~/.xp-kit/memory/),
indexando todas as 5 camadas (fatos, decisões, histórico, lições/never e Dead-Ends).
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
USER_DB_FILENAME = ".user_index.db"


def get_db_path(workspace: Path) -> Path:
    return workspace.resolve() / ".agents" / "memory" / DB_FILENAME


def resolve_user_memory_dir(user_dir: Optional[Path] = None) -> Path:
    if user_dir is not None:
        return Path(user_dir).expanduser().resolve()
    env_dir = os.environ.get("XP_USER_MEMORY_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / ".xp-kit" / "memory").resolve()


def get_file_meta(file_path: Path) -> Tuple[float, int, str]:
    stat = file_path.stat()
    content = file_path.read_bytes()
    h = hashlib.sha256(content).hexdigest()
    return stat.st_mtime, stat.st_size, h


def init_db(db_path: Path) -> sqlite3.Connection:
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


def _section_kind(h2: str) -> str:
    low = h2.lower()
    if "dead-end" in low or "dead end" in low or "falharam" in low or "negative memory" in low:
        return "dead_end"
    if "never" in low or "lições" in low or "licoes" in low or "procedural" in low or "gotcha" in low:
        return "never_or_lesson"
    if "decis" in low or "architectural" in low or "preferências" in low or "preferencias" in low:
        return "decision"
    return ""


def extract_entries_from_file(file_path: Path, rel_path: str) -> List[Dict[str, Any]]:
    """Extrai lições, regras never, Dead-Ends, decisões, políticas, ACs e histórico."""
    entries: List[Dict[str, Any]] = []
    if not file_path.is_file():
        return entries

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    is_policy_file = "policies" in rel_path
    is_spec_file = "specs" in rel_path
    is_decision_file = "5-architectural" in rel_path or "/adr/" in rel_path or rel_path.startswith("adr/")
    is_dead_ends_file = "dead_ends" in rel_path.lower() or "dead-ends" in rel_path.lower()

    current_h2 = ""
    current_h3 = ""
    section_title = ""
    section_start_line = 1
    section_lines: List[str] = []

    def flush_section():
        nonlocal section_lines, section_title, section_start_line
        if not section_lines or not section_title:
            section_lines = []
            return
        body = " ".join([l.strip() for l in section_lines if l.strip()])
        if len(body) > 10:
            cat = "policy" if is_policy_file else ("spec" if is_spec_file else "info")
            ident = f"{Path(rel_path).stem}-{section_title[:30]}".replace(" ", "-")
            content = f"[Arquivo: {rel_path} | Seção: {section_title}] {body}"
            entries.append({
                "category": cat,
                "identifier": ident,
                "title": section_title,
                "content": content,
                "source_file": rel_path,
                "line_number": section_start_line,
            })
        section_lines = []

    for idx, line in enumerate(lines, 1):
        s_line = line.strip()
        if not s_line or s_line.startswith("<!--"):
            continue

        if s_line.startswith("## "):
            if is_policy_file or is_spec_file:
                flush_section()
            current_h2 = s_line[3:].strip()
            section_title = current_h2
            section_start_line = idx
            current_h3 = ""
            continue
        elif s_line.startswith("### "):
            if is_policy_file or is_spec_file:
                flush_section()
            current_h3 = s_line[4:].strip()
            section_title = f"{current_h2} > {current_h3}" if current_h2 else current_h3
            section_start_line = idx
            continue
        elif s_line.startswith("# "):
            if is_policy_file or is_spec_file:
                flush_section()
            section_title = s_line[2:].strip()
            section_start_line = idx
            continue

        sec_kind = _section_kind(current_h2)

        # 1. Lições aprendidas [L-NNN]
        lesson_match = re.search(r"\[(L-\d+)\]\s*(?:\*\*(.*?)\*\*)?[:\s-]*(.*)", s_line)
        if lesson_match:
            lid = lesson_match.group(1)
            title = lesson_match.group(2) or lid
            body = f"[Arquivo: {rel_path} | Lição: {lid}] {s_line}"
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
                entries.append({
                    "category": "history",
                    "identifier": f"{date_str}-{type_str}",
                    "title": f"[{type_str}] {date_str}",
                    "content": s_line,
                    "source_file": rel_path,
                    "line_number": idx,
                })
                continue

        # 3. Dead-Ends (Negative Memory)
        if (sec_kind == "dead_end" or is_dead_ends_file) and s_line.startswith(("- ", "* ")):
            if "nenhum dead-end registrado" in s_line.lower():
                continue
            entries.append({
                "category": "dead_end",
                "identifier": f"DEAD-END-L{idx}",
                "title": f"Dead-End ({Path(rel_path).name})",
                "content": f"[Arquivo: {rel_path} | Dead-End] {s_line}",
                "source_file": rel_path,
                "line_number": idx,
            })
            continue

        # 4. Regras 'never' e lições em bullet da seção 4
        if sec_kind == "never_or_lesson" and s_line.startswith(("- ", "* ")):
            is_never = bool(re.match(r"^[-*]\s+`?never`?\b", s_line, re.IGNORECASE))
            cat = "never" if is_never else "lesson"
            label = "Never" if is_never else "Lição"
            entries.append({
                "category": cat,
                "identifier": f"{cat.upper()}-L{idx}",
                "title": f"{label} ({Path(rel_path).name})",
                "content": f"[Arquivo: {rel_path} | {label}] {s_line}",
                "source_file": rel_path,
                "line_number": idx,
            })
            continue

        # 5. Decisões arquiteturais e preferências globais
        dec_match = re.search(r"^[-*]\s*\*\*(?:(\d{4}-\d{2}-\d{2})\s*[-–:]\s*)?(.*?)\*\*[:\s-]*(.*)", s_line)
        if dec_match and (is_decision_file or sec_kind == "decision" or "decis" in s_line.lower()):
            dt = dec_match.group(1) or ""
            title = dec_match.group(2).strip()
            ident = f"{dt}-{title[:20]}" if dt else title[:30]
            content = f"[Arquivo: {rel_path} | Decisão: {title}] {s_line}"
            entries.append({
                "category": "decision",
                "identifier": ident,
                "title": title,
                "content": content,
                "source_file": rel_path,
                "line_number": idx,
            })
            continue
        if sec_kind == "decision" and s_line.startswith(("- ", "* ")):
            entries.append({
                "category": "decision",
                "identifier": f"DEC-L{idx}",
                "title": f"Decisão ({Path(rel_path).name})",
                "content": f"[Arquivo: {rel_path} | Decisão] {s_line}",
                "source_file": rel_path,
                "line_number": idx,
            })
            continue

        # 6. Critérios de aceitação de Specs (AC-N: ...)
        ac_match = re.search(r"^[-*]?\s*[`'\"]?(AC-\d+)[`'\"]?[:\s-]*(.*)", s_line)
        if ac_match:
            ac_id = ac_match.group(1)
            content = f"[Arquivo: {rel_path} | Spec: {ac_id}] {s_line}"
            entries.append({
                "category": "spec",
                "identifier": ac_id,
                "title": f"[{ac_id}] {Path(rel_path).stem}",
                "content": content,
                "source_file": rel_path,
                "line_number": idx,
            })
            continue

        if is_policy_file or is_spec_file:
            section_lines.append(s_line)

    if is_policy_file or is_spec_file:
        flush_section()

    return entries


def find_candidate_files(workspace: Path) -> List[Path]:
    workspace = workspace.resolve()
    candidate_files: List[Path] = []
    agents_dir = workspace / ".agents"
    memory_dir = agents_dir / "memory"

    if memory_dir.is_dir():
        proj_mem = memory_dir / "PROJECT_MEMORY.md"
        if proj_mem.is_file():
            candidate_files.append(proj_mem)
        for sub in ("archive", "details", "adr"):
            sub_dir = memory_dir / sub
            if sub_dir.is_dir():
                candidate_files.extend(sorted(sub_dir.glob("*.md")))

    for folder in ("policies", "specs"):
        f_dir = agents_dir / folder
        if f_dir.is_dir():
            for f in sorted(f_dir.glob("*.md")):
                if f.name != "INDEX.md":
                    candidate_files.append(f)

    return candidate_files


def _index_files_into_db(base_dir: Path, files: List[Path], db_path: Path) -> Dict[str, int]:
    if not files:
        return {"indexed_items": 0, "reindexed_files": 0}
    conn = init_db(db_path)
    total_indexed = 0
    reindexed = 0
    for fpath in files:
        try:
            rel_path = str(fpath.relative_to(base_dir))
        except ValueError:
            rel_path = fpath.name
        mtime, size, fhash = get_file_meta(fpath)
        row = conn.execute(
            "SELECT mtime, size, hash FROM indexed_files WHERE file_path = ?", (rel_path,)
        ).fetchone()
        if row and row[0] == mtime and row[1] == size and row[2] == fhash:
            continue

        conn.execute("DELETE FROM memory_fts WHERE source_file = ?", (rel_path,))
        for e in extract_entries_from_file(fpath, rel_path):
            conn.execute(
                "INSERT INTO memory_fts (category, identifier, title, content, source_file, line_number) VALUES (?, ?, ?, ?, ?, ?);",
                (e["category"], e["identifier"], e["title"], e["content"], e["source_file"], e["line_number"]),
            )
            total_indexed += 1
        conn.execute(
            "INSERT OR REPLACE INTO indexed_files (file_path, mtime, size, hash) VALUES (?, ?, ?, ?);",
            (rel_path, mtime, size, fhash),
        )
        reindexed += 1
    conn.commit()
    conn.close()
    return {"indexed_items": total_indexed, "reindexed_files": reindexed}


def build_or_update_index(workspace: Path) -> Dict[str, int]:
    ws = workspace.resolve()
    return _index_files_into_db(ws, find_candidate_files(ws), get_db_path(ws))


def build_or_update_user_index(user_dir: Optional[Path] = None) -> Dict[str, int]:
    u_dir = resolve_user_memory_dir(user_dir)
    if not u_dir.is_dir():
        return {"indexed_items": 0, "reindexed_files": 0}
    files = sorted(u_dir.glob("*.md"))
    return _index_files_into_db(u_dir, files, u_dir / USER_DB_FILENAME)


def _query_db(
    db_path: Path,
    safe_terms: List[str],
    limit: int,
    category: Optional[str],
    scope_label: str,
) -> List[Dict[str, Any]]:
    if not db_path.is_file():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    query_and = " ".join([f'"{term}"*' for term in safe_terms])
    query_or = " OR ".join([f'"{term}"*' for term in safe_terms])

    def execute_query(fts_pattern: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT category, identifier, title, content, source_file, line_number,
                   bm25(memory_fts, 1.0, 5.0, 10.0, 1.0, 0.5) AS rank
            FROM memory_fts
            WHERE memory_fts MATCH ?
        """
        params: List[Any] = [fts_pattern]
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += (
            " ORDER BY CASE WHEN category IN ('dead_end', 'never', 'lesson', 'policy', 'decision', 'spec') "
            "THEN 0 ELSE 1 END, rank ASC LIMIT ?"
        )
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [
            {
                "category": r["category"],
                "identifier": r["identifier"],
                "title": r["title"],
                "content": r["content"],
                "source_file": r["source_file"],
                "line_number": r["line_number"],
                "rank": r["rank"],
                "scope": scope_label,
            }
            for r in rows
        ]

    try:
        res = execute_query(query_and)
        if not res and query_and != query_or:
            res = execute_query(query_or)
        return res
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def search_memory(
    workspace: Path,
    query: str,
    limit: int = 5,
    category: Optional[str] = None,
    scope: str = "all",
    user_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Executa busca full-text BM25 em SQLite FTS5 nos escopos repo:, user: ou all."""
    ws = workspace.resolve()
    safe_terms = [re.sub(r"[^a-zA-Z0-9_\-]", "", t) for t in query.split() if t.strip()]
    safe_terms = [t for t in safe_terms if t]
    if not safe_terms:
        return []

    combined: List[Dict[str, Any]] = []
    if scope in ("all", "repo"):
        build_or_update_index(ws)
        combined.extend(_query_db(get_db_path(ws), safe_terms, limit, category, "repo"))

    if scope in ("all", "user"):
        u_dir = resolve_user_memory_dir(user_dir)
        if u_dir.is_dir():
            build_or_update_user_index(u_dir)
            combined.extend(_query_db(u_dir / USER_DB_FILENAME, safe_terms, limit, category, "user"))

    priority_cats = {"dead_end", "never", "lesson", "policy", "decision", "spec"}
    combined.sort(
        key=lambda r: (
            0 if r["category"] in priority_cats else 1,
            0 if r["scope"] == "repo" else 1,
            r["rank"],
        )
    )
    return combined[:limit]


def format_search_results(results: List[Dict[str, Any]], query: str) -> str:
    if not results:
        return f"ℹ️ Nenhuma entrada encontrada na memória para: '{query}'"
    lines: List[str] = [f"🔍 Memória FTS5 — Resultados para '{query}' ({len(results)} encontrados):"]
    for r in results:
        sc = r.get("scope", "repo").upper()
        cat_badge = f"[{sc}|{r['category'].upper()}]"
        ident = f"`{r['identifier']}`" if r["identifier"] else ""
        content = r["content"]
        if r["category"] == "history":
            parts = [p.strip() for p in content.split("|")[1:-1]]
            if len(parts) >= 3:
                content = f"{parts[0]} ({parts[1]}): {parts[2]}"
        loc = f"({r['source_file']}#L{r['line_number']})"
        lines.append(f"- {cat_badge} {ident} {content} {loc}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Motor de Busca Rápida de Memória Multi-Repo (SQLite FTS5)")
    parser.add_argument("query", nargs="?", default="", help="Termo para buscar na memória")
    parser.add_argument("--workspace", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--scope", choices=["all", "repo", "user"], default="all")
    parser.add_argument("--category", choices=["lesson", "history", "decision", "policy", "spec", "dead_end", "never"])
    parser.add_argument("--index", action="store_true", help="Apenas reindexar os bancos de memória")

    args = parser.parse_args()
    ws = Path(args.workspace)

    if args.index or not args.query:
        stats = build_or_update_index(ws)
        u_stats = build_or_update_user_index()
        print(
            f"✅ Índice atualizado: repo={stats['indexed_items']} itens ({stats['reindexed_files']} arq.) | "
            f"user={u_stats['indexed_items']} itens ({u_stats['reindexed_files']} arq.)"
        )
        return 0

    results = search_memory(ws, args.query, limit=args.limit, category=args.category, scope=args.scope)
    print(format_search_results(results, args.query))
    return 0


if __name__ == "__main__":
    sys.exit(main())
