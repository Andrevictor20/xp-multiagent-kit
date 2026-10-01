#!/usr/bin/env python3
"""
scripts/hooks/tool-size-guard.py
Hook PostToolUse para auditar payloads de ferramentas e alertar contra saídas infladas.

Ordem de processamento: primeiro remove ruído decorativo de shell (banner/MOTD,
que fica abaixo do limiar de tamanho e era invisível à auditoria), depois mede
e trunca o que ainda exceder o orçamento.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

kit_dir = Path(__file__).resolve().parent.parent.parent
if str(kit_dir) not in sys.path:
    sys.path.insert(0, str(kit_dir))
if not os.environ.get("KIT_ROOT"):
    os.environ["KIT_ROOT"] = str(kit_dir)

from scripts.kit_constants import (  # noqa: E402
    SANITIZE_HEAD_LINES,
    SANITIZE_TAIL_LINES,
    TOOL_OUTPUT_MAX_CHARS,
    TOOL_OUTPUT_MAX_LINES,
    runtime_dir,
)
from scripts.output_noise import clean_output, noise_stats  # noqa: E402


def clamp_output_text(
    text: str,
    max_head: int = SANITIZE_HEAD_LINES + 5,
    max_tail: int = SANITIZE_TAIL_LINES,
    max_chars: int = TOOL_OUTPUT_MAX_CHARS,
) -> Tuple[str, bool]:
    """
    Trunca saídas extensas de ferramentas preservando o início e fim (resumos/erros).
    """
    lines = text.splitlines()
    char_count = len(text)
    if len(lines) <= (max_head + max_tail) and char_count <= max_chars:
        return text, False

    head_lines = lines[:max_head]
    tail_lines = lines[-max_tail:] if max_tail > 0 else []
    omitted_lines = max(0, len(lines) - max_head - max_tail)
    head_char_sum = sum(len(l) for l in head_lines)
    tail_char_sum = sum(len(l) for l in tail_lines)
    omitted_chars = max(0, char_count - head_char_sum - tail_char_sum)

    clamp_marker = (
        f"\n[... Omitidas {omitted_lines} linhas ({omitted_chars} chars) "
        f"pelo PostTool Output Clamp ...]\n"
    )
    clamped = "\n".join(head_lines) + clamp_marker + "\n".join(tail_lines)
    return clamped, True


def process_tool_payload(
    data: Dict[str, Any], scratch_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """Remove ruído de shell, audita o payload e registra alerta se exceder limites."""
    content = ""
    if isinstance(data, dict):
        content = str(
            data.get("output")
            or data.get("result")
            or data.get("content")
            or ""
        )

    # B4: banner/MOTD é removido ANTES da medição de tamanho
    noise = noise_stats(content)
    denoised = clean_output(content) if noise["noise_lines"] else content

    char_count = len(denoised)
    line_count = len(denoised.splitlines())
    is_flooding = char_count > TOOL_OUTPUT_MAX_CHARS or line_count > TOOL_OUTPUT_MAX_LINES
    tool_name = (
        data.get("tool_name", "unknown") if isinstance(data, dict) else "unknown"
    )

    clamped_content = None
    if is_flooding:
        target_dir = scratch_dir or Path(
            os.environ.get("KIT_SCRATCH_DIR") or (runtime_dir() / "scratch")
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        log_file = target_dir / "tool_warnings.log"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(
                f"⚠️ [TOOL FLOOD WARNING] {tool_name}: {char_count} chars, {line_count} linhas "
                f"(ruído de shell removido: {noise['noise_lines']} linhas / {noise['saved_chars']} chars). "
                f"Considere usar agy-sanitize ou agy-compact.\n"
            )

        backup_file = target_dir / "last_tool_output.log"
        backup_file.write_text(content, encoding="utf-8")

        clamped_text, was_clamped = clamp_output_text(denoised)
        if was_clamped:
            clamped_content = clamped_text

        try:
            from scripts.context_compactor import compact_payload

            compact_payload(
                denoised,
                source_name=f"post_tool_{tool_name}",
                max_inline_chars=2000,
            )
        except Exception:
            pass
    elif noise["noise_lines"]:
        # Houve economia mesmo sem flood: devolve o output já limpo
        clamped_content = denoised

    result: Dict[str, Any] = {
        "is_flooding": is_flooding,
        "char_count": char_count,
        "line_count": line_count,
        "tool_name": tool_name,
        "noise_lines_removed": noise["noise_lines"],
        "noise_chars_saved": noise["saved_chars"],
    }
    if clamped_content is not None:
        result["clamped_content"] = clamped_content
        result["overwrite"] = {"output": clamped_content}

    return result


def main() -> int:
    output_resp = {}
    try:
        raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw_input:
            data = json.loads(raw_input)
            payload_res = process_tool_payload(data)
            if "overwrite" in payload_res:
                output_resp = {"overwrite": payload_res["overwrite"]}
    except Exception:
        pass

    sys.stdout.write(json.dumps(output_resp, ensure_ascii=False))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
