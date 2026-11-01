#!/usr/bin/env python3
"""scripts/hooks/pre_tool_guard.py — Hook PreToolUse e validador de políticas (AC-2)
Impede adulteração de políticas e execução de ações do tier human sem aprovação.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TIER_ORDER = {"auto": 0, "review": 1, "human": 2}
RISK_TO_TIER = {"L0": "auto", "L1": "auto", "L2": "review", "L3": "human"}


def get_runtime_dir() -> Path:
    env_dir = os.environ.get("KIT_RUNTIME_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
    else:
        p = Path(__file__).resolve().parent.parent.parent / ".agents" / "runtime"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_approvals_path() -> Path:
    return get_runtime_dir() / "approvals.json"


def record_approval(id_str: str) -> None:
    path = get_approvals_path()
    data = {"approved_ids": []}
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"approved_ids": []}
    if id_str not in data["approved_ids"]:
        data["approved_ids"].append(id_str)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def has_approval(id_str: str) -> bool:
    path = get_approvals_path()
    if not path.is_file():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return id_str in data.get("approved_ids", [])
    except Exception:
        return False


def load_policy() -> Dict[str, Any]:
    policy_path = Path(__file__).resolve().parent.parent.parent / ".agents" / "policy.yaml"
    if not policy_path.is_file():
        return {
            "tiers": {
                "auto": {"patterns": ["*.md", "tests/**", "test_*.py", "docs/**"]},
                "review": {"patterns": ["**/auth/**", "**/billing/**", "**/schema/**", ".github/**"]},
                "human": {
                    "patterns": ["**/migrations/**", "*.tf", ".env*"],
                    "commands": ["rm -rf", "DROP", "terraform apply", "git push --force"],
                },
            }
        }
    # Parse YAML simples sem dependência externa
    tiers: Dict[str, Any] = {"auto": {"patterns": []}, "review": {"patterns": []}, "human": {"patterns": [], "commands": []}}
    cur_tier = None
    cur_key = None
    for line in policy_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and line[:-1] in ["auto", "review", "human"]:
            cur_tier = line[:-1]
            continue
        if cur_tier and line.endswith(":") and line[:-1] in ["patterns", "commands"]:
            cur_key = line[:-1]
            continue
        if cur_tier and cur_key and line.startswith("- "):
            val = line[2:].strip().strip('"').strip("'")
            tiers[cur_tier].setdefault(cur_key, []).append(val)
    return {"tiers": tiers}


def evaluate_policy_for_files_and_commands(
    files: List[str], commands: List[str]
) -> Tuple[str, List[str]]:
    policy = load_policy()
    human_patterns = policy["tiers"].get("human", {}).get("patterns", [])
    human_cmds = policy["tiers"].get("human", {}).get("commands", [])
    review_patterns = policy["tiers"].get("review", {}).get("patterns", [])

    reasons: List[str] = []
    # Check commands for human tier
    for cmd in commands:
        for h_cmd in human_cmds:
            if h_cmd.lower() in cmd.lower():
                reasons.append(f"Command '{cmd}' contains human-tier operation '{h_cmd}'")
                return "human", reasons

    # Check files for human tier
    for f in files:
        for p in human_patterns:
            if fnmatch.fnmatch(f, p) or fnmatch.fnmatch(f, f"*/{p}") or p in f:
                reasons.append(f"File '{f}' matches human-tier pattern '{p}'")
                return "human", reasons

    # Check files for review tier
    for f in files:
        for p in review_patterns:
            if fnmatch.fnmatch(f, p) or fnmatch.fnmatch(f, f"*/{p}") or p in f:
                reasons.append(f"File '{f}' matches review-tier pattern '{p}'")
                return "review", reasons

    return "auto", reasons


def calculate_effective_tier(
    declared_risk: str, changed_files: List[str], commands: List[str]
) -> str:
    declared_tier = RISK_TO_TIER.get(declared_risk.upper(), "auto")
    derived_tier, _ = evaluate_policy_for_files_and_commands(changed_files, commands)
    return "human" if "human" in (declared_tier, derived_tier) else ("review" if "review" in (declared_tier, derived_tier) else "auto")


def is_action_permitted(
    tool_name: str, tool_args: Dict[str, Any], action_id: Optional[str] = None
) -> Tuple[bool, str]:
    # 1. Proibição de adulterar policy.yaml e approvals.json
    target_path = str(tool_args.get("Path", "") or tool_args.get("path", ""))
    if target_path:
        norm = target_path.replace("\\", "/")
        if norm.endswith("policy.yaml") or ".agents/policy.yaml" in norm:
            return False, "Agent is forbidden from modifying .agents/policy.yaml (immutable policy)"
        if norm.endswith("approvals.json") or "runtime/approvals.json" in norm:
            return False, "Agent is forbidden from modifying approvals.json (tamper protection)"

    # 2. Verificação de comandos
    cmd = str(tool_args.get("CommandLine", "") or tool_args.get("command", ""))
    if cmd:
        if re.search(r"\bxp\s+approve\b", cmd):
            return False, "Agent cannot invoke 'xp approve' (requires interactive human approval)"
        derived_tier, reasons = evaluate_policy_for_files_and_commands([], [cmd])
        if derived_tier == "human":
            act_id = action_id or cmd.split()[0]
            if not has_approval(act_id):
                return False, f"Action requires explicit human approval via 'xp approve {act_id}': {reasons}"

    return True, "Permitted"
