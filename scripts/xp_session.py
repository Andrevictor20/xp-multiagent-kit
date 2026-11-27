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

from scripts.xp_contract import get_runtime_dir, load_contract


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
    risk_level: Optional[str] = None,
    surfaces: Optional[List[str]] = None,
    spec_path: str = "",
    tests_status: str = "RED",
    tests_command: str = "python3 -m unittest discover tests",
    files_touched: Optional[List[str]] = None,
    goal: str = "",
    decisions: Optional[Dict[str, Any]] = None,
    next_step: str = "",
) -> Dict[str, Any]:
    active = load_contract() or {}
    merged_files = list(dict.fromkeys((files_touched or []) + active.get("scope_files", [])))
    merged_decisions = dict(active.get("known") or {})
    if decisions:
        merged_decisions.update(decisions)
    return {
        "task_id": task_id,
        "risk_level": risk_level or active.get("risk", "L1"),
        "goal": goal or active.get("goal", ""),
        "surfaces": surfaces or [],
        "spec_path": spec_path,
        "tests": {
            "status": tests_status,
            "command": active.get("verify_cmd") or tests_command,
        },
        "files_touched": merged_files,
        "decisions": merged_decisions,
        "dead_ends": active.get("tried", []),
        "next_step": next_step or active.get("next", ""),
        "visual_evidence": active.get("visual_evidence", []),
        "timestamp": json.loads(json.dumps(str(Path(__file__).stat().st_mtime))),
    }


def render_handoff_markdown(contract: Dict[str, Any]) -> str:
    lines = [
        f"# Session Handoff — {contract.get('task_id', 'session')}",
        "",
        f"- **Risk:** {contract.get('risk_level', 'L1')}",
        f"- **Goal:** {contract.get('goal') or 'N/A'}",
        f"- **Verify:** `{contract.get('tests', {}).get('command', '')}` ({contract.get('tests', {}).get('status', 'RED')})",
    ]
    if contract.get("next_step"):
        lines.append(f"- **Next step:** {contract['next_step']}")
    if contract.get("spec_path"):
        lines.append(f"- **Spec:** `{contract['spec_path']}`")
    lines.extend(["", "## Active Files"])
    for f in contract.get("files_touched") or []:
        lines.append(f"- `{f}`")
    if contract.get("decisions"):
        lines.extend(["", "## Verified Decisions"])
        for k, v in contract["decisions"].items():
            lines.append(f"- **{k}:** {v}")
    if contract.get("dead_ends"):
        lines.extend(["", "## Dead-Ends"])
        for d in contract["dead_ends"]:
            lines.append(f"- `{d.get('signature', '?')}`: {d.get('reason', '')}")
    if contract.get("visual_evidence"):
        lines.extend(["", "## Visual Evidence"])
        for v in contract["visual_evidence"]:
            lines.append(f"- `{v.get('path', '')}` ({v.get('note', '')})")
    return "\n".join(lines) + "\n"


def write_handoff_file(contract: Dict[str, Any], out_path: Optional[Path] = None) -> Path:
    dest = out_path or (get_runtime_dir() / "handoff.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_handoff_markdown(contract), encoding="utf-8")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Session & Handoff Tool (AC-11)")
    sub = parser.add_subparsers(dest="subcommand")

    p_compact = sub.add_parser("compact", help="Compacta texto ou arquivo de sessão")
    p_compact.add_argument("file", nargs="?", help="Arquivo para compactar")

    p_resume = sub.add_parser("resume", help="Retoma contexto da última sessão")
    p_resume.add_argument("--transcript", help="Caminho para transcript.jsonl")

    p_handoff = sub.add_parser("handoff", help="Gera handoff.md limpo entre fases")
    p_handoff.add_argument("--task-id", required=True, help="ID da tarefa delegada")
    p_handoff.add_argument("--risk", default=None, choices=["L0", "L1", "L2", "L3"], help="Nível de risco L0-L3 (padrão: contrato ativo ou L1)")
    p_handoff.add_argument("--spec", default="", help="Caminho da especificação")
    p_handoff.add_argument("--status", default="RED", choices=["RED", "GREEN"], help="Status dos testes")
    p_handoff.add_argument("--files", nargs="*", default=[], help="Arquivos alterados")
    p_handoff.add_argument("--goal", default="", help="Objetivo da fase")
    p_handoff.add_argument("--next", default="", dest="next_step", help="Próximo passo")
    p_handoff.add_argument("--out", default="", help="Caminho do handoff.md (padrão: .agents/runtime/handoff.md)")
    p_handoff.add_argument("--json", action="store_true", help="Imprime contrato JSON em vez de gravar handoff.md")

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
            task_id=args.task_id, risk_level=args.risk, spec_path=args.spec,
            tests_status=args.status, files_touched=args.files,
            goal=args.goal, next_step=args.next_step,
        )
        if args.json:
            print(json.dumps(contract, indent=2, ensure_ascii=False))
        else:
            dest = write_handoff_file(contract, Path(args.out) if args.out else None)
            print(f"Handoff gravado em: {dest}")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
