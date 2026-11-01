#!/usr/bin/env python3
"""scripts/xp_contract.py — Contrato e estado de execução do XP Multi-Agent Kit (AC-1)
Mantém .agents/runtime/run.json como a memória compilada do loop.
Limite estrito: <= 150 linhas.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_runtime_dir() -> Path:
    env_dir = os.environ.get("KIT_RUNTIME_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
    else:
        p = Path(__file__).resolve().parent.parent / ".agents" / "runtime"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_runtime_contract_path() -> Path:
    return get_runtime_dir() / "run.json"


def init_contract(
    risk: str = "L1", goal: str = "", acs: Optional[List[str]] = None,
    scope_files: Optional[List[str]] = None, constraints: Optional[List[str]] = None,
    approval_required: Optional[List[str]] = None, verify_cmd: str = "",
    checks: Optional[List[str]] = None, max_attempts: int = 3, refactor: bool = False,
    known: Optional[Dict[str, Any]] = None, next_step: str = "", never: Optional[List[str]] = None,
) -> Dict[str, Any]:
    contract = {
        "risk": risk.upper(), "goal": goal, "acs": acs or [],
        "scope_files": scope_files or [], "constraints": constraints or [],
        "approval_required": approval_required or [], "verify_cmd": verify_cmd,
        "checks": checks or [], "max_attempts": max_attempts, "refactor": refactor,
        "tried": [], "known": known or {}, "next": next_step, "never": never or [],
    }
    save_contract(contract)
    return contract


def load_contract() -> Dict[str, Any]:
    path = get_runtime_contract_path()
    if not path.is_file():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_contract(contract: Dict[str, Any]) -> Path:
    path = get_runtime_contract_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)
    return path


def record_dead_end(signature: str, reason: str, **extra: Any) -> None:
    contract = load_contract()
    if not contract:
        contract = init_contract(risk="L1", goal="Implicit contract for dead ends")
    tried = contract.setdefault("tried", [])
    import time
    for item in tried:
        if isinstance(item, dict) and item.get("signature") == signature:
            item["count"] = item.get("count", 1) + 1
            item["last_seen"] = round(time.time(), 3)
            if reason:
                item["reason"] = reason
            item.update(extra)
            save_contract(contract)
            return
    entry = {"signature": signature, "reason": reason, "count": 1, "last_seen": round(time.time(), 3)}
    entry.update(extra)
    tried.append(entry)
    save_contract(contract)


def add_never(item: str) -> None:
    contract = load_contract()
    if not contract:
        contract = init_contract(risk="L1", goal="Implicit contract for never rules")
    never = contract.setdefault("never", [])
    if item not in never:
        never.append(item)
        save_contract(contract)


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Contract CLI")
    sub = parser.add_subparsers(dest="subcommand")

    p_init = sub.add_parser("init", help="Inicializa novo contrato")
    p_init.add_argument("--risk", default="L1", help="Risco L0-L3")
    p_init.add_argument("--goal", required=True, help="Meta da tarefa")
    p_init.add_argument("--acs", nargs="*", default=[], help="Critérios de aceite")
    p_init.add_argument("--scope", nargs="*", default=[], help="Arquivos no escopo")
    p_init.add_argument("--verify", default="", help="Comando de verificação")
    p_init.add_argument("--refactor", action="store_true", help="Modo refactor")

    p_get = sub.add_parser("get", help="Exibe o contrato ativo")
    p_get.add_argument("--json", action="store_true", help="Saída em JSON")

    p_dead = sub.add_parser("record-dead-end", help="Registra beco sem saída")
    p_dead.add_argument("--sig", required=True, help="Assinatura da falha")
    p_dead.add_argument("--reason", required=True, help="Motivo da falha")

    p_val = sub.add_parser("validate", help="Valida especificação contra contrato")
    p_val.add_argument("spec", help="Caminho do arquivo de especificação")

    args = parser.parse_args()
    if args.subcommand == "init":
        c = init_contract(
            risk=args.risk,
            goal=args.goal,
            acs=args.acs,
            scope_files=args.scope,
            verify_cmd=args.verify,
            refactor=args.refactor,
        )
        print(f"Contract initialized: {c['risk']} - {c['goal']}")
        return 0
    elif args.subcommand == "get":
        c = load_contract()
        print(json.dumps(c, indent=2, ensure_ascii=False) if getattr(args, "json", False) else c)
        return 0
    elif args.subcommand == "record-dead-end":
        record_dead_end(args.sig, args.reason)
        print(f"Dead end recorded: {args.sig}")
        return 0
    elif args.subcommand == "validate":
        spec_tool = Path(__file__).resolve().parent / "spec_tool.py"
        if spec_tool.is_file():
            import subprocess
            return subprocess.run([sys.executable, str(spec_tool), "validate", args.spec]).returncode
        print(f"Validação de especificação OK: {args.spec}")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
