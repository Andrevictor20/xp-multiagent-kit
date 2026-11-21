"""LLM-in-the-loop paired A/B benchmark runner (with vs without XP kit)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

BENCH_DIR = Path(__file__).resolve().parent
KIT_ROOT = BENCH_DIR.parent
if str(BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(BENCH_DIR))
if str(KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(KIT_ROOT))

import llm_adapters
import llm_tasks
import oracles

SUBSTRATE = BENCH_DIR / "substrate"
KIT_PAYLOAD = [
    "AGENTS.md",
    "scripts",
    ".agents/policy.yaml",
    ".agents/graph",
    ".agents/policies",
    ".agents/memory",
    ".agents/agents",
    ".agents/hooks.json",
]


def _ignore(_dir: str, names: List[str]) -> List[str]:
    return [
        n
        for n in names
        if n in ("__pycache__", ".git", "global-token-optimizer", "runtime", ".memory_index.db", "details", "archive")
    ]


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def prepare_arm_sandbox(dest: Path, with_kit: bool) -> Path:
    """Create a clean isolated git sandbox from substrate (with or without kit)."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SUBSTRATE, dest, ignore=_ignore)
    if with_kit:
        for rel in KIT_PAYLOAD:
            src = KIT_ROOT / rel
            if not src.exists():
                continue
            dst = dest / rel
            if src.is_dir():
                shutil.copytree(src, dst, ignore=_ignore)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        idx = dest / ".agents" / "policies" / "INDEX.md"
        if not idx.is_file() and (dest / ".agents" / "policies").is_dir():
            from scripts.policy_index import write_policy_index

            write_policy_index(dest / ".agents" / "policies", idx)
        (dest / ".agents" / "runtime").mkdir(parents=True, exist_ok=True)

    _git(dest, "init", "-q")
    _git(dest, "config", "user.email", "bench@example.com")
    _git(dest, "config", "user.name", "bench")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-qm", "base")
    return dest


def _apply_dry_run_solution(repo: Path, task: llm_tasks.LLMTask, with_kit: bool) -> None:
    """Apply minimal deterministic edits so `--dry-run` validates the full pipeline."""
    if task.tid == "T01_l0_docs_typo":
        readme = repo / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("dependency-free", "dependency free"), encoding="utf-8")
    elif task.tid == "T02_l1_bugfix_tdd":
        parser_p = repo / "app" / "parser.py"
        txt = parser_p.read_text(encoding="utf-8").replace(
            "    if not 1 <= day <= 31:\n        raise ValueError(f\"invalid day: {raw!r}\")\n    return year, month, day",
            "    import datetime\n    if not 1 <= day <= 31:\n        raise ValueError(f\"invalid day: {raw!r}\")\n"
            "    datetime.date(year, month, day)\n    return year, month, day",
        )
        parser_p.write_text(txt, encoding="utf-8")
    if with_kit:
        subprocess.run(
            [sys.executable, "scripts/xp_contract.py", "init", "--risk", task.risk, "--goal", task.goal,
             "--verify", "python3 -m unittest discover -s tests -q", *(["--scope", *task.scope] if task.scope else [])],
            cwd=str(repo), capture_output=True, text=True,
        )


def _run_unittest(repo: Path, pattern: str = "test*.py") -> bool:
    res = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-q"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return res.returncode == 0


def _evaluate_oracles(repo: Path, task: llm_tasks.LLMTask, with_kit: bool) -> Dict[str, List[str]]:
    """Run independent non-circular oracles on the modified sandbox."""
    allowed_scope = list(task.scope)
    if with_kit:
        allowed_scope.extend([".agents/runtime", ".agents/memory"])
    sc_proxy = SimpleNamespace(scope=allowed_scope, acs=task.acs)
    failures: Dict[str, List[str]] = {}
    for check in task.oracle_checks:
        fn = oracles.ORACLES.get(check)
        if not fn:
            continue
        failed, details = fn(repo, sc_proxy, {})
        if failed:
            failures[check] = details
    return failures


def _evaluate_kit_ceremony(repo: Path) -> Dict[str, Any]:
    runtime = repo / ".agents" / "runtime"
    contract_present = (runtime / "run.json").is_file()
    ev_path = runtime / "evidence" / "index.jsonl"
    has_red = has_green = False
    if ev_path.is_file():
        for line in ev_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("exit_code", 0) != 0 or entry.get("status") == "FAIL":
                has_red = True
            elif entry.get("exit_code") == 0:
                has_green = True
    gate = subprocess.run(
        [sys.executable, "scripts/xp_gate.py", "check"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return {
        "contract_present": contract_present,
        "red_green_evidence": has_red and has_green,
        "gate_exit": gate.returncode,
        "gate_pass": gate.returncode == 0,
        "gate_summary": (gate.stdout.strip().splitlines() or [""])[0][:180],
    }


def evaluate_arm(repo: Path, task: llm_tasks.LLMTask, with_kit: bool) -> Dict[str, Any]:
    """Evaluate functional correctness, hidden tests, oracles, and kit ceremony."""
    base_suite_ok = _run_unittest(repo)
    oracle_failures = _evaluate_oracles(repo, task, with_kit=with_kit)
    kit_ceremony = _evaluate_kit_ceremony(repo) if with_kit else {
        "contract_present": False,
        "red_green_evidence": False,
        "gate_exit": None,
        "gate_pass": False,
        "gate_summary": "",
    }

    written_hidden: List[Path] = []
    for rel, content in task.hidden_tests.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written_hidden.append(target)

    hidden_tests_pass = _run_unittest(repo, pattern="test_hidden_*.py") if written_hidden else base_suite_ok
    all_tests_pass = _run_unittest(repo)
    for p in written_hidden:
        if p.is_file():
            p.unlink()

    resolved = bool(base_suite_ok and hidden_tests_pass and all_tests_pass and not oracle_failures)
    claimed_done = base_suite_ok if not with_kit else (base_suite_ok and (kit_ceremony["gate_pass"] or not oracle_failures))
    defect_escaped = bool((not hidden_tests_pass or oracle_failures) and base_suite_ok)

    return {
        "base_suite_ok": base_suite_ok,
        "hidden_tests_pass": hidden_tests_pass,
        "all_tests_pass": all_tests_pass,
        "oracle_failures": oracle_failures,
        "resolved": resolved,
        "claimed_done": claimed_done,
        "defect_escaped": defect_escaped,
        "changed_files": oracles.changed_paths(repo),
        "kit_ceremony": kit_ceremony,
    }


def run_single_arm(
    task: llm_tasks.LLMTask,
    arm: str,
    run_idx: int,
    runner_name: str,
    workdir: Path,
    model: Optional[str] = None,
    effort: Optional[str] = None,
    timeout_s: int = 240,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Run one task on one arm (`baseline` or `kit`) and return structured metrics."""
    with_kit = arm == "kit"
    sandbox = workdir / f"run{run_idx}_{task.tid}__{arm}"
    env_home = workdir / f"home_{arm}"
    log_path = workdir / "logs" / f"run{run_idx}_{task.tid}__{arm}.log"
    prepare_arm_sandbox(sandbox, with_kit=with_kit)

    if dry_run:
        _apply_dry_run_solution(sandbox, task, with_kit=with_kit)
        llm_res = llm_adapters.LLMRunResult(
            runner=runner_name,
            model=model or "dry-run",
            exit_code=0,
            duration_s=0.05,
            input_tokens=1800 if with_kit else 900,
            output_tokens=200,
            cache_read_tokens=400 if with_kit else 0,
            total_tokens=2400 if with_kit else 1100,
            turns=2,
            tool_calls=3,
            status="dry_run",
        )
    else:
        llm_res = llm_adapters.execute_runner(
            runner_name=runner_name,
            prompt=task.prompt,
            sandbox_dir=sandbox,
            with_kit=with_kit,
            env_home=env_home,
            log_path=log_path,
            model=model,
            effort=effort,
            timeout_s=timeout_s,
        )

    ev = evaluate_arm(sandbox, task, with_kit=with_kit)
    return {
        "task": task.tid,
        "risk": task.risk,
        "arm": arm,
        "run": run_idx,
        **llm_res.to_dict(),
        **ev,
    }


def _to_eval_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "task": rec["task"],
        "risk": rec["risk"],
        "gate_pass": bool(rec["resolved"]),
        "first_gate_pass": bool(rec["resolved"] and rec.get("exit_code", 1) == 0),
        "repeat_failures": 0,
        "human_interventions": 0,
        "gate_verdict_present": bool(rec.get("kit_ceremony", {}).get("contract_present")) if rec["arm"] == "kit" else False,
        "turns": int(rec.get("turns", 1)),
        "duration_seconds": float(rec.get("duration_s", 0.0)),
        "total_tokens": int(rec.get("total_tokens", 0)),
        "defect_expected": bool(rec.get("defect_escaped", False)),
    }


def run_benchmark(
    task_ids: Optional[List[str]] = None,
    runner_name: str = "agy",
    model: Optional[str] = None,
    effort: Optional[str] = None,
    runs: int = 1,
    timeout_s: int = 240,
    workdir: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:
    """Run paired LLM benchmark tasks and write JSONL outputs."""
    selected = [llm_tasks.BY_ID[tid] for tid in task_ids] if task_ids else llm_tasks.TASKS
    wdir = workdir or Path("/tmp/opencode/xp-llm-bench")
    odir = out_dir or (BENCH_DIR / "results")
    wdir.mkdir(parents=True, exist_ok=True)
    odir.mkdir(parents=True, exist_ok=True)

    records: List[Dict[str, Any]] = []
    for run_idx in range(1, runs + 1):
        for task in selected:
            for arm in ("baseline", "kit"):
                rec = run_single_arm(
                    task=task,
                    arm=arm,
                    run_idx=run_idx,
                    runner_name=runner_name,
                    workdir=wdir,
                    model=model,
                    effort=effort,
                    timeout_s=timeout_s,
                    dry_run=dry_run,
                )
                records.append(rec)
                print(
                    f"[run {run_idx}] {task.tid:<24} {arm:<8} resolved={rec['resolved']} "
                    f"tokens={rec['total_tokens']} turns={rec['turns']} {rec['duration_s']}s"
                )

    raw_path = odir / "llm_raw.jsonl"
    raw_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    for arm in ("baseline", "kit"):
        arm_recs = [_to_eval_record(r) for r in records if r["arm"] == arm]
        (odir / f"llm_{arm}.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in arm_recs) + "\n",
            encoding="utf-8",
        )
    return records


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="XP Kit paired LLM-in-the-loop benchmark")
    parser.add_argument("--runner", default="agy", choices=llm_adapters.SUPPORTED_RUNNERS)
    parser.add_argument("--model", default=None, help="Optional model override for the CLI")
    parser.add_argument("--effort", default=None, help="Optional reasoning effort (agy only)")
    parser.add_argument("--only", nargs="*", default=None, help="Subset of task IDs to execute")
    parser.add_argument("--runs", type=int, default=1, help="Number of paired repetitions")
    parser.add_argument("--timeout", type=int, default=240, help="Per-arm timeout in seconds")
    parser.add_argument("--workdir", default="/tmp/opencode/xp-llm-bench")
    parser.add_argument("--out-dir", default=str(BENCH_DIR / "results"))
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline without invoking real LLMs")
    args = parser.parse_args()

    run_benchmark(
        task_ids=args.only,
        runner_name=args.runner,
        model=args.model,
        effort=args.effort,
        runs=args.runs,
        timeout_s=args.timeout,
        workdir=Path(args.workdir),
        out_dir=Path(args.out_dir),
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
