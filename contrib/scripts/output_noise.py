#!/usr/bin/env python3
"""
scripts/output_noise.py
Remoção de ruído decorativo de shell (B4).

Motivo: banners de MOTD, fastfetch/neofetch e decoração de prompt custam
centenas de tokens em CADA chamada de ferramenta e ficam abaixo do limiar do
tool-size-guard (2,5KB), portanto eram invisíveis à instrumentação do kit.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import List, Sequence, Tuple

try:  # importável como pacote do kit
    from scripts.kit_constants import (
        ASCII_ART_LETTER_DOMINANCE,
        SHELL_NOISE_LINE_PATTERNS,
        SHELL_NOISE_MIN_CONSECUTIVE,
    )
except ImportError:  # pragma: no cover - execução direta do script
    from kit_constants import (  # type: ignore
        ASCII_ART_LETTER_DOMINANCE,
        SHELL_NOISE_LINE_PATTERNS,
        SHELL_NOISE_MIN_CONSECUTIVE,
    )

_NOISE_RE = tuple(re.compile(p, re.IGNORECASE) for p in SHELL_NOISE_LINE_PATTERNS)
_REPEAT_RUN_RE = re.compile(r"(.)\1{3,}")


def is_ascii_art(line: str) -> bool:
    """
    Detecta linhas de ASCII art de banners (fastfetch/neofetch) que não contêm
    caracteres de desenho de caixa.

    Critério: possui uma corrida de 4+ caracteres idênticos E as letras da linha
    são dominadas por um único caractere. Saída real de comando (logs, diffs,
    resultados de teste) quase nunca tem mais de 60% das letras repetidas.
    """
    stripped = line.strip()
    if not _REPEAT_RUN_RE.search(stripped):
        return False
    letters = [c for c in stripped if c.isalpha()]
    if len(letters) < 4:
        return False
    dominant = Counter(letters).most_common(1)[0][1]
    return dominant / len(letters) >= ASCII_ART_LETTER_DOMINANCE


def is_noise_line(line: str) -> bool:
    """True quando a linha é decoração de terminal, não conteúdo de comando."""
    stripped = line.strip()
    if not stripped:
        return False
    if any(pattern.match(stripped) for pattern in _NOISE_RE):
        return True
    return is_ascii_art(stripped)


def strip_shell_noise(lines: Sequence[str]) -> Tuple[List[str], int]:
    """
    Remove blocos contíguos de ruído de shell preservando o conteúdo real.

    Blocos menores que SHELL_NOISE_MIN_CONSECUTIVE linhas são mantidos, para não
    suprimir saída legítima que por acaso contenha caracteres de desenho de caixa.
    Retorna (linhas limpas, total de linhas de ruído removidas).
    """
    kept: List[str] = []
    noise_block: List[str] = []
    removed = 0

    def drain() -> None:
        nonlocal removed
        if not noise_block:
            return
        if len(noise_block) >= SHELL_NOISE_MIN_CONSECUTIVE:
            kept.append(
                f"[... {len(noise_block)} linhas de banner/decoração de shell removidas ...]\n"
            )
            removed += len(noise_block)
        else:
            kept.extend(noise_block)
        noise_block.clear()

    for line in lines:
        normalized = line if line.endswith("\n") else line + "\n"
        if is_noise_line(line):
            noise_block.append(normalized)
        else:
            drain()
            kept.append(normalized)

    drain()
    return kept, removed


def never_worse(raw: str, filtered: str) -> str:
    """
    Garantia formal inspirada no RTK: uma saída filtrada/sanitizada
    NUNCA deve emitir mais caracteres ou tokens do que a saída original.
    Se a filtragem aumentou o tamanho, reverte imediatamente para raw.
    """
    if len(filtered) > len(raw):
        return raw
    return filtered


def clean_output(text: str) -> str:
    """Recebe o output cru e devolve o texto sem ruído decorativo com garantia never_worse."""
    cleaned, _ = strip_shell_noise(text.splitlines(keepends=True))
    result = "".join(cleaned)
    return never_worse(text, result)


def noise_stats(text: str) -> dict:
    """Métricas do ruído removido, para telemetria e auditoria."""
    lines = text.splitlines()
    cleaned, removed = strip_shell_noise(text.splitlines(keepends=True))
    original_chars = len(text)
    cleaned_chars = sum(len(line) for line in cleaned)
    return {
        "original_lines": len(lines),
        "noise_lines": removed,
        "original_chars": original_chars,
        "saved_chars": max(0, original_chars - cleaned_chars),
    }
