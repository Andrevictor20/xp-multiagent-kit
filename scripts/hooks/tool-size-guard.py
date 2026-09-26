#!/usr/bin/env python3
"""
scripts/hooks/tool-size-guard.py
Hook PostToolUse para auditar payloads de ferramentas e alertar contra saídas infladas.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def clamp_output_text(
    text: str, max_head: int = 15, max_tail: int = 25, max_chars: int = 2500
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
    """Audita o payload da ferramenta e registra alerta se exceder limites."""
    content = ""
    if isinstance(data, dict):
        content = str(
            data.get("output")
            or data.get("result")
            or data.get("content")
            or ""
        )

    char_count = len(content)
    line_count = len(content.splitlines())
    is_flooding = char_count > 2500 or line_count > 50
    tool_name = (
        data.get("tool_name", "unknown") if isinstance(data, dict) else "unknown"
    )

    clamped_content = None
    if is_flooding:
        target_dir = scratch_dir or Path(
            os.environ.get("KIT_SCRATCH_DIR", "/tmp/antigravity-scratch")
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        log_file = target_dir / "tool_warnings.log"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(
                f"⚠️ [TOOL FLOOD WARNING] {tool_name}: {char_count} chars, {line_count} linhas. Considere usar agy-sanitize ou agy-compact.\n"
            )

        backup_file = target_dir / "last_tool_output.log"
        backup_file.write_text(content, encoding="utf-8")

        clamped_text, was_clamped = clamp_output_text(content)
        if was_clamped:
            clamped_content = clamped_text

        try:
            from scripts.context_compactor import compact_payload

            compact_payload(
                content,
                source_name=f"post_tool_{tool_name}",
                max_inline_chars=2000,
            )
        except Exception:
            pass

    result: Dict[str, Any] = {
        "is_flooding": is_flooding,
        "char_count": char_count,
        "line_count": line_count,
        "tool_name": tool_name,
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
