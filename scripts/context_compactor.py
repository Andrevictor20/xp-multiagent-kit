#!/usr/bin/env python3
"""
context_compactor.py — Motor de Compressão e Compactação de Mensagens e Contexto.

Inspirado no Claude Code (/compact, microcompact), Headroom (CCR, SmartCrusher) e SuperCompress.
Reduz o consumo de tokens na transmissão de mensagens via:
1. Limpeza sem perda de ANSI escape codes e normalização de whitespace.
2. Deduplicação inteligente de linhas consecutivas em logs e outputs de terminal.
3. Colapso de linhas de contexto inalteradas em diffs de código.
4. Compressão Contextual com Recuperação (CCR) armazenando saídas massivas em cache local.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

ANSI_REGEX = re.compile(
    r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\r"
)


def strip_ansi_codes(text: str) -> str:
    """Remove códigos de escape ANSI e sequências de controle de terminal."""
    if not text:
        return ""
    return ANSI_REGEX.sub("", text)


def compress_whitespace(text: str) -> str:
    """Remove espaços em branco supérfluos e normaliza sequências excessivas de quebras de linha."""
    if not text:
        return ""
    # Strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.splitlines()]
    joined = "\n".join(lines)
    # Compress 3 or more consecutive newlines into exactly two
    joined = re.sub(r"\n{3,}", "\n\n", joined)
    return joined.strip()


def compress_logs(log_text: str) -> str:
    """Deduplica linhas consecutivas idênticas em logs de execução."""
    if not log_text:
        return ""
    lines = log_text.splitlines()
    if not lines:
        return ""

    compressed_lines: List[str] = []
    current_line = lines[0]
    count = 1

    for line in lines[1:]:
        if line == current_line:
            count += 1
        else:
            if count > 1:
                compressed_lines.append(f"{current_line} (repeated {count}x)")
            else:
                compressed_lines.append(current_line)
            current_line = line
            count = 1

    if count > 1:
        compressed_lines.append(f"{current_line} (repeated {count}x)")
    else:
        compressed_lines.append(current_line)

    return "\n".join(compressed_lines)


def compress_diff(diff_text: str, max_context_lines: int = 2) -> str:
    """
    Comprime diffs unificados mantendo cabeçalhos e alterações (+/-),
    colapsando blocos longos de linhas de contexto inalteradas.
    """
    if not diff_text:
        return ""

    lines = diff_text.splitlines()
    out_lines: List[str] = []
    context_buffer: List[str] = []

    def flush_context():
        nonlocal context_buffer
        if not context_buffer:
            return
        if len(context_buffer) <= (max_context_lines * 2):
            out_lines.extend(context_buffer)
        else:
            out_lines.extend(context_buffer[:max_context_lines])
            out_lines.append("   [... unchanged lines collapsed ...]")
            out_lines.extend(context_buffer[-max_context_lines:])
        context_buffer = []

    for line in lines:
        if line.startswith("diff ") or line.startswith("--- ") or line.startswith("+++ ") or line.startswith("@@"):
            flush_context()
            out_lines.append(line)
        elif line.startswith("+") or line.startswith("-"):
            flush_context()
            out_lines.append(line)
        elif line.startswith(" ") or not line:
            context_buffer.append(line)
        else:
            flush_context()
            out_lines.append(line)

    flush_context()
    return "\n".join(out_lines)


def compress_json(
    raw_json: Union[str, Dict[str, Any], List[Any]],
    remove_nulls: bool = True,
) -> str:
    """
    Minifica e comprime payloads JSON removendo espaços desnecessários
    e opcionalmente chaves nulas (null pruning).
    """
    if isinstance(raw_json, str):
        try:
            data = json.loads(raw_json)
        except Exception:
            return raw_json
    else:
        data = raw_json

    def _prune(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: _prune(v)
                for k, v in obj.items()
                if (v is not None if remove_nulls else True)
            }
        elif isinstance(obj, list):
            return [_prune(elem) for elem in obj]
        return obj

    cleaned_data = _prune(data) if remove_nulls else data
    return json.dumps(cleaned_data, separators=(",", ":"), ensure_ascii=False)


def calculate_compression_stats(
    original_text: str,
    compressed_text: str,
) -> Dict[str, Union[int, float]]:
    """Calcula métricas detalhadas de economia de caracteres e percentual de compressão."""
    orig_len = len(original_text)
    comp_len = len(compressed_text)
    saved = orig_len - comp_len
    pct = round((saved / orig_len) * 100, 1) if orig_len > 0 else 0.0
    return {
        "original_chars": orig_len,
        "compressed_chars": comp_len,
        "saved_chars": saved,
        "reduction_percent": pct,
    }


def compress_conversation_turns(
    messages: List[Dict[str, Any]],
    budget_chars: int = 2000,
    ccr: Optional[ContextualCompressorWithRetrieval] = None,
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

    # Mantém os últimos 2 turnos sem compactação agressiva
    cutoff_index = max(0, len(messages) - 2)

    for i, msg in enumerate(messages):
        msg_copy = dict(msg)
        content = msg_copy.get("content", "")

        # Se for um turno anterior de tool ou output volumoso que exceda o budget
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

    # 1. Strip ANSI
    cleaned = strip_ansi_codes(raw_content)

    # 2. Compress whitespace
    cleaned = compress_whitespace(cleaned)

    # 3. Compress logs se houver repetições
    cleaned = compress_logs(cleaned)

    # 4. Se for diff, aplica compressão de diff
    if cleaned.startswith("diff --git") or "\n@@ " in cleaned:
        cleaned = compress_diff(cleaned)

    # 5. Se ainda exceder budget, aplica CCR
    if len(cleaned) > max_inline_chars:
        ccr = ContextualCompressorWithRetrieval(max_inline_chars=max_inline_chars)
        compacted, _ = ccr.compress(source_name, cleaned)
        return compacted

    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(
        description="XP Message & Context Compactor (CCR + Semantic Compression)"
    )
    parser.add_argument(
        "--file", "-f", help="Arquivo para compactar"
    )
    parser.add_argument(
        "--expand", metavar="ID", help="Expande um payload CCR a partir do ID"
    )
    parser.add_argument(
        "--clean-cache", action="store_true", help="Limpa o cache local de CCR"
    )
    parser.add_argument(
        "--stdin", action="store_true", help="Lê conteúdo de stdin e imprime compactado"
    )
    parser.add_argument(
        "--json", action="store_true", dest="is_json", help="Minifica e remove nulos de payload JSON"
    )
    parser.add_argument(
        "--diff", action="store_true", dest="is_diff", help="Aplica colapso de contexto em diff unificado"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Exibe estatísticas de redução de payload no stderr"
    )

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
