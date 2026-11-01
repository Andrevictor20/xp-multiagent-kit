#!/usr/bin/env python3
"""
scripts/context_compactor_ccr.py
Compressão Contextual com Recuperação (CCR) e pipeline unificado de
compactação de payload, incluindo micro-compactação de turnos de conversa.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.context_compactor_core import (  # noqa: E402
    compress_logs,
    compress_whitespace,
    strip_ansi_codes,
)


def compress_conversation_turns(
    messages: List[Dict[str, Any]],
    budget_chars: int = 2000,
    ccr: Optional["ContextualCompressorWithRetrieval"] = None,
) -> List[Dict[str, Any]]:
    """
    Micro-compactação de histórico de conversação (estilo Claude Code / AGY):
    Compacta saídas de ferramentas em turnos mais antigos que excederem o budget,
    preservando as mensagens do usuário e a resposta final do assistente intactas.
    """
    if not messages:
        return []

    compactor = ccr or ContextualCompressorWithRetrieval(max_inline_chars=budget_chars)
    compacted_messages = []

    cutoff_index = max(0, len(messages) - 2)

    for i, msg in enumerate(messages):
        msg_copy = dict(msg)
        content = msg_copy.get("content", "")

        if i < cutoff_index and isinstance(content, str) and len(content) > budget_chars:
            source = msg_copy.get("tool_name", f"turn_{i}")
            compacted_content, _ = compactor.compress(source, content)
            msg_copy["content"] = compacted_content

        compacted_messages.append(msg_copy)

    return compacted_messages


class ContextualCompressorWithRetrieval:
    """
    Implementação de Contextual Compression with Retrieval (CCR).
    Substitui payloads volumosos por stubs compactos referenciando o cache local.
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_inline_chars: int = 1500,
    ) -> None:
        self.cache_dir = Path(
            cache_dir or os.environ.get(
                "KIT_CCR_CACHE_DIR",
                os.path.expanduser("~/.gemini/antigravity-cli/cache/ccr"),
            )
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_inline_chars = max_inline_chars

    def compress(self, source_name: str, content: str) -> Tuple[str, str]:
        """Comprime o conteúdo salvando-o no cache se exceder o limite inline."""
        clean_content = compress_whitespace(strip_ansi_codes(content))
        if len(clean_content) <= self.max_inline_chars:
            return clean_content, ""

        content_hash = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()[:12]
        doc_id = f"ccr_{content_hash}"
        cache_file = self.cache_dir / f"{doc_id}.log"

        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(clean_content)

        lines = clean_content.splitlines()
        first_lines = "\n".join(lines[:3])
        last_lines = "\n".join(lines[-2:]) if len(lines) > 5 else ""

        preview = f"{first_lines}\n...\n{last_lines}" if last_lines else first_lines
        stub = (
            f"[CCR_COMPACT id={doc_id} source={source_name} | {len(lines)} lines, {len(clean_content)} chars]\n"
            f"{preview}\n"
            f"[Full output cached: use agy-compact --expand {doc_id} to view full content]"
        )
        return stub, doc_id

    def retrieve(self, doc_id: str) -> Optional[str]:
        """Recupera o conteúdo original do cache a partir do doc_id."""
        cache_file = self.cache_dir / f"{doc_id}.log"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def clean_cache(self) -> None:
        """Limpa todo o diretório de cache CCR."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)


def compact_payload(
    raw_content: str,
    source_name: str = "payload",
    max_inline_chars: int = 2500,
) -> str:
    """Pipeline unificado de compactação de payload de envio."""
    if not raw_content:
        return ""

    cleaned = strip_ansi_codes(raw_content)
    cleaned = compress_whitespace(cleaned)
    cleaned = compress_logs(cleaned)

    if cleaned.startswith("diff --git") or "\n@@ " in cleaned:
        from scripts.context_compactor_core import compress_diff  # noqa: E402

        cleaned = compress_diff(cleaned)

    if len(cleaned) > max_inline_chars:
        ccr = ContextualCompressorWithRetrieval(max_inline_chars=max_inline_chars)
        compacted, _ = ccr.compress(source_name, cleaned)
        return compacted

    return cleaned
