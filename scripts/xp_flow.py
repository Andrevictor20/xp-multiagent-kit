#!/usr/bin/env python3
"""scripts/xp_flow.py — Executor determinístico do grafo mínimo de workflows (AC-7)
Lê .agents/workflow.yaml, gerencia nós, exit_cmd e congelamento de testes RED.
Limite estrito: <= 320 linhas.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.evidence_recorder import record
from scripts.hooks.pre_tool_guard import get_project_root, get_runtime_dir
from scripts.xp_contract import init_contract, load_contract, save_contract


def get_flow_state_path() -> Path:
    return get_runtime_dir() / "flow_state.json"


def load_workflow_yaml(custom_path: Optional[str] = None) -> Dict[str, Any]:
    wf_path = Path(custom_path) if custom_path else get_project_root() / ".agents" / "workflow.yaml"
    if not wf_path.is_file():
        wf_path = ROOT_DIR / ".agents" / "workflow.yaml"
    if not wf_path.is_file():
        return {"workflows": {}, "risk_workflows": {}}
    workflows: Dict[str, Any] = {}
    risk_workflows: Dict[str, str] = {}
    cur_wf, sec = None, None
    for line in wf_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("workflows"):
            sec = "w"
        elif s.startswith("risk_workflows"):
            sec = "r"
        elif sec == "r" and ":" in s:
            k, v = s.split(":", 1)
            risk_workflows[k.strip()] = v.strip().strip('"').strip("'")
        elif sec == "w" and line.startswith("  ") and not line.startswith("    ") and s.endswith(":"):
            cur_wf = s[:-1]
            workflows[cur_wf] = {"nodes": []}
        elif cur_wf and "description:" in s:
            workflows[cur_wf]["description"] = s.split(":", 1)[1].strip().strip('"')
        elif cur_wf and s.startswith("- {") and s.endswith("}"):
            try:
                workflows[cur_wf]["nodes"].append(json.loads(re.sub(r'(\b[a-zA-Z_]\w*)\s*:', r'"\1":', s[2:].strip())))
            except Exception:
                continue
    return {"workflows": workflows, "risk_workflows": risk_workflows}


def load_flow_state() -> Dict[str, Any]:
    p = get_flow_state_path()
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"workflow": None, "current_idx": 0, "completed": [], "frozen_tests": {}, "reopened": []}
    return {"workflow": None, "current_idx": 0, "completed": [], "frozen_tests": {}, "reopened": []}


def save_flow_state(state: Dict[str, Any]) -> None:
    get_flow_state_path().write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def freeze_test_files() -> Dict[str, str]:
    frozen: Dict[str, str] = {}
    root = get_project_root()
    c = load_contract() or init_contract(risk="L1", goal="Frozen tests baseline")
    globs = c.get("test_globs") or ["tests/**/test_*.py", "**/*.test.*", "**/*_test.*", "src/test/**"]
    for pat in globs:
        for f in root.glob(pat):
            if f.is_file():
                try:
                    frozen[str(f.relative_to(root))] = hashlib.sha256(f.read_bytes()).hexdigest()
                except Exception:
                    continue
    c["frozen_tests"] = frozen
    save_contract(c)
    return frozen


def resolve_cmd(cmd_template: str) -> str:
    c = load_contract()
    v_cmd = (c.get("verify_cmd") if c else "") or "python3 -m unittest discover tests"
    return cmd_template.replace("{verify_cmd}", v_cmd).strip()


def run_node_exit_cmd(exit_cmd: str, node_name: str = "") -> bool:
    if not exit_cmd:
        return True
    resolved = resolve_cmd(exit_cmd)
    res = subprocess.run(resolved, shell=True, cwd=str(get_project_root()), capture_output=True, text=True)
    c = load_contract()
    risk = c.get("risk", "L1") if c else "L1"
    if "red" in node_name.lower() or resolved.startswith("!"):
        record(resolved, 1 if res.returncode == 0 else 0, output=res.stdout + res.stderr, risk_level=risk)
    elif "green" in node_name.lower():
        record(resolved, res.returncode, output=res.stdout + res.stderr, risk_level=risk)
    return res.returncode == 0


def validate_workflows(custom_path: Optional[str] = None) -> int:
    wfs = load_workflow_yaml(custom_path).get("workflows", {})
    if not wfs:
        print("❌ Nenhum workflow encontrado.", file=sys.stderr)
        return 1
    valid_agents = {"orchestrator", "builder", "reviewer", "sentinel", "designer", "shipper", "code"}
    s_dir = ROOT_DIR / ".agents" / "skills"
    valid_skills = {d.name for d in s_dir.iterdir() if d.is_dir()} if s_dir.is_dir() else set()
    errors: List[str] = []
    for wf, defn in wfs.items():
        nodes = defn.get("nodes", [])
        if not nodes:
            errors.append(f"Workflow '{wf}' sem nós.")
            continue
        for n in nodes:
            name, run, sks, cmd = n.get("name"), n.get("run"), n.get("skills", []), n.get("exit_cmd")
            if not run or run not in valid_agents:
                errors.append(f"{wf}.{name}: agente '{run}' inválido.")
            if len(sks) > 2 or any(s not in valid_skills for s in sks):
                errors.append(f"{wf}.{name}: skills inválidas ou > 2 ({sks}).")
            if not cmd:
                errors.append(f"{wf}.{name}: exit_cmd vazio.")
            for ph in re.findall(r"\{([a-zA-Z0-9_]+)\}", cmd or ""):
                if ph != "verify_cmd":
                    errors.append(f"{wf}.{name}: placeholder desconhecido '{{{ph}}}'.")
        if nodes[-1].get("name") != "gate":
            errors.append(f"{wf}: último nó deve ser 'gate'.")
    if errors:
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        return 1
    print(f"✅ Validação OK: {len(wfs)} fluxos íntegros.")
    return 0


def start_flow(name: str) -> int:
    if name not in load_workflow_yaml().get("workflows", {}):
        print(f"❌ Workflow '{name}' não existe.", file=sys.stderr)
        return 1
    save_flow_state({"workflow": name, "current_idx": 0, "completed": [], "frozen_tests": {}, "reopened": []})
    print(f"✅ Workflow '{name}' iniciado.")
    return 0


def next_node() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    if not wf:
        print("❌ Nenhum workflow ativo.", file=sys.stderr)
        return 1
    nodes = load_workflow_yaml().get("workflows", {}).get(wf, {}).get("nodes", [])
    idx = state.get("current_idx", 0)
    if idx >= len(nodes):
        print(f"Workflow '{wf}' concluído.")
        return 0
    n = nodes[idx]
    c = load_contract()
    msg = (
        f"WORKFLOW: {wf} ({idx+1}/{len(nodes)})\n"
        f"NÓ: {n.get('name')} [{n.get('kind', 'model')}]\n"
        f"AGENTE: {n.get('run', 'code')}\n"
        f"SKILLS: {', '.join(n.get('skills', [])) or 'nenhuma'}\n"
        f"EXIT_CMD: {resolve_cmd(n.get('exit_cmd', ''))}\n"
        f"OBJETIVO: {c.get('goal', 'Sem objetivo')[:100]}"
    )
    b = msg.encode("utf-8")
    print(b[:797].decode("utf-8", errors="ignore") + "..." if len(b) > 800 else msg)
    return 0


def advance_flow() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    nodes = load_workflow_yaml().get("workflows", {}).get(wf, {}).get("nodes", []) if wf else []
    idx = state.get("current_idx", 0)
    if not wf or idx >= len(nodes):
        print("❌ Nenhum nó a avançar.", file=sys.stderr)
        return 1
    n = nodes[idx]
    if not run_node_exit_cmd(n.get("exit_cmd", ""), n.get("name", "")):
        print(f"❌ Nó '{n.get('name')}' falhou: {resolve_cmd(n.get('exit_cmd', ''))}")
        return 1
    if n.get("freeze_tests"):
        freeze_test_files()
    state["completed"].append(n.get("name"))
    state["current_idx"] += 1
    save_flow_state(state)
    print(f"✅ Avançado ({state['current_idx']}/{len(nodes)}).")
    return 0


def where_flow() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    nodes = load_workflow_yaml().get("workflows", {}).get(wf, {}).get("nodes", []) if wf else []
    idx = state.get("current_idx", 0)
    name = nodes[idx].get("name") if idx < len(nodes) else "fim"
    print(f"workflow: {wf or 'nenhum'} | step: {idx + 1}/{len(nodes)} | node: {name}")
    return 0


def run_flow(workflow_name: str, step_only: bool = False) -> int:
    wfs = load_workflow_yaml().get("workflows", {})
    if workflow_name not in wfs:
        print(f"Erro: Workflow '{workflow_name}' não encontrado.", file=sys.stderr)
        return 1
    nodes = wfs[workflow_name].get("nodes", [])
    state = load_flow_state()
    if state.get("workflow") != workflow_name:
        state = {"workflow": workflow_name, "current_idx": 0, "completed": [], "frozen_tests": {}, "reopened": []}

    while state["current_idx"] < len(nodes):
        node = nodes[state["current_idx"]]
        name = node.get("name")
        print(f"▶ [{state['current_idx']+1}/{len(nodes)}] {name} ({node.get('run', 'agent')})...")
        if not run_node_exit_cmd(node.get("exit_cmd", ""), name):
            print(f"❌ Nó '{name}' falhou: {resolve_cmd(node.get('exit_cmd', ''))}")
            save_flow_state(state)
            return 1
        print(f"✅ Nó '{name}' concluído com sucesso.")
        if node.get("freeze_tests"):
            state["frozen_tests"].update(freeze_test_files())
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
    wf = state.get("workflow")
    nodes = load_workflow_yaml().get("workflows", {}).get(wf, {}).get("nodes", []) if wf else []
    t_idx = next((i for i, n in enumerate(nodes) if n.get("name") == node_name), None)
    if t_idx is None:
        print(f"Erro: Nó '{node_name}' não encontrado.", file=sys.stderr)
        return 1
    state.setdefault("reopened", []).append({"node": node_name, "reason": reason, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    state["current_idx"] = t_idx
    state["completed"] = [n for n in state.get("completed", []) if n != node_name]
    save_flow_state(state)
    print(f"🔓 Nó '{node_name}' reaberto explicitamente. Motivo: {reason}")
    return 0


def status_flow() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    if not wf:
        print("Nenhum workflow ativo no momento.")
        return 0
    nodes = load_workflow_yaml().get("workflows", {}).get(wf, {}).get("nodes", [])
    idx = state.get("current_idx", 0)
    print(f"Workflow: {wf} (Passo {idx + 1} de {len(nodes)})")
    for i, n in enumerate(nodes):
        m = "✅" if i < idx else ("▶️" if i == idx else "⏳")
        print(f"  {m} {n.get('name')} [{n.get('run', '')}]")
    if state.get("frozen_tests"):
        print(f"Testes Congelados: {len(state['frozen_tests'])} arquivos")
    return 0


def reset_flow() -> int:
    p = get_flow_state_path()
    if p.is_file():
        p.unlink()
    print("Estado do workflow resetado.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="XP Flow Engine (AC-7)")
    sub = p.add_subparsers(dest="subcommand")
    sub.add_parser("validate").add_argument("--file")
    sub.add_parser("start").add_argument("workflow")
    for name in ("next", "advance", "where", "status", "reset"):
        sub.add_parser(name)
    r_p = sub.add_parser("run")
    r_p.add_argument("workflow"); r_p.add_argument("--step", action="store_true")
    ro_p = sub.add_parser("reopen")
    ro_p.add_argument("node"); ro_p.add_argument("--reason", required=True)

    args = p.parse_args()
    cmds = {
        "validate": lambda: validate_workflows(args.file), "start": lambda: start_flow(args.workflow),
        "next": next_node, "advance": advance_flow, "where": where_flow,
        "run": lambda: run_flow(args.workflow, step_only=args.step), "status": status_flow,
        "reset": reset_flow, "reopen": lambda: reopen_node(args.node, args.reason),
    }
    if args.subcommand in cmds:
        return cmds[args.subcommand]()
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
