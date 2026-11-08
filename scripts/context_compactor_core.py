#!/usr/bin/env python3
"""
scripts/context_compactor_core.py
Funções core de compactação de texto: remoção de ANSI, normalização de
whitespace, dedup de logs, colapso de diff, minificação JSON e estatísticas.
"""
from __future__ import annotations

import hashlib
import json
import re
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
    lines = [line.rstrip() for line in text.splitlines()]
    joined = "\n".join(lines)
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
