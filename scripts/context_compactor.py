#!/usr/bin/env python3
"""
context_compactor.py — Motor de Compressão e Compactação de Mensagens e Contexto.

Este módulo é um ponto de entrada que re-exporta as funções implementadas em
submódulos (core, ccr, cci) para preservar a API pública usada por testes e
por outros scripts (ex: tool-size-guard, agy-git-ops). A CLI `--file/--stdin`
continua disponível via `main()`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

# Permite execução direta como script (CLI agy-compact / xp-compact).
kit_dir = Path(__file__).resolve().parent.parent
if str(kit_dir) not in sys.path:
    sys.path.insert(0, str(kit_dir))
if not os.environ.get("KIT_ROOT"):
    os.environ["KIT_ROOT"] = str(kit_dir)

from scripts.context_compactor_core import (  # noqa: E402
    ANSI_REGEX,
    calculate_compression_stats,
    compress_diff,
    compress_json,
    compress_logs,
    compress_whitespace,
    strip_ansi_codes,
)
from scripts.context_compactor_cci import (  # noqa: E402
    compress_ci_output,
    compress_git_output,
    compress_html,
)
from scripts.context_compactor_ccr import (  # noqa: E402
    ContextualCompressorWithRetrieval,
    compress_conversation_turns,
    compact_payload,
)

# Re-exportação dos símbolos de nível de módulo usados por testes e outros scripts.
__all__ = [
    "ANSI_REGEX",
    "strip_ansi_codes",
    "compress_whitespace",
    "compress_logs",
    "compress_diff",
    "compress_json",
    "calculate_compression_stats",
    "compress_conversation_turns",
    "ContextualCompressorWithRetrieval",
    "compact_payload",
    "compress_ci_output",
    "compress_git_output",
    "compress_html",
    "main",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="XP Message & Context Compactor (CCR + Semantic Compression)"
    )
    parser.add_argument("--file", "-f", help="Arquivo para compactar")
    parser.add_argument("--expand", metavar="ID", help="Expande um payload CCR a partir do ID")
    parser.add_argument("--clean-cache", action="store_true", help="Limpa o cache local de CCR")
    parser.add_argument("--stdin", action="store_true", help="Lê conteúdo de stdin e imprime compactado")
    parser.add_argument("--json", action="store_true", dest="is_json", help="Minifica e remove nulos de payload JSON")
    parser.add_argument("--diff", action="store_true", dest="is_diff", help="Aplica colapso de contexto em diff unificado")
    parser.add_argument("--ci", action="store_true", dest="is_ci", help="Comprime logs de CI/CD isolando resumo e erros")
    parser.add_argument("--git", action="store_true", dest="is_git", help="Comprime relatórios de status/log do git")
    parser.add_argument("--html", action="store_true", dest="is_html", help="Remove tags/scripts/css de HTML e extrai texto limpo")
    parser.add_argument("--stats", action="store_true", help="Exibe estatísticas de redução de payload no stderr")

    args = parser.parse_args()

    if args.expand:
        ccr = ContextualCompressorWithRetrieval()
        content = ccr.retrieve(args.expand)
        if content:
            print(content)
        else:
            print(f"❌ Documento '{args.expand}' não encontrado no cache CCR.", file=sys.stderr)
            sys.exit(1)
    elif args.clean_cache:
        ccr = ContextualCompressorWithRetrieval()
        ccr.clean_cache()
        print("✅ Cache CCR limpo com sucesso.")
    elif args.file or args.stdin or not sys.stdin.isatty():
        if args.file:
            path = Path(args.file)
            if not path.exists():
                print(f"❌ Arquivo não encontrado: {path}", file=sys.stderr)
                sys.exit(1)
            raw = path.read_text(encoding="utf-8")
            source_name = path.name
        else:
            raw = sys.stdin.read()
            source_name = "stdin"

        if args.is_json:
            compacted = compress_json(raw)
        elif args.is_diff:
            compacted = compress_diff(raw)
        elif args.is_ci:
            compacted = compress_ci_output(raw)
        elif args.is_git:
            compacted = compress_git_output(raw)
        elif args.is_html:
            compacted = compress_html(raw)
        else:
            compacted = compact_payload(raw, source_name=source_name)

        print(compacted)

        if args.stats:
            stats = calculate_compression_stats(raw, compacted)
            print(
                f"\n[📊 Redução de tamanho: {stats['original_chars']} -> {stats['compressed_chars']} chars "
                f"({stats['reduction_percent']}% economizado / -{stats['saved_chars']} chars)]",
                file=sys.stderr,
            )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
