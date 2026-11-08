#!/usr/bin/env python3
"""
scripts/context_compactor_cci.py
Compactação de saídas de CI/CD, logs do git e extração de texto de HTML.
"""
from __future__ import annotations

import re
from typing import List, Optional

from scripts.context_compactor_core import (  # noqa: E402
    compress_whitespace,
    strip_ansi_codes,
)


def compress_ci_output(ci_text: str, max_error_lines: int = 30) -> str:
    """
    Comprime logs de CI/CD (GitHub Actions, etc.) eliminando ruído de steps
    bem-sucedidos (setup, checkout, teardown, docker cache) e isolando
    estritamente o resumo do job, o step que falhou e o stacktrace relevante.
    """
    if not ci_text:
        return ""

    clean_text = strip_ansi_codes(ci_text)
    lines = clean_text.splitlines()
    if not lines:
        return ""

    noise_patterns = [
        re.compile(r"^\d{4}-\d{2}-\d{2}T.*?Z\s+##\[group\]"),
        re.compile(r"^\d{4}-\d{2}-\d{2}T.*?Z\s+##\[endgroup\]"),
        re.compile(r"^\d{4}-\d{2}-\d{2}T.*?Z\s+Set up job", re.IGNORECASE),
        re.compile(r"^\d{4}-\d{2}-\d{2}T.*?Z\s+Run actions/(?:checkout|setup-.*)@v\d+", re.IGNORECASE),
        re.compile(r"^\d{4}-\d{2}-\d{2}T.*?Z\s+Post Run actions/", re.IGNORECASE),
        re.compile(r"^\d{4}-\d{2}-\d{2}T.*?Z\s+Complete job", re.IGNORECASE),
        re.compile(r"^Ubuntu \d+\.\d+", re.IGNORECASE),
    ]

    filtered_lines: List[str] = []
    in_group = False

    for line in lines:
        stripped = line.strip()
        if "##[group]" in stripped:
            in_group = True
            continue
        if "##[endgroup]" in stripped:
            in_group = False
            continue
        if in_group:
            continue

        is_noise = False
        for np in noise_patterns:
            if np.search(stripped):
                is_noise = True
                break
        if not is_noise:
            filtered_lines.append(line)

    if not filtered_lines:
        return "[CI Output: Clean / No failure detected]"

    if len(filtered_lines) > max_error_lines:
        error_indices = [
            i for i, l in enumerate(filtered_lines)
            if re.search(r"##\[error\]|FAIL|ERROR|FATAL|Exception|Error:", l, re.IGNORECASE)
        ]
        if error_indices:
            first_err = max(0, error_indices[0] - 2)
            retained = filtered_lines[first_err:]
            if len(retained) > max_error_lines:
                retained = retained[:max_error_lines]
            return f"[... {first_err} lines omitted ...]\n" + "\n".join(retained)
        else:
            return f"[... {len(filtered_lines) - max_error_lines} lines omitted ...]\n" + "\n".join(filtered_lines[-max_error_lines:])

    return "\n".join(filtered_lines)


def compress_git_output(git_text: str, max_items: int = 15) -> str:
    """
    Comprime relatórios de status/log do git, colapsando listas longas
    de arquivos não rastreados (untracked) ou arquivos modificados repetitivos.
    """
    if not git_text:
        return ""

    clean = strip_ansi_codes(git_text)
    lines = clean.splitlines()
    if len(lines) <= max_items:
        return clean

    out: List[str] = []
    untracked_buffer: List[str] = []
    in_untracked = False

    for line in lines:
        if "Untracked files:" in line:
            in_untracked = True
            out.append(line)
            continue

        if in_untracked:
            if line.startswith("\t") or line.startswith("  "):
                untracked_buffer.append(line)
                continue
            else:
                if untracked_buffer:
                    if len(untracked_buffer) > max_items:
                        out.extend(untracked_buffer[:max_items])
                        omitted = len(untracked_buffer) - max_items
                        out.append(f"\t[... {omitted} untracked files omitted to save tokens ...]")
                    else:
                        out.extend(untracked_buffer)
                    untracked_buffer = []
                in_untracked = False
                out.append(line)
        else:
            out.append(line)

    if untracked_buffer:
        if len(untracked_buffer) > max_items:
            out.extend(untracked_buffer[:max_items])
            omitted = len(untracked_buffer) - max_items
            out.append(f"\t[... {omitted} untracked files omitted to save tokens ...]")
        else:
            out.extend(untracked_buffer)

    return "\n".join(out)


def compress_html(html_text: str, max_chars: int = 10000) -> str:
    """
    Remove blocos pesados de HTML bruto (<script>, <style>, <svg>, comentários)
    e extrai o conteúdo semântico legível (títulos, parágrafos, listas) formatado
    em texto limpo para evitar inundação de tokens em chamadas web/curl.
    """
    if not html_text:
        return ""

    text = html_text
    text = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<svg\b[^<]*(?:(?!<\/svg>)<[^<]*)*<\/svg>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<noscript\b[^<]*(?:(?!<\/noscript>)<[^<]*)*<\/noscript>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<(?:h[1-6]|p|div|tr|li|blockquote|header|footer)\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\/(?:h[1-6]|p|div|tr|li|blockquote|header|footer)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*\/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", "\"")
    )
    clean = compress_whitespace(text)
    if len(clean) > max_chars:
        return clean[:max_chars] + f"\n\n[... {len(clean) - max_chars} characters truncated by agy-compact --html ...]"
    return clean
