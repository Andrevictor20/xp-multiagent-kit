#!/usr/bin/env python3
"""
scripts/hooks/token-badge-hook.py
Hook PostInvocation: registra o turno na telemetria local e atualiza o relatório.

D3: o registro local (turn_telemetry) funciona em qualquer IDE/CLI, inclusive
onde não há Language Server RPC. O tracker do Antigravity continua sendo usado
quando disponível, para a cota oficial ao vivo.
XP Multi-Agent Kit v2
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

kit_dir = Path(__file__).resolve().parent.parent.parent
if str(kit_dir) not in sys.path:
    sys.path.insert(0, str(kit_dir))
if not os.environ.get("KIT_ROOT"):
    os.environ["KIT_ROOT"] = str(kit_dir)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def record_local_turn(payload: dict) -> None:
    """Grava o turno na telemetria local; falha silenciosa nunca quebra o hook."""
    try:
        from scripts.turn_telemetry import record_turn

        tool_calls = payload.get("toolCalls") or payload.get("tool_calls") or 0
        session_id = payload.get("sessionId") or payload.get("session_id")
        transcript_path = None
        try:
            from scripts.token_tracker import find_active_session
            s_id, t_path, _ = find_active_session()
            if not session_id:
                session_id = s_id
            transcript_path = t_path
        except Exception:
            pass

        tool_chars = int(payload.get("toolChars") or payload.get("tool_chars") or 0)
        response_chars = int(payload.get("responseChars") or payload.get("response_chars") or 0)
        history_chars = int(payload.get("historyChars") or payload.get("history_chars") or 0)

        # Se o hook não recebeu os caracteres via stdin, extrai do transcript da IDE
        if (tool_chars == 0 and response_chars == 0) and transcript_path and Path(transcript_path).is_file():
            try:
                from scripts.token_tracker import load_transcript, calculate_turn_stats
                from scripts.kit_constants import CHARS_PER_TOKEN
                steps = load_transcript(Path(transcript_path))
                turn = calculate_turn_stats(steps)
                tool_calls = tool_calls or len([
                    s for s in steps
                    if s.get("type") not in ("USER_INPUT", "PLANNER_RESPONSE", "EPHEMERAL_MESSAGE", "SYSTEM_MESSAGE")
                ])
                tool_chars = turn.tool_tokens * CHARS_PER_TOKEN
                response_chars = turn.model_output_tokens * CHARS_PER_TOKEN
                total_chars = sum(len(str(s.get("content", ""))) for s in steps)
                history_chars = max(0, total_chars - tool_chars - response_chars)
            except Exception:
                pass

        record_turn(
            risk_level=str(payload.get("riskLevel") or payload.get("risk_level") or "L1"),
            tool_calls=int(tool_calls),
            tool_chars=tool_chars,
            response_chars=response_chars,
            history_chars=history_chars,
            session_id=session_id,
        )
    except Exception:
        pass


def run_live_report() -> None:
    """Atualiza o relatório oficial quando o tracker do Antigravity está disponível."""
    tracker_script = SCRIPTS_DIR / "token_tracker.py"
    if not tracker_script.is_file():
        return
    try:
        # Executa no workspace atual para atualizar o TOKEN_TELEMETRY.md do projeto ativo
        subprocess.run(
            [sys.executable, str(tracker_script), "--report"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        pass


def main() -> int:
    payload: dict = {}
    try:
        raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw_input.strip():
            loaded = json.loads(raw_input)
            if isinstance(loaded, dict):
                payload = loaded
    except Exception:
        payload = {}

    record_local_turn(payload)
    run_live_report()

    # PostInvocation hook exige JSON válido (protojson) para não gerar erro no Language Server
    sys.stdout.write(json.dumps({}))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
