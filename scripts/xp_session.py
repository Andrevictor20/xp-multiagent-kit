#!/usr/bin/env python3
"""scripts/xp_session.py — Consolidador de sessão, retomada e handoff (AC-11)
Substitui ferramentas avulsas de sessão por uma interface unificada em stdlib.
Limite estrito: <= 200 linhas.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.xp_contract import get_runtime_dir


def compact_session_text(text: str, max_chars: int = 1500) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if sum(len(l) for l in lines) <= max_chars:
        return "\n".join(lines)
    head = lines[:10]
    tail = lines[-10:] if len(lines) > 20 else []
    return "\n".join(head) + f"\n[... {max(0, len(lines) - 20)} linhas compactadas ...]\n" + "\n".join(tail)


def resume_session(transcript_path: Optional[str] = None) -> Dict[str, Any]:
    rdir = get_runtime_dir()
    tfile = Path(transcript_path) if transcript_path else (rdir / "transcript.jsonl")
    if not tfile.is_file():
        return {"status": "NO_PREVIOUS_SESSION", "summary": "", "steps_count": 0}

    steps: List[Dict[str, Any]] = []
    for line in tfile.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            try:
                steps.append(json.loads(line.strip()))
            except Exception:
                pass

    last_user = ""
    for s in reversed(steps):
        if s.get("type") in ("USER_INPUT", "user"):
            last_user = s.get("content", "")
            break

    return {
        "status": "RESUMED",
        "steps_count": len(steps),
        "latest_prompt": last_user[:200],
        "summary": f"Sessão retomada com {len(steps)} passos registrados.",
    }


def create_handoff_contract(
    task_id: str,
    risk_level: str = "L1",
    surfaces: Optional[List[str]] = None,
    spec_path: str = "",
    tests_status: str = "RED",
    tests_command: str = "python3 -m unittest discover tests",
    files_touched: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "risk_level": risk_level,
        "surfaces": surfaces or [],
        "spec_path": spec_path,
        "tests": {
            "status": tests_status,
            "command": tests_command,
        },
        "files_touched": files_touched or [],
        "timestamp": json.loads(json.dumps(str(Path(__file__).stat().st_mtime))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Session & Handoff Tool (AC-11)")
    sub = parser.add_subparsers(dest="subcommand")

    p_compact = sub.add_parser("compact", help="Compacta texto ou arquivo de sessão")
    p_compact.add_argument("file", nargs="?", help="Arquivo para compactar")

    p_resume = sub.add_parser("resume", help="Retoma contexto da última sessão")
    p_resume.add_argument("--transcript", help="Caminho para transcript.jsonl")

    p_handoff = sub.add_parser("handoff", help="Gera contrato estruturado de handoff")
    p_handoff.add_argument("--task-id", required=True, help="ID da tarefa delegada")
    p_handoff.add_argument("--risk", default="L1", help="Nível de risco L0-L3")
    p_handoff.add_argument("--spec", default="", help="Caminho da especificação")
    p_handoff.add_argument("--status", default="RED", choices=["RED", "GREEN"], help="Status dos testes")
    p_handoff.add_argument("--files", nargs="*", default=[], help="Arquivos alterados")

    args = parser.parse_args()
    if args.subcommand == "compact":
        if args.file and Path(args.file).is_file():
            txt = Path(args.file).read_text(encoding="utf-8")
        else:
            txt = sys.stdin.read() if not sys.stdin.isatty() else ""
        print(compact_session_text(txt))
        return 0
    elif args.subcommand == "resume":
        res = resume_session(args.transcript)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    elif args.subcommand == "handoff":
        contract = create_handoff_contract(
            task_id=args.task_id,
            risk_level=args.risk,
            spec_path=args.spec,
            tests_status=args.status,
            files_touched=args.files,
        )
        print(json.dumps(contract, indent=2, ensure_ascii=False))
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
