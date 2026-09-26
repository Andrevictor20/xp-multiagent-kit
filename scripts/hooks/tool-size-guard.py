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

        try:
            from scripts.context_compactor import compact_payload

            compact_payload(
                content,
                source_name=f"post_tool_{tool_name}",
                max_inline_chars=2000,
            )
        except Exception:
            pass

    return {
        "is_flooding": is_flooding,
        "char_count": char_count,
        "line_count": line_count,
        "tool_name": tool_name,
    }


def main() -> int:
    try:
        raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw_input:
            data = json.loads(raw_input)
            process_tool_payload(data)
    except Exception:
        pass

    sys.stdout.write(json.dumps({}))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
