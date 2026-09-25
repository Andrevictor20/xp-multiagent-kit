#!/usr/bin/env python3
"""
scripts/repo_map.py
Gerador de Repo Map Ultracompacto (Padrão Aider) para o XP Multi-Agent Kit v2.
Extrai assinaturas e definições AST/Regex em árvore concisa (< 80 linhas / ~1.2k tokens)
para zerar a necessidade de chamadas de exploração cega (list_dir, grep exploratório).
"""
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

IGNORED_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".gemini",
    "coverage",
    ".pytest_cache",
    ".turbo",
    ".mypy_cache",
    "target",
    "brain",
    ".system_generated",
}

IGNORED_EXTS: Set[str] = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".map",
    ".min.js",
    ".min.css",
    ".lock",
    ".jsonl",
    ".log",
}


def extract_python_symbols(file_path: Path) -> List[str]:
    """Extrai classes, métodos e funções de um arquivo Python via AST."""
    symbols: List[str] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content, filename=str(file_path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [
                    m.name
                    for m in node.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not m.name.startswith("__")
                ]
                if methods:
                    symbols.append(f"class {node.name}({', '.join(methods[:4])})")
                else:
                    symbols.append(f"class {node.name}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    symbols.append(f"def {node.name}()")
    except Exception:
        pass
    return symbols


def extract_js_ts_symbols(file_path: Path) -> List[str]:
    """Extrai definições exportadas de arquivos TypeScript/JavaScript."""
    symbols: List[str] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        class_matches = re.findall(r"export\s+class\s+([A-Za-z0-9_]+)", content)
        for c in class_matches:
            symbols.append(f"class {c}")

        func_matches = re.findall(r"export\s+(?:async\s+)?function\s+([A-Za-z0-9_]+)", content)
        for f in func_matches:
            symbols.append(f"def {f}()")

        iface_matches = re.findall(r"export\s+(?:interface|type)\s+([A-Za-z0-9_]+)", content)
        for i in iface_matches[:3]:
            symbols.append(f"type {i}")
    except Exception:
        pass
    return symbols


def extract_file_symbols(file_path: Path) -> List[str]:
    """Roteia extração de símbolos pelo formato do arquivo."""
    suffix = file_path.suffix.lower()
    if suffix == ".py":
        return extract_python_symbols(file_path)
    elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return extract_js_ts_symbols(file_path)
    return []


def generate_repo_map(workspace_dir: Path, max_lines: int = 80) -> str:
    """Gera o mapa conciso de repositório em formato Markdown compatível com Aider."""
    workspace = workspace_dir.resolve()
    lines: List[str] = [
        "# REPO MAP — XP Multi-Agent Kit (Símbolos & Estrutura)",
        "> Mapa gerado automaticamente pelo `agy-repo-map`. Consulte antes de buscar arquivos.",
        "",
    ]

    files_by_dir: Dict[str, List[Path]] = {}

    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        rel_root = os.path.relpath(root, workspace)
        if rel_root == ".":
            rel_root = ""

        # Ignora arquivos de memória arquivada para poupar espaço
        if "archive" in rel_root.split(os.sep):
            continue

        valid_files = [
            Path(root) / f
            for f in sorted(files)
            if Path(f).suffix.lower() not in IGNORED_EXTS
            and not f.startswith(".")
            and not f.endswith(".tmp")
        ]

        if valid_files:
            files_by_dir[rel_root] = valid_files

    for rel_dir, file_paths in sorted(files_by_dir.items()):
        if len(lines) >= max_lines - 5:
            lines.append("... [demais arquivos omitidos para manter < 80 linhas]")
            break

        header = f"### {rel_dir}/" if rel_dir else "### / (raiz)"
        dir_lines = [header]

        for fp in file_paths:
            if len(lines) + len(dir_lines) >= max_lines - 2:
                break
            rel_file = fp.name
            symbols = extract_file_symbols(fp)
            if symbols:
                sym_str = f" [{', '.join(symbols[:3])}]"
                dir_lines.append(f"- `{rel_file}`{sym_str}")
            else:
                dir_lines.append(f"- `{rel_file}`")

        dir_lines.append("")
        lines.extend(dir_lines)

    return "\n".join(lines[:max_lines]).strip() + "\n"


def save_repo_map(
    workspace_dir: Path,
    target_path: Optional[Path] = None,
    max_lines: int = 80,
) -> Path:
    """Salva o mapa do repositório em disco."""
    workspace = workspace_dir.resolve()
    dest = target_path or (workspace / ".agents" / "memory" / "REPO_MAP.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = generate_repo_map(workspace, max_lines=max_lines)
    dest.write_text(content, encoding="utf-8")
    return dest


def main() -> int:
    ws_dir = Path.cwd()
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        ws_dir = Path(sys.argv[1])

    dest = save_repo_map(ws_dir)
    print(f"✅ REPO_MAP.md gerado com sucesso em: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
