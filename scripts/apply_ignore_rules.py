#!/usr/bin/env python3
"""
scripts/apply_ignore_rules.py
XP Multi-Agent Kit v2

Aplica universal.geminiignore e .antigravityignore em todos os projetos,
workspaces e diretórios globais do Antigravity IDE & CLI.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sqlite3
import sys
import urllib.parse
from pathlib import Path
from typing import List, Set


def get_template_content() -> str:
    template_path = Path(__file__).resolve().parent.parent / "templates" / "universal.geminiignore"
    if not template_path.is_file():
        raise FileNotFoundError(f"Template não encontrado em: {template_path}")
    return template_path.read_text(encoding="utf-8")


def discover_all_project_directories() -> List[Path]:
    projects: Set[Path] = set()
    home = Path.home()

    # 1. Diretórios Globais do Antigravity / Gemini
    for g in [
        home / ".gemini",
        home / ".gemini" / "antigravity-ide",
        home / ".gemini" / "antigravity-cli",
        home / ".gemini" / "config",
    ]:
        if g.is_dir():
            projects.add(g)

    # 2. Workspaces registrados no banco SQLite do Antigravity IDE
    vscdb_path = home / ".config" / "Antigravity IDE" / "User" / "globalStorage" / "state.vscdb"
    if vscdb_path.is_file():
        try:
            conn = sqlite3.connect(f"file:{vscdb_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # 2.1 recentlyOpenedPathsList
            cursor.execute("SELECT value FROM ItemTable WHERE key = 'history.recentlyOpenedPathsList';")
            row = cursor.fetchone()
            if row:
                try:
                    data = json.loads(row[0])
                    for entry in data.get("entries", []):
                        uri = entry.get("folderUri")
                        if uri:
                            p = Path(urllib.parse.unquote(uri.replace("file://", "")))
                            if p.is_dir():
                                projects.add(p)
                except Exception:
                    pass

            # 2.2 sidebarWorkspaces
            cursor.execute("SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.sidebarWorkspaces';")
            row = cursor.fetchone()
            if row and row[0]:
                for m in re.findall(r"file://[^\s\x00-\x1f\"\'\*\<\>\?]+", row[0]):
                    p = Path(urllib.parse.unquote(m.replace("file://", "")))
                    if p.is_dir():
                        projects.add(p)

            conn.close()
        except Exception as e:
            sys.stderr.write(f"Aviso ao ler state.vscdb: {e}\n")

    # 3. Varredura nos diretórios usuais de projetos: ~/Downloads e ~/Documentos
    indicator_files = (
        ".git",
        ".agents",
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "requirements.txt",
        "go.mod",
        "docker-compose.yml",
        "Dockerfile",
        "Makefile",
    )

    for search_root in [home / "Downloads", home / "Documentos"]:
        if not search_root.is_dir():
            continue
        try:
            for entry in search_root.iterdir():
                if entry.is_dir() and not entry.name.startswith("."):
                    if any((entry / ind).exists() for ind in indicator_files):
                        projects.add(entry)
                    # Verifica subpastas de primeiro nível (ex: Saturn/frontend)
                    for sub in entry.iterdir():
                        if sub.is_dir() and any((sub / ind).exists() for ind in indicator_files):
                            projects.add(sub)
        except Exception:
            pass

    return sorted(list(projects))


def apply_ignore_to_directory(project_dir: Path, template_content: str) -> List[str]:
    created = []
    for filename in (".geminiignore", ".antigravityignore"):
        target = project_dir / filename
        try:
            target.write_text(template_content, encoding="utf-8")
            created.append(filename)
        except Exception as e:
            sys.stderr.write(f"Erro ao gravar {target}: {e}\n")
    return created


def main() -> int:
    template = get_template_content()
    projects = discover_all_project_directories()

    print("=" * 75)
    print(" 🛡️  APLICAÇÃO GLOBAL DE .geminiignore & .antigravityignore (XP Multi-Agent Kit)")
    print("=" * 75)
    print(f"Diretórios de projetos e globais localizados: {len(projects)}")
    print("-" * 75)

    success_count = 0
    for proj in projects:
        applied = apply_ignore_to_directory(proj, template)
        if applied:
            success_count += 1
            print(f" ✅ {proj.name:32} -> {', '.join(applied)} [{proj}]")

    print("-" * 75)
    print(f"✨ Concluído com sucesso! {success_count} diretórios atualizados.")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
