#!/usr/bin/env python3
"""scripts/hooks/pre_tool_guard.py — Hook PreToolUse e validador de políticas (AC-2)
Impede adulteração de políticas e execução de ações do tier human sem aprovação.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TIER_ORDER = {"auto": 0, "review": 1, "human": 2}
RISK_TO_TIER = {"L0": "auto", "L1": "auto", "L2": "review", "L3": "human"}


def get_project_root() -> Path:
    env_dir = os.environ.get("KIT_PROJECT_ROOT")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    try:
        res = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if res.returncode == 0 and isinstance(res.stdout, str) and res.stdout.strip():
            return Path(res.stdout.strip()).resolve()
    except Exception:
        pass
    return Path.cwd().resolve()


def get_runtime_dir() -> Path:
    env_dir = os.environ.get("KIT_RUNTIME_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
    else:
        p = get_project_root() / ".agents" / "runtime"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_approvals_path() -> Path:
    return get_runtime_dir() / "approvals.json"


def get_reviews_path() -> Path:
    return get_runtime_dir() / "reviews.json"


def compute_action_id(tier: str, human_items: List[str]) -> str:
    """Calcula ID determinístico: sha1(tier + caminhos e comandos ordenados)[:8]."""
    sorted_items = sorted(str(item).strip() for item in human_items if str(item).strip())
    raw = f"{tier}:{':'.join(sorted_items)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]


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
    try:
        from scripts.kit_events import emit
        emit("approval", action_id=id_str)
    except Exception:
        pass


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


def record_review(reviewer: str, verdict: str, diff_hash: str) -> Dict[str, Any]:
    """Registra revisão aprovada pelo revisor para o diff atual (convenção de processo)."""
    import time
    path = get_reviews_path()
    data = {"reviews": []}
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"reviews": []}
    entry = {
        "reviewer": reviewer,
        "verdict": verdict,
        "diff_hash": diff_hash,
        "ts": round(time.time(), 3),
    }
    data.setdefault("reviews", []).append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return entry


def load_reviews() -> List[Dict[str, Any]]:
    path = get_reviews_path()
    if not path.is_file():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("reviews", [])
    except Exception:
        return []


def load_policy() -> Dict[str, Any]:
    proj_policy = get_project_root() / ".agents" / "policy.yaml"
    policy_path = proj_policy if proj_policy.is_file() else Path(__file__).resolve().parent.parent.parent / ".agents" / "policy.yaml"
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
) -> Tuple[str, List[str], List[str]]:
    policy = load_policy()
    human_patterns = policy["tiers"].get("human", {}).get("patterns", [])
    human_cmds = policy["tiers"].get("human", {}).get("commands", [])
    review_patterns = policy["tiers"].get("review", {}).get("patterns", [])

    reasons: List[str] = []
    human_matches: List[str] = []
    for cmd in commands:
        for h_cmd in human_cmds:
            h_lower = h_cmd.lower()
            cmd_lower = cmd.lower()
            # Casamento por palavra inteira para comandos de uma única palavra (ex: DROP não casa com dropdown/dropzone)
            if " " in h_lower:
                matched = h_lower in cmd_lower
            else:
                matched = re.search(r"\b" + re.escape(h_lower) + r"\b", cmd_lower) is not None
            if matched:
                reasons.append(f"Command '{cmd}' contains human-tier operation '{h_cmd}'")
                human_matches.append(cmd)

    for f in files:
        for p in human_patterns:
            if fnmatch.fnmatch(f, p) or fnmatch.fnmatch(f, f"*/{p}") or p in f:
                reasons.append(f"File '{f}' matches human-tier pattern '{p}'")
                human_matches.append(f)

    if human_matches:
        return "human", reasons, human_matches

    review_matches: List[str] = []
    for f in files:
        for p in review_patterns:
            if fnmatch.fnmatch(f, p) or fnmatch.fnmatch(f, f"*/{p}") or p in f:
                reasons.append(f"File '{f}' matches review-tier pattern '{p}'")
                review_matches.append(f)

    if review_matches:
        return "review", reasons, review_matches

    return "auto", reasons, []


def calculate_effective_tier(
    declared_risk: str, changed_files: List[str], commands: List[str]
) -> str:
    declared_tier = RISK_TO_TIER.get(declared_risk.upper(), "auto")
    derived_tier, _, _ = evaluate_policy_for_files_and_commands(changed_files, commands)
    return "human" if "human" in (declared_tier, derived_tier) else ("review" if "review" in (declared_tier, derived_tier) else "auto")


_PROTECTED_FILES = ("approvals.json", "policy.yaml")

# Revisores que indicam autoaprovação/forjaria de tier review via shell do agente.
_AUTO_REVIEWERS = ("qa", "builder")


def _basename(path: str) -> str:
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def _shell_writes_protected_file(cmd: str) -> bool:
    """Detecta gravação direta em approvals.json / policy.yaml via shell (echo >, tee, sed -i, cp/mv/install)."""
    norm = cmd.replace("\\", "/")
    names = _PROTECTED_FILES

    # Redirecionamento de saída: cmd > arquivo / cmd >> arquivo / cmd >| arquivo
    for m in re.finditer(r'(?:>>|>|>\|)\s*(["\']?)([^\s"\']+)\1', norm):
        dest = m.group(2)
        if _basename(dest) in names or ".agents/policy.yaml" in dest:
            return True

    # tee <arquivo> (opcional -a)
    for m in re.finditer(r'\btee\b(?:\s+-a)?\s*(["\']?)([^\s"\']+)\1', norm):
        dest = m.group(2)
        if _basename(dest) in names or ".agents/policy.yaml" in dest:
            return True

    # sed -i / --in-place sobre arquivo protegido
    if re.search(r'\bsed\b', norm) and re.search(r'(?:^|[ \t])(-i|--in-place)(?:[ \t]|$)', norm):
        for name in names:
            if re.search(r'\b' + re.escape(name) + r'\b', norm):
                return True
        if ".agents/policy.yaml" in norm:
            return True

    # cp / mv / install que mencionam arquivo protegido
    if re.search(r'\b(cp|mv|install)\b', norm):
        for name in names:
            if re.search(r'\b' + re.escape(name) + r'\b', norm):
                return True
        if ".agents/policy.yaml" in norm:
            return True

    return False


def is_action_permitted(
    tool_name: str, tool_args: Dict[str, Any], action_id: Optional[str] = None
) -> Tuple[bool, str]:
    # 1. Proibição estrita de adulterar policy.yaml e approvals.json (arquivo direto)
    target_path = str(tool_args.get("Path", "") or tool_args.get("path", "") or tool_args.get("TargetFile", ""))
    if target_path:
        norm = target_path.replace("\\", "/")
        if norm.endswith("policy.yaml") or ".agents/policy.yaml" in norm:
            return False, "Agent is forbidden from modifying .agents/policy.yaml (immutable policy)"
        if norm.endswith("approvals.json") or "approvals.json" in norm:
            return False, "Agent is forbidden from modifying approvals.json (tamper protection)"

    # 1b. Bloqueia gravação direta via shell (echo >, tee, sed -i, cp/mv/install)
    cmd = str(tool_args.get("CommandLine", "") or tool_args.get("command", "") or "")
    if cmd and _shell_writes_protected_file(cmd):
        return False, "Agent is forbidden from writing approvals.json or policy.yaml via shell (tamper protection)"

    # 2. Verificação de comandos
    if cmd:
        # xp approve só é válido com stdin interativo (Decisão 14 do SPEC-006)
        if re.search(r"\bxp\s+approve\b", cmd):
            return False, "Agent cannot invoke 'xp approve' (requires interactive human approval)"

        # Remoção de autoaprovação via --reviewer (qa / builder)
        m = re.search(r"\bxp\s+gate\s+review\b", cmd)
        if m:
            m2 = re.search(r"--reviewer\s+(\S+)", cmd)
            if m2 and m2.group(1).lower() in _AUTO_REVIEWERS:
                return False, f"Auto-approval via --reviewer {m2.group(1)} is not allowed (human review required)"

        derived_tier, reasons, matches = evaluate_policy_for_files_and_commands([], [cmd])
        if derived_tier == "human":
            act_id = action_id or compute_action_id("human", matches)
            if not has_approval(act_id):
                return False, f"Action requires explicit human approval via 'xp approve {act_id}': {reasons}"

    return True, "Permitted"


def main() -> int:
    try:
        raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw_input.strip():
            payload = json.loads(raw_input)
            tool_name = payload.get("tool_name") or payload.get("tool") or ""
            tool_args = payload.get("tool_args") or payload.get("parameters") or payload.get("args") or {}
            cmd = str(tool_args.get("CommandLine", "") or tool_args.get("command", "") or "")

            # Decisão 14 do SPEC-006: xp approve exige stdin interativo (isatty verdadeiro).
            if re.search(r"\bxp\s+approve\b", cmd) and not sys.stdin.isatty():
                result = {"decision": "deny", "reason": "'xp approve' requires interactive human stdin (isatty)"}
            else:
                allowed, reason = is_action_permitted(tool_name, tool_args)
                result = {"decision": "allow" if allowed else "deny"}
                if not allowed:
                    result["reason"] = reason
        else:
            result = {"decision": "allow"}
    except Exception:
        # Fail closed: JSON inválido ou exceção no hook BLOQUEIA a ação.
        result = {"decision": "deny", "reason": "hook error"}

    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
