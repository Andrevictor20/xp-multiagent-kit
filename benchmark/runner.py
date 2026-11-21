"""Benchmark runner: executes paired scenarios with and without the XP kit."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple

import oracles
import scenarios as scen

KIT_ROOT = Path(__file__).resolve().parent.parent
SUBSTRATE = Path(__file__).resolve().parent / "substrate"
PY = "python3"

KIT_PAYLOAD = [
    "AGENTS.md",
    "scripts",
    ".agents/policy.yaml",
    ".agents/graph",
    ".agents/policies",
    ".agents/memory",
]


def _ensure_policy_index(dest: Path) -> None:
    """Gera o índice JIT de políticas dentro do sandbox (equivalente ao estado entregue)."""
    idx = dest / ".agents" / "policies" / "INDEX.md"
    if not idx.is_file():
        from scripts.policy_index import write_policy_index
        policies_dir = dest / ".agents" / "policies"
        if policies_dir.is_dir():
            write_policy_index(policies_dir, idx)


# O kit carrega em todo turno apenas AGENTS.md + memória + índice de políticas (JIT).
# As 7 políticas inteiras só entram por gatilho, via `xp context <query>`.
FIXED_CONTEXT_FILES = [
    "AGENTS.md",
    ".agents/memory/PROJECT_MEMORY.md",
    ".agents/policies/INDEX.md",
]


def fixed_context_bytes(repo: Path) -> int:
    total = 0
    for rel in FIXED_CONTEXT_FILES:
        path = repo / rel
        if path.is_file():
            total += path.stat().st_size
    return total


def _ignore(_dir: str, names: List[str]) -> List[str]:
    return [n for n in names if n in ("__pycache__", ".git", "global-token-optimizer")]


def build_sandbox(dest: Path, with_kit: bool) -> Path:
    """Create an isolated git repository at `dest` from the substrate."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SUBSTRATE, dest, ignore=_ignore)
    if with_kit:
        for rel in KIT_PAYLOAD:
            src = KIT_ROOT / rel
            dst = dest / rel
            if src.is_dir():
                shutil.copytree(src, dst, ignore=_ignore)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        _ensure_policy_index(dest)
    _git(dest, "init", "-q")
    _git(dest, "config", "user.email", "bench@example.com")
    _git(dest, "config", "user.name", "bench")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-qm", "base")
    return dest


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def run_cmd(repo: Path, argv: List[str]) -> Tuple[int, str, float]:
    started = time.perf_counter()
    res = subprocess.run(argv, cwd=str(repo), capture_output=True, text=True)
    elapsed = time.perf_counter() - started
    return res.returncode, (res.stdout or "") + (res.stderr or ""), elapsed


def snapshot_tests(repo: Path) -> Dict[str, str]:
    return {
        str(p.relative_to(repo)): p.read_text(encoding="utf-8")
        for p in sorted((repo / "tests").rglob("*.py"))
    }


def apply_files(repo: Path, mapping: scen.FileMap) -> None:
    for rel, content in mapping.items():
        target = repo / rel
        if content is None:
            if target.is_file():
                target.unlink()
            continue
        if callable(content):
            content(repo)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _changed_bytes(repo: Path) -> int:
    total = 0
    for rel in oracles.changed_paths(repo):
        path = repo / rel
        if path.is_file():
            total += path.stat().st_size
    return total


def _runtime_bytes(repo: Path) -> int:
    runtime = repo / ".agents" / "runtime"
    if not runtime.is_dir():
        return 0
    return sum(p.stat().st_size for p in runtime.rglob("*") if p.is_file())


def arm_baseline(repo: Path, sc: scen.Scenario) -> Dict[str, object]:
    """Arm A: a plain repo. The developer writes the change and runs the suite."""
    started = time.perf_counter()
    apply_files(repo, sc.red)
    apply_files(repo, sc.green)
    files_bytes = _changed_bytes(repo)
    code_c, out_c, _ = run_cmd(repo, [PY, "-m", "compileall", "-q", "app", "tests"])
    code_t, out_t, _ = run_cmd(repo, [PY, "-m", "unittest", "discover", "-s", "tests", "-q"])
    verdict = "pass" if code_c == 0 and code_t == 0 else "blocked"
    return {
        "arm": "baseline",
        "verdict": verdict,
        "exit_code": code_t if code_t != 0 else code_c,
        "blocked_step": None,
        "duration_s": round(time.perf_counter() - started, 3),
        "files_bytes": files_bytes,
        "process_output_bytes": len(out_c) + len(out_t),
        "governance_bytes": 0,
        "ceremony_bytes": 0,
        "human_steps": 0,
        "commands": 2,
        "detail": (out_t.strip().splitlines() or [""])[-1][:200],
    }


def _contract_init(repo: Path, sc: scen.Scenario) -> Tuple[int, str]:
    argv = [PY, "scripts/xp_contract.py", "init", "--risk", sc.risk, "--goal", sc.goal,
            "--verify", scen.UNITTEST]
    if sc.acs:
        argv += ["--acs", *sc.acs]
    if sc.scope:
        argv += ["--scope", *sc.scope]
    if sc.refactor:
        argv.append("--refactor")
    code, out, _ = run_cmd(repo, argv)
    return code, out


def _freeze(repo: Path) -> Tuple[int, str]:
    code, out, _ = run_cmd(
        repo,
        [PY, "-c", "from scripts.xp_flow import freeze_test_files; "
                   "print(len(freeze_test_files()))"],
    )
    return code, out


def arm_kit(repo: Path, sc: scen.Scenario) -> Dict[str, object]:
    """Arm B: the same repo with the XP kit installed and its ceremony followed."""
    started = time.perf_counter()
    commands = 0
    human_steps = 0
    outputs: List[str] = []

    code, out = _contract_init(repo, sc)
    commands += 1
    outputs.append(out)
    code, out = _freeze(repo) if sc.freeze_tests else (0, "")
    commands += 1 if sc.freeze_tests else 0
    outputs.append(out)

    if sc.needs_red:
        apply_files(repo, sc.red)
        _, out, _ = run_cmd(repo, [PY, "scripts/xp_gate.py", "record", "--", *scen.UNITTEST.split()])
        commands += 1
        outputs.append(out)

    apply_files(repo, sc.green)
    files_bytes = _changed_bytes(repo)
    _, out, _ = run_cmd(repo, [PY, "scripts/xp_gate.py", "record", "--", *scen.UNITTEST.split()])
    commands += 1
    outputs.append(out)

    code, out, duration = run_cmd(repo, [PY, "scripts/xp_gate.py", "check"])
    commands += 1
    outputs.append(out)
    total_duration = duration
    blocked_step = _blocked_step(out)

    if code == 2 and "tier=human" in out and sc.requires_approval:
        match = re.search(r"action=([0-9a-f]{8})", out)
        if match:
            _, out2, _ = run_cmd(repo, [PY, "scripts/xp", "approve", match.group(1)])
            commands += 1
            human_steps += 1
            outputs.append(out2)
            code, out, duration = run_cmd(repo, [PY, "scripts/xp_gate.py", "check"])
            commands += 1
            total_duration += duration
            outputs.append(out)
            blocked_step = _blocked_step(out)

    if code == 2 and "tier=review" in out and sc.requires_review:
        _, out2, _ = run_cmd(repo, [PY, "scripts/xp_gate.py", "review",
                                    "--reviewer", "staff-engineer", "--verdict", "approve"])
        commands += 1
        human_steps += 1
        outputs.append(out2)
        code, out, duration = run_cmd(repo, [PY, "scripts/xp_gate.py", "check"])
        commands += 1
        total_duration += duration
        outputs.append(out)
        blocked_step = _blocked_step(out)

    elapsed = time.perf_counter() - started
    return {
        "arm": "kit",
        "verdict": "pass" if code == 0 else "blocked",
        "exit_code": code,
        "blocked_step": blocked_step,
        "duration_s": round(elapsed, 3),
        "gate_duration_s": round(total_duration, 3),
        "files_bytes": files_bytes,
        "process_output_bytes": sum(len(o) for o in outputs),
        "governance_bytes": governance_bytes(repo),
        "ceremony_bytes": _runtime_bytes(repo),
        "human_steps": human_steps,
        "commands": commands,
        "detail": (out.strip().splitlines() or [""])[-1][:200],
    }


def _blocked_step(output: str) -> object:
    if "GATE FAIL" not in output and "GATE BLOCK" not in output:
        return None
    match = re.search(r"step=(\d+)", output)
    if match:
        return int(match.group(1))
    if "tier=human" in output or "tier=review" in output:
        return 10
    return None


def governance_bytes(repo: Path) -> int:
    """Bytes do contexto fixo de governança pago em cada turno.

    Com o índice JIT, as 7 políticas inteiras (9.2 KB) não são mais
    injetadas: entram apenas `AGENTS.md` + `PROJECT_MEMORY.md` +
    `.agents/policies/INDEX.md` (≈ 586 B). O restante é carregado
    por gatilho via `xp context <query>` quando relevante.
    """
    return fixed_context_bytes(repo)


def run_scenario(sc: scen.Scenario, workdir: Path) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for arm in ("baseline", "kit"):
        repo = build_sandbox(workdir / f"{sc.sid}__{arm}", with_kit=(arm == "kit"))
        base = snapshot_tests(repo)
        result = arm_baseline(repo, sc) if arm == "baseline" else arm_kit(repo, sc)
        defective, labels = oracles.evaluate(repo, sc, base)
        result.update({
            "scenario": sc.sid,
            "kind": sc.kind,
            "risk": sc.risk,
            "oracle": sc.oracle,
            "oracle_defective": defective,
            "oracle_labels": labels,
            "true_positive": bool(defective and result["verdict"] == "blocked"),
            "false_positive": bool((not defective) and result["verdict"] == "blocked"),
            "hypothesis": sc.hypothesis,
        })
        records.append(result)
    return records


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="XP kit paired benchmark")
    parser.add_argument("--only", nargs="*", default=None, help="Scenario ids to run")
    parser.add_argument("--workdir", default=str(Path("/tmp/opencode/xp-bench")))
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "results" / "raw.jsonl"))
    args = parser.parse_args()

    selected = [scen.BY_ID[s] for s in args.only] if args.only else scen.SCENARIOS
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records: List[Dict[str, object]] = []
    for sc in selected:
        records.extend(run_scenario(sc, workdir))
        for rec in records[-2:]:
            flag = "TP" if rec["true_positive"] else ("FP" if rec["false_positive"] else "--")
            print(f"{rec['scenario']:<24} {rec['arm']:<9} {rec['verdict']:<8} "
                  f"step={rec['blocked_step']} {flag} {rec['duration_s']}s")

    with out_path.open("w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(records)} records to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
