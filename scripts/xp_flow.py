#!/usr/bin/env python3
"""scripts/xp_flow.py — Executor de workflows v2 (AC-7 + padrões ADK em stdlib pura).
Suporta State Whiteboard (output_key + {key}), LoopAgent (on_fail: retry / reopen:<nó> + circuit breaker)
e ParallelAgent (nós parallel:[...] concorrentes via ThreadPoolExecutor).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.evidence_recorder import record
from scripts.hooks.pre_tool_guard import compute_action_id, get_project_root, get_runtime_dir, has_approval
from scripts.xp_contract import init_contract, load_contract, save_contract

STATE_KEYS: Dict[str, Any] = {
    "workflow": None, "current_idx": 0, "completed": [],
    "frozen_tests": {}, "reopened": [], "state": {}, "retries": {},
}
_LAST_EXEC_OUTPUT: Dict[str, str] = {"stdout": "", "stderr": ""}


def get_flow_state_path() -> Path:
    return get_runtime_dir() / "flow_state.json"


def _fresh_state() -> Dict[str, Any]:
    return {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v) for k, v in STATE_KEYS.items()}


def _parse_inline_node(raw: str) -> Optional[Dict[str, Any]]:
    quoted = re.sub(r'(?<=[{,\s])([a-zA-Z_]\w*)\s*:', r'"\1":', raw)
    try:
        return json.loads(quoted)
    except Exception:
        return None


def load_workflow_yaml(custom_path: Optional[str] = None) -> Dict[str, Any]:
    wf_path = Path(custom_path) if custom_path else get_project_root() / ".agents" / "graph" / "workflow.yaml"
    if not wf_path.is_file():
        wf_path = ROOT_DIR / ".agents" / "graph" / "workflow.yaml"
    if not wf_path.is_file():
        return {"workflows": {}, "risk_workflows": {}}
    workflows: Dict[str, Any] = {}
    risk_workflows: Dict[str, str] = {}
    cur_wf: Optional[str] = None
    sec: Optional[str] = None
    for line in wf_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("workflows"):
            sec = "w"
            continue
        if s.startswith("risk_workflows"):
            sec = "r"
            continue
        if sec == "r" and ":" in s:
            k, v = s.split(":", 1)
            risk_workflows[k.strip()] = v.strip().strip('"').strip("'")
        elif sec == "w" and line.startswith("  ") and not line.startswith("    ") and s.endswith(":"):
            cur_wf = s[:-1]
            workflows[cur_wf] = {"nodes": []}
        elif cur_wf and "description:" in s:
            workflows[cur_wf]["description"] = s.split(":", 1)[1].strip().strip('"')
        elif cur_wf and s.startswith("- {") and s.endswith("}"):
            parsed = _parse_inline_node(s[2:].strip())
            if parsed is not None:
                workflows[cur_wf]["nodes"].append(parsed)
    return {"workflows": workflows, "risk_workflows": risk_workflows}


def load_flow_state() -> Dict[str, Any]:
    p = get_flow_state_path()
    try:
        data = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else _fresh_state()
        for k, v in _fresh_state().items():
            data.setdefault(k, v)
        return data
    except Exception:
        return _fresh_state()


def save_flow_state(state: Dict[str, Any]) -> None:
    get_flow_state_path().write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def freeze_test_files() -> Dict[str, str]:
    frozen: Dict[str, str] = {}
    root = get_project_root()
    c = load_contract() or init_contract(risk="L1", goal="Frozen tests baseline")
    for pat in c.get("test_globs") or ["tests/**/test_*.py", "**/*.test.*", "**/*_test.*", "src/test/**"]:
        for f in root.glob(pat):
            if f.is_file():
                try:
                    frozen[str(f.relative_to(root))] = hashlib.sha256(f.read_bytes()).hexdigest()
                except Exception:
                    continue
    c["frozen_tests"] = frozen
    save_contract(c)
    return frozen


def resolve_cmd(cmd_template: str, whiteboard: Optional[Dict[str, Any]] = None) -> str:
    c = load_contract()
    v_cmd = (c.get("verify_cmd") if c else "") or "python3 -m unittest discover tests"
    resolved = cmd_template.replace("{verify_cmd}", v_cmd)
    wb = whiteboard if whiteboard is not None else load_flow_state().get("state", {})
    for k, val in wb.items():
        resolved = resolved.replace(f"{{{k}}}", str(val))
    return resolved.strip()


def run_node_exit_cmd(exit_cmd: str, node_name: str = "", whiteboard: Optional[Dict[str, Any]] = None) -> bool:
    if not exit_cmd:
        _LAST_EXEC_OUTPUT["stdout"] = _LAST_EXEC_OUTPUT["stderr"] = ""
        return True
    resolved = resolve_cmd(exit_cmd, whiteboard=whiteboard)
    res = subprocess.run(resolved, shell=True, cwd=str(get_project_root()), capture_output=True, text=True)
    _LAST_EXEC_OUTPUT["stdout"] = res.stdout.strip()[:500]
    _LAST_EXEC_OUTPUT["stderr"] = res.stderr.strip()[:500]
    c = load_contract()
    risk = c.get("risk", "L1") if c else "L1"
    if "red" in node_name.lower() or resolved.startswith("!"):
        record(resolved, 1 if res.returncode == 0 else 0, output=res.stdout + res.stderr, risk_level=risk)
    elif "green" in node_name.lower():
        record(resolved, res.returncode, output=res.stdout + res.stderr, risk_level=risk)
    return res.returncode == 0


def _run_parallel_branches(branches: List[Dict[str, Any]], whiteboard: Dict[str, Any]) -> Tuple[bool, Dict[str, str], str]:
    outputs: Dict[str, str] = {}
    errors: List[str] = []

    def _exec(br: Dict[str, Any]) -> Tuple[str, Optional[str], bool, str, str]:
        cmd = resolve_cmd(br.get("exit_cmd", ""), whiteboard=whiteboard)
        res = subprocess.run(cmd, shell=True, cwd=str(get_project_root()), capture_output=True, text=True)
        return br.get("name", "branch"), br.get("output_key"), res.returncode == 0, res.stdout.strip()[:500], res.stderr.strip()[:300]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(len(branches), 6))) as pool:
        for fut in concurrent.futures.as_completed([pool.submit(_exec, b) for b in branches]):
            b_name, out_key, ok, out, err = fut.result()
            if out_key and ok:
                outputs[out_key] = out
            if not ok:
                errors.append(f"{b_name}: {err or out or 'exit!=0'}")
    return len(errors) == 0, outputs, "; ".join(errors)


def _execute_node(node: Dict[str, Any], state: Dict[str, Any]) -> bool:
    name = node.get("name", "")
    wb = state.setdefault("state", {})
    parallel = node.get("parallel")
    if isinstance(parallel, list) and parallel:
        ok, branch_outs, err_msg = _run_parallel_branches(parallel, wb)
        wb.update(branch_outs)
        if not ok:
            wb["last_failure"] = err_msg[:300]
        return ok
    _LAST_EXEC_OUTPUT["stdout"] = _LAST_EXEC_OUTPUT["stderr"] = ""
    ok = run_node_exit_cmd(node.get("exit_cmd", ""), name)
    if ok and node.get("output_key"):
        wb[node["output_key"]] = _LAST_EXEC_OUTPUT["stdout"]
    elif not ok:
        wb["last_failure"] = (_LAST_EXEC_OUTPUT["stderr"] or _LAST_EXEC_OUTPUT["stdout"] or f"node '{name}' failed")[:300]
    return ok


def _approval_ok(wf: str, node: Dict[str, Any]) -> bool:
    if not node.get("approval_required"):
        return True
    act_id = compute_action_id("human", [wf, node.get("name", "")])
    if not has_approval(act_id):
        print(f"❌ Nó '{node.get('name')}' requer aprovação humana. Execute: xp approve {act_id}", file=sys.stderr)
        return False
    return True


def _red_before_green(node: Dict[str, Any], completed: List[str]) -> bool:
    if "green" not in node.get("name", "").lower():
        return True
    if not any("red" in n.lower() for n in completed):
        print(f"❌ Nó '{node.get('name')}' bloqueado: RED deve preceder GREEN.", file=sys.stderr)
        return False
    return True


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
        node_names = {n.get("name") for n in nodes}
        known_keys = {"verify_cmd", "last_failure"}
        for n in nodes:
            name, run, sks, cmd, par = n.get("name"), n.get("run"), n.get("skills", []), n.get("exit_cmd"), n.get("parallel")
            if not run or run not in valid_agents:
                errors.append(f"{wf}.{name}: agente '{run}' inválido.")
            if len(sks) > 2 or any(s not in valid_skills for s in sks):
                errors.append(f"{wf}.{name}: skills inválidas ({sks}).")
            if not cmd and not par:
                errors.append(f"{wf}.{name}: exit_cmd vazio.")
            on_fail = str(n.get("on_fail", "abort"))
            if on_fail.startswith("reopen:") and on_fail.split(":", 1)[1].strip() not in node_names:
                errors.append(f"{wf}.{name}: on_fail reopen alvo '{on_fail}' inexistente.")
            for ph in re.findall(r"\{([a-zA-Z0-9_]+)\}", cmd or ""):
                if ph not in known_keys:
                    errors.append(f"{wf}.{name}: placeholder '{{{ph}}}'.")
            if n.get("output_key"):
                known_keys.add(n["output_key"])
            if isinstance(par, list):
                known_keys.update(b["output_key"] for b in par if b.get("output_key"))
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
    state = _fresh_state()
    state["workflow"] = name
    save_flow_state(state)
    print(f"✅ Workflow '{name}' iniciado.")
    return 0


def _nodes(wf: str, custom_path: Optional[str] = None) -> List[Dict[str, Any]]:
    return load_workflow_yaml(custom_path).get("workflows", {}).get(wf, {}).get("nodes", [])


def next_node() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    if not wf:
        print("❌ Nenhum workflow ativo.", file=sys.stderr)
        return 1
    nodes = _nodes(wf)
    idx = state.get("current_idx", 0)
    if idx >= len(nodes):
        print(f"Workflow '{wf}' concluído.")
        return 0
    n = nodes[idx]
    c = load_contract()
    print(
        f"WORKFLOW: {wf} ({idx+1}/{len(nodes)})\nNÓ: {n.get('name')}\nAGENTE: {n.get('run', 'code')}\n"
        f"SKILLS: {', '.join(n.get('skills', [])) or 'nenhuma'}\n"
        f"EXIT_CMD: {resolve_cmd(n.get('exit_cmd', ''), whiteboard=state.get('state', {}))}\n"
        f"OBJETIVO: {c.get('goal', 'Sem objetivo')[:100]}"
    )
    return 0


def emit_node(name: str, phase: str, status: Optional[str] = None) -> None:
    try:
        from scripts.kit_events import emit
        emit("node", node=name, phase=phase, status=status)
    except Exception:
        pass


def _advance_one(state: Dict[str, Any], wf: str, nodes: List[Dict[str, Any]], idx: int) -> int:
    n = nodes[idx]
    if not _approval_ok(wf, n) or not _red_before_green(n, state.get("completed", [])):
        return 1
    emit_node(n.get("name", ""), "enter")
    if not _execute_node(n, state):
        emit_node(n.get("name", ""), "exit", "fail")
        print(f"❌ Nó '{n.get('name')}' falhou: {resolve_cmd(n.get('exit_cmd', ''), whiteboard=state.get('state', {}))}")
        save_flow_state(state)
        return 1
    emit_node(n.get("name", ""), "exit", "pass")
    if n.get("freeze_tests"):
        freeze_test_files()
    state["completed"].append(n.get("name"))
    state["current_idx"] = idx + 1
    save_flow_state(state)
    print(f"✅ Avançado ({state['current_idx']}/{len(nodes)}).")
    return 0


def advance_flow() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    nodes = _nodes(wf) if wf else []
    idx = state.get("current_idx", 0)
    if not wf or idx >= len(nodes):
        print("❌ Nenhum nó a avançar.", file=sys.stderr)
        return 1
    return _advance_one(state, wf, nodes, idx)


def where_flow() -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    nodes = _nodes(wf) if wf else []
    idx = state.get("current_idx", 0)
    name = nodes[idx].get("name") if idx < len(nodes) else "fim"
    print(f"workflow: {wf or 'nenhum'} | step: {idx + 1}/{len(nodes)} | node: {name}")
    return 0


def _handle_node_failure(node: Dict[str, Any], nodes: List[Dict[str, Any]], state: Dict[str, Any]) -> Tuple[str, int]:
    """Aplica política on_fail (retry | reopen:<nó> | abort) com circuit breaker."""
    name = node.get("name", "")
    on_fail = str(node.get("on_fail", "abort"))
    max_retries = int(node.get("max_retries", 2))
    retries = state.setdefault("retries", {})
    count = int(retries.get(name, 0)) + 1
    retries[name] = count

    if on_fail == "retry":
        if count <= max_retries:
            print(f"🔁 Nó '{name}' falhou (tentativa {count}/{max_retries}); tentando novamente...")
            return "continue", 0
        print(f"🚨 Circuit breaker: nó '{name}' excedeu {max_retries} tentativas.", file=sys.stderr)
        return "stop", 3

    if on_fail.startswith("reopen:"):
        target = on_fail.split(":", 1)[1].strip()
        t_idx = next((i for i, n in enumerate(nodes) if n.get("name") == target), None)
        if t_idx is not None and count <= max_retries:
            reason = f"Auto-reopen por falha em '{name}' ({count}/{max_retries})"
            state.setdefault("reopened", []).append({"node": target, "reason": reason})
            state["completed"] = [c for c in state.get("completed", []) if c != target]
            state["current_idx"] = t_idx
            print(f"🔄 {reason}")
            return "continue", 0
        print(f"🚨 Circuit breaker: loop reopen '{target}' excedeu {max_retries} ciclos.", file=sys.stderr)
        return "stop", 3

    print(f"❌ Nó '{name}' falhou: {resolve_cmd(node.get('exit_cmd', ''), whiteboard=state.get('state', {}))}")
    return "stop", 1


def run_flow(workflow_name: str, step_only: bool = False, custom_workflow_path: Optional[str] = None) -> int:
    wfs = load_workflow_yaml(custom_workflow_path).get("workflows", {})
    if workflow_name not in wfs:
        print(f"Erro: Workflow '{workflow_name}' não encontrado.", file=sys.stderr)
        return 1
    nodes = wfs[workflow_name].get("nodes", [])
    state = load_flow_state()
    if state.get("workflow") != workflow_name:
        state = _fresh_state()
        state["workflow"] = workflow_name

    while state["current_idx"] < len(nodes):
        idx = state["current_idx"]
        node = nodes[idx]
        name = node.get("name", "")
        emit_node(name, "enter")
        print(f"▶ [{idx+1}/{len(nodes)}] {name} ({node.get('run', 'agent')})...")

        if not _approval_ok(workflow_name, node) or not _red_before_green(node, state.get("completed", [])):
            emit_node(name, "exit", "fail")
            save_flow_state(state)
            return 1

        if not _execute_node(node, state):
            emit_node(name, "exit", "fail")
            action, rc = _handle_node_failure(node, nodes, state)
            save_flow_state(state)
            if action == "continue":
                continue
            return rc

        emit_node(name, "exit", "pass")
        print(f"✅ Nó '{name}' concluído com sucesso.")
        if node.get("freeze_tests"):
            state["frozen_tests"].update(freeze_test_files())
        if name not in state["completed"]:
            state["completed"].append(name)
        state["current_idx"] = idx + 1
        save_flow_state(state)
        if step_only:
            break

    if state["current_idx"] >= len(nodes):
        print(f"🎉 Workflow '{workflow_name}' concluído com sucesso!")
    return 0


def reopen_node(node_name: str, reason: str) -> int:
    state = load_flow_state()
    wf = state.get("workflow")
    nodes = _nodes(wf) if wf else []
    t_idx = next((i for i, n in enumerate(nodes) if n.get("name") == node_name), None)
    if t_idx is None:
        print(f"Erro: Nó '{node_name}' não encontrado.", file=sys.stderr)
        return 1
    state.setdefault("reopened", []).append({"node": node_name, "reason": reason})
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
    nodes = _nodes(wf)
    idx = state.get("current_idx", 0)
    print(f"Workflow: {wf} (Passo {idx + 1} de {len(nodes)})")
    for i, n in enumerate(nodes):
        m = "✅" if i < idx else ("▶️" if i == idx else "⏳")
        print(f"  {m} {n.get('name')} [{n.get('run', '')}]")
    if state.get("frozen_tests"):
        print(f"Testes Congelados: {len(state['frozen_tests'])} arquivos")
    if state.get("state"):
        print(f"Whiteboard keys: {', '.join(sorted(state['state'].keys()))}")
    return 0


def reset_flow() -> int:
    p = get_flow_state_path()
    if p.is_file():
        p.unlink()
    print("Estado do workflow resetado.")
    return 0


def state_cmd(action: str = "get", key: Optional[str] = None, value: Optional[str] = None) -> int:
    st = load_flow_state()
    if action == "set" and key is not None:
        st.setdefault("state", {})[key] = value or ""
        save_flow_state(st)
        print(f"✅ state[{key}] = {value or ''}")
        return 0
    print(json.dumps(st.get("state", {}), indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="XP Flow Engine v2 (AC-7 + ADK patterns)")
    sub = p.add_subparsers(dest="subcommand")
    sub.add_parser("validate").add_argument("--file")
    sub.add_parser("start").add_argument("workflow")
    for name in ("next", "advance", "where", "status", "reset"):
        sub.add_parser(name)
    rp = sub.add_parser("run")
    rp.add_argument("workflow"); rp.add_argument("--step", action="store_true"); rp.add_argument("--file", default=None)
    ro = sub.add_parser("reopen")
    ro.add_argument("node"); ro.add_argument("--reason", required=True)
    rs = sub.add_parser("state")
    rs.add_argument("action", nargs="?", default="get", choices=["get", "set"])
    rs.add_argument("key", nargs="?", default=None); rs.add_argument("value", nargs="?", default=None)
    args = p.parse_args()
    cmds = {
        "validate": lambda: validate_workflows(args.file), "start": lambda: start_flow(args.workflow),
        "next": next_node, "advance": advance_flow, "where": where_flow,
        "run": lambda: run_flow(args.workflow, step_only=args.step, custom_workflow_path=args.file),
        "status": status_flow, "reset": reset_flow,
        "reopen": lambda: reopen_node(args.node, args.reason),
        "state": lambda: state_cmd(args.action, args.key, args.value),
    }
    return cmds[args.subcommand]() if args.subcommand in cmds else (p.print_help() or 1)


if __name__ == "__main__":
    sys.exit(main())
