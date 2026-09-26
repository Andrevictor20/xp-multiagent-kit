#!/usr/bin/env python3
"""
scripts/repo_map.py
Gerador de Repo Map Ultracompacto (Padrão Aider) para o XP Multi-Agent Kit v2.
Extrai assinaturas e definições AST/Regex em árvore concisa (< 80 linhas / ~1.2k tokens)
para zerar a necessidade de chamadas de exploração cega (list_dir, grep exploratório).
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

CACHE_FILENAME: str = ".repo_map_cache.json"

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

def load_symbol_cache(cache_file: Path) -> Dict[str, Any]:
    """Carrega o cache incremental de símbolos do disco."""
    if not cache_file.is_file():
        return {"version": 1, "files": {}}
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "files" in data:
            return data
    except Exception:
        pass
    return {"version": 1, "files": {}}


def save_symbol_cache(cache_file: Path, cache_data: Dict[str, Any]) -> None:
    """Persiste o cache incremental de símbolos em disco em formato JSON."""
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(cache_data, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        pass


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


def extract_file_symbols(
    file_path: Path,
    rel_path: str = "",
    cache_data: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Roteia extração de símbolos com suporte a cache incremental por mtime/size."""
    if cache_data is not None and rel_path:
        files_cache = cache_data.setdefault("files", {})
        try:
            stat = file_path.stat()
            cached = files_cache.get(rel_path)
            if cached and cached.get("mtime") == stat.st_mtime and cached.get("size") == stat.st_size:
                return cached.get("symbols", [])
        except OSError:
            pass

    suffix = file_path.suffix.lower()
    symbols: List[str] = []
    if suffix == ".py":
        symbols = extract_python_symbols(file_path)
    elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
        symbols = extract_js_ts_symbols(file_path)

    if cache_data is not None and rel_path:
        try:
            stat = file_path.stat()
            cache_data.setdefault("files", {})[rel_path] = {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "symbols": symbols,
            }
        except OSError:
            pass

    return symbols


def generate_repo_map(
    workspace_dir: Path,
    max_lines: int = 80,
    cache_data: Optional[Dict[str, Any]] = None,
) -> str:
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
            rel_path = os.path.relpath(fp, workspace)
            symbols = extract_file_symbols(fp, rel_path=rel_path, cache_data=cache_data)
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
    cache_path: Optional[Path] = None,
) -> Path:
    """Salva o mapa do repositório em disco e atualiza o cache incremental."""
    workspace = workspace_dir.resolve()
    dest = target_path or (workspace / ".agents" / "memory" / "REPO_MAP.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    cache_file = cache_path or (workspace / ".agents" / "memory" / CACHE_FILENAME)
    cache_data = load_symbol_cache(cache_file)
    content = generate_repo_map(workspace, max_lines=max_lines, cache_data=cache_data)
    dest.write_text(content, encoding="utf-8")
    save_symbol_cache(cache_file, cache_data)
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
