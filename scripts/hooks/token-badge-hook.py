#!/usr/bin/env python3
"""
scripts/hooks/token-badge-hook.py
Hook PostInvocation para registrar telemetria de tokens após cada mensagem no Antigravity.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    tracker_script = Path(__file__).resolve().parent.parent / "token_tracker.py"
    if tracker_script.is_file():
        try:
            # Atualiza o relatório de telemetria silenciosamente na raiz do repositório
            subprocess.run(
                [sys.executable, str(tracker_script), "--report"],
                cwd=str(tracker_script.parent.parent),
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            pass

    # PostInvocation hook exige JSON válido (protojson) para não gerar erro no Language Server
    sys.stdout.write(json.dumps({}))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
