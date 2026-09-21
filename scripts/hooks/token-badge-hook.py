#!/usr/bin/env python3
"""
scripts/hooks/token-badge-hook.py
Hook PostInvocation para exibir a telemetria de tokens após cada mensagem no Antigravity.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    tracker_script = Path(__file__).resolve().parent.parent / "token_tracker.py"
    if not tracker_script.is_file():
        return 0

    try:
        res = subprocess.run(
            [sys.executable, str(tracker_script), "--turn"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.stdout:
            sys.stdout.write(res.stdout)
            if not res.stdout.endswith("\n"):
                sys.stdout.write("\n")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
