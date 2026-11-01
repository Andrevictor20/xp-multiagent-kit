#!/usr/bin/env python3
"""scripts/xp_flow.py — Executor determinístico do grafo mínimo de workflows (AC-7)
Lê .agents/workflow.yaml, gerencia nós, exit_cmd e congelamento de testes RED.
Limite estrito: <= 250 linhas.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.xp_contract import get_runtime_dir, load_contract, save_contract


def get_flow_state_path() -> Path:
    return get_runtime_dir() / "flow_state.json"


def load_workflow_yaml() -> Dict[str, Any]:
    wf_path = ROOT_DIR / ".agents" / "workflow.yaml"
    if not wf_path.is_file():
        return {"workflows": {}}
    # Parser YAML nativo e minimalista para evitar dependência externa pyyaml
    content = wf_path.read_text(encoding="utf-8")
    workflows: Dict[str, Any] = {}
    current_wf = None
    for line in content.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue
        if line.startswith("  ") and not line.startswith("    ") and line_str.endswith(":"):
            current_wf = line_str[:-1]
            workflows[current_wf] = {"nodes": []}
        elif current_wf and "description:" in line_str:
            workflows[current_wf]["description"] = line_str.split(":", 1)[1].strip().strip('"')
        elif current_wf and line_str.startswith("- {") and line_str.endswith("}"):
            raw_dict = line_str[2:].strip()
            try:
                import re
                quoted = re.sub(r'(\b[a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', raw_dict)
                node_dict = json.loads(quoted)
                workflows[current_wf]["nodes"].append(node_dict)
            except Exception:
                pass
    return {"workflows": workflows}


def load_flow_state() -> Dict[str, Any]:
    p = get_flow_state_path()
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"workflow": None, "current_idx": 0, "completed": [], "frozen_tests": {}, "reopened": []}


def save_flow_state(state: Dict[str, Any]) -> None:
    p = get_flow_state_path()
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def freeze_test_files() -> Dict[str, str]:
    frozen: Dict[str, str] = {}
    tests_dir = ROOT_DIR / "tests"
    if tests_dir.is_dir():
        for test_file in tests_dir.rglob("test_*.py"):
            try:
                sha = hashlib.sha256(test_file.read_bytes()).hexdigest()
                frozen[str(test_file.relative_to(ROOT_DIR))] = sha
            except Exception:
                pass
    contract = load_contract()
    contract["frozen_tests"] = frozen
    save_contract(contract)
    return frozen


def run_node_exit_cmd(exit_cmd: str) -> bool:
    if not exit_cmd:
        return True
    res = subprocess.run(exit_cmd, shell=True, cwd=str(ROOT_DIR), capture_output=True, text=True)
    return res.returncode == 0


def run_flow(workflow_name: str, step_only: bool = False) -> int:
    wfs = load_workflow_yaml().get("workflows", {})
    if workflow_name not in wfs:
        print(f"Erro: Workflow '{workflow_name}' não encontrado em .agents/workflow.yaml")
        return 1

    wf_def = wfs[workflow_name]
    nodes = wf_def.get("nodes", [])
    state = load_flow_state()

    if state.get("workflow") != workflow_name:
        state = {
            "workflow": workflow_name,
            "current_idx": 0,
            "completed": [],
            "frozen_tests": {},
            "reopened": [],
        }

    while state["current_idx"] < len(nodes):
        node = nodes[state["current_idx"]]
        name = node.get("name")
        exit_cmd = node.get("exit_cmd", "")
        print(f"▶ [Nó {state['current_idx']+1}/{len(nodes)}] {name} ({node.get('run', 'agent')})...")

        ok = run_node_exit_cmd(exit_cmd)
        if not ok:
            print(f"❌ Nó '{name}' falhou na verificação: {exit_cmd}")
            save_flow_state(state)
            return 1

        print(f"✅ Nó '{name}' concluído com sucesso.")
        if node.get("freeze_tests"):
            frozen = freeze_test_files()
            state["frozen_tests"].update(frozen)
            print(f"❄️  Testes RED congelados ({len(frozen)} arquivos rastreados via SHA-256).")

        if name not in state["completed"]:
            state["completed"].append(name)
        state["current_idx"] += 1
        save_flow_state(state)

        if step_only:
            break

    if state["current_idx"] >= len(nodes):
        print(f"🎉 Workflow '{workflow_name}' concluído com sucesso!")
    return 0


def reopen_node(node_name: str, reason: str) -> int:
    state = load_flow_state()
    wf_name = state.get("workflow")
    if not wf_name:
        print("Erro: Nenhum workflow ativo encontrado no estado.")
        return 1

    wfs = load_workflow_yaml().get("workflows", {})
    nodes = wfs.get(wf_name, {}).get("nodes", [])
    target_idx = None
    for idx, n in enumerate(nodes):
        if n.get("name") == node_name:
            target_idx = idx
            break

    if target_idx is None:
        print(f"Erro: Nó '{node_name}' não encontrado no workflow '{wf_name}'.")
        return 1

    entry = {
        "node": node_name,
        "reason": reason,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    state.setdefault("reopened", []).append(entry)
    state["current_idx"] = target_idx
    if node_name in state.get("completed", []):
        state["completed"] = [n for n in state["completed"] if n != node_name]
    save_flow_state(state)
    print(f"🔓 Nó '{node_name}' reaberto explicitamente. Motivo: {reason}")
    return 0


def status_flow() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    if not wf:
        print("Nenhum workflow ativo no momento.")
        return 0
    wfs = load_workflow_yaml().get("workflows", {})
    nodes = wfs.get(wf, {}).get("nodes", [])
    curr_idx = state.get("current_idx", 0)
    print(f"Workflow: {wf} (Passo {curr_idx + 1} de {len(nodes)})")
    for idx, n in enumerate(nodes):
        status_marker = "✅" if idx < curr_idx else ("▶️" if idx == curr_idx else "⏳")
        print(f"  {status_marker} {n.get('name')} [{n.get('run', '')}]")
    if state.get("frozen_tests"):
        print(f"Testes Congelados: {len(state['frozen_tests'])} arquivos")
    if state.get("reopened"):
        print(f"Reaberturas: {len(state['reopened'])}")
    return 0


def reset_flow() -> int:
    p = get_flow_state_path()
    if p.is_file():
        p.unlink()
    print("Estado do workflow resetado.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="XP Flow Engine (AC-7)")
    sub = parser.add_subparsers(dest="subcommand")

    p_run = sub.add_parser("run", help="Executa um workflow")
    p_run.add_argument("workflow", help="Nome do workflow (feature, fix, refactor, chore, hotfix, release, migration, incident)")
    p_run.add_argument("--step", action="store_true", help="Executa apenas o próximo nó")

    p_status = sub.add_parser("status", help="Exibe status do workflow atual")
    p_reset = sub.add_parser("reset", help="Reseta o estado do workflow atual")

    p_reopen = sub.add_parser("reopen", help="Reabre um nó já executado")
    p_reopen.add_argument("node", help="Nome do nó a ser reaberto")
    p_reopen.add_argument("--reason", required=True, help="Motivo formal da reabertura")

    args = parser.parse_args()
    if args.subcommand == "run":
        return run_flow(args.workflow, step_only=args.step)
    elif args.subcommand == "status":
        return status_flow()
    elif args.subcommand == "reset":
        return reset_flow()
    elif args.subcommand == "reopen":
        return reopen_node(args.node, args.reason)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
