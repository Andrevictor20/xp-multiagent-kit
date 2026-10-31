#!/usr/bin/env python3
"""
scripts/context_retriever.py
Motor de Recuperação JIT (Just-In-Time) de Memória & Regras de Contexto.
Permite injeção cirúrgica (< 300 tokens) das regras, decisões e lições mais relevantes
para a tarefa atual, eliminando a leitura de arquivos markdown inteiros e prevenindo
a amnésia de contexto e saturação de tokens.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.memory_search import build_or_update_index, search_memory


FILE_KEYWORD_MAP = {
    "auth": ["security", "auth", "jwt", "token", "password", "seguranca"],
    "security": ["security", "secret", "owasp", "stride", "seguranca"],
    "test": ["tdd", "test", "anti-test-bypass", "atdd", "acceptance"],
    "frontend": ["frontend", "design-system", "token", "accessibility", "wcag", "css"],
    "ui": ["frontend", "design-system", "component", "mobile"],
    "db": ["database", "migration", "concurrency", "acid", "sql"],
    "database": ["database", "migration", "concurrency", "acid"],
    "api": ["api-contracts", "rest", "endpoint", "openapi"],
    "deploy": ["release", "zero-downtime", "canary", "pipeline"],
}


def derive_keywords_from_files(files: List[str]) -> List[str]:
    """Deriva tópicos e palavras-chave de governança a partir dos arquivos tocados."""
    keywords: Set[str] = set()
    for f in files:
        f_lower = f.lower().replace("\\", "/")
        path_obj = Path(f_lower)
        stem = path_obj.stem
        # Adiciona termos do nome do arquivo
        for part in re.split(r"[_\-.]+", stem):
            if len(part) >= 3 and part not in {"src", "test", "tests", "py", "ts", "js"}:
                keywords.add(part)

        # Checa mapeamento temático
        for key, mapped_terms in FILE_KEYWORD_MAP.items():
            if key in f_lower:
                keywords.update(mapped_terms)

    return list(keywords)


def estimate_tokens(text: str) -> int:
    """Estimativa rápida de tokens (média de 4 caracteres por token)."""
    return max(1, len(text) // 4)


def get_jit_context(
    workspace: Path,
    query: str = "",
    touched_files: Optional[List[str]] = None,
    max_items: int = 4,
    token_budget: int = 350,
) -> List[Dict[str, Any]]:
    """
    Recupera os itens de memória mais relevantes (lições, políticas, decisões, specs)
    com limite estrito de tokens e relevância orientada a arquivos tocados.
    """
    workspace = workspace.resolve()
    touched_files = touched_files or []

    # 1. Constrói termos de busca
    search_queries: List[str] = []
    if query.strip():
        search_queries.append(query.strip())

    file_keywords = derive_keywords_from_files(touched_files)
    if file_keywords:
        search_queries.append(" ".join(file_keywords[:6]))

    if not search_queries:
        search_queries.append("regra política lição")

    # 2. Executa buscas
    seen_identifiers: Set[str] = set()
    raw_results: List[Dict[str, Any]] = []

    for q in search_queries:
        res = search_memory(workspace, q, limit=max_items * 2)
        for item in res:
            ident = item.get("identifier") or item.get("title") or item.get("content")[:30]
            if ident not in seen_identifiers:
                seen_identifiers.add(ident)
                raw_results.append(item)

    # 3. Boost de relevância com base nos arquivos tocados
    def score_item(item: Dict[str, Any]) -> float:
        score = item.get("rank", 0.0)
        src = item.get("source_file", "").lower()
        title = item.get("title", "").lower()
        content = item.get("content", "").lower()

        # Prioriza itens com categorias acionáveis
        cat = item.get("category", "")
        if cat in {"policy", "decision", "lesson", "spec"}:
            score -= 10.0

        # Boost se arquivo tocado correlaciona com o arquivo fonte da regra
        for kw in file_keywords:
            if kw in src or kw in title:
                score -= 5.0
            elif kw in content:
                score -= 2.0

        return score

    raw_results.sort(key=score_item)

    # 4. Aplica limite de itens e teto de tokens
    final_items: List[Dict[str, Any]] = []
    used_tokens = 0

    for item in raw_results:
        if len(final_items) >= max_items:
            break

        c_tokens = estimate_tokens(item.get("content", ""))
        # Se ultrapassar o orçamento mas for o primeiro item, trunca cirurgicamente
        if used_tokens + c_tokens > token_budget and final_items:
            continue

        if used_tokens + c_tokens > token_budget and not final_items:
            # Trunca o conteúdo para caber no orçamento
            max_chars = token_budget * 4
            item["content"] = item["content"][:max_chars] + "..."
            c_tokens = estimate_tokens(item["content"])

        final_items.append(item)
        used_tokens += c_tokens

    return final_items


def format_jit_prompt(items: List[Dict[str, Any]]) -> str:
    """Formata os itens recuperados em bloco Markdown limpo para injeção em prompts."""
    if not items:
        return ""

    lines: List[str] = ["### 🧠 Contexto & Regras Relevantes (JIT Memory)"]
    for item in items:
        cat = item.get("category", "info").upper()
        ident = item.get("identifier", "")
        src = item.get("source_file", "")
        line_no = item.get("line_number", 1)
        content = item.get("content", "").strip()

        loc = f"[{src}#L{line_no}]"
        badge = f"**[{cat}{': ' + ident if ident else ''}]**"
        lines.append(f"- {badge} {loc} {content}")

    return "\n".join(lines)


def format_jit_json(items: List[Dict[str, Any]]) -> str:
    """Retorna os itens recuperados como string JSON estruturada."""
    return json.dumps(items, indent=2, ensure_ascii=False)


def format_jit_compact(items: List[Dict[str, Any]]) -> str:
    """Formata em linhas de sumário compactas de 1 linha por item."""
    if not items:
        return "Nenhum contexto JIT relevante encontrado."
    lines: List[str] = []
    for it in items:
        lines.append(f"[{it.get('category', '').upper()}] {it.get('title', '')} ({it.get('source_file')}#L{it.get('line_number')})")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Motor de Recuperação JIT de Memória & Regras de Contexto para XP Multi-Agent Kit"
    )
    parser.add_argument("query", nargs="?", default="", help="Consulta conceitual ou tarefa ativa")
    parser.add_argument("--workspace", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--files", nargs="*", default=[], help="Arquivos tocados na tarefa")
    parser.add_argument("--max-items", type=int, default=4, help="Número máximo de regras/itens (padrão: 4)")
    parser.add_argument("--budget", type=int, default=350, help="Orçamento máximo em tokens (padrão: 350)")
    parser.add_argument(
        "--format",
        choices=["prompt", "json", "compact"],
        default="prompt",
        help="Formato de saída (padrão: prompt)",
    )

    args = parser.parse_args()
    ws = Path(args.workspace)

    items = get_jit_context(
        workspace=ws,
        query=args.query,
        touched_files=args.files,
        max_items=args.max_items,
        token_budget=args.budget,
    )

    if args.format == "json":
        print(format_jit_json(items))
    elif args.format == "compact":
        print(format_jit_compact(items))
    else:
        print(format_jit_prompt(items))

    return 0


if __name__ == "__main__":
    sys.exit(main())
