"""Mechanical cost measurements for the XP kit benchmark.

Measures the parts that are deterministic and reproducible without an LLM in
the loop: fixed governance context, hook latency per tool call, gate latency,
and just-in-time context retrieval size.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

import runner

PY = sys.executable
BENCH = Path(__file__).resolve().parent

BENIGN_COMMANDS = [
    "python3 -m unittest discover -s tests -q",
    "git status",
    "ls -la app",
    'grep -rn "TODO" app',
    "cat README.md",
    "python3 -m compileall -q app",
    'git commit -m "feat: add formatter"',
    "git diff --stat",
]

DANGEROUS_COMMANDS = [
    "rm -rf /tmp/build",
    'psql -c "DROP TABLE users"',
    "git push --force origin main",
    "terraform apply -auto-approve",
    "docker push registry.local/app:latest",
    "npm publish",
]

DANGEROUS_WRITES = [
    ".agents/policy.yaml",
    ".agents/runtime/approvals.json",
]

JIT_QUERIES = [
    "policy approval destructive command",
    "tdd red green evidence",
    "token budget base context",
    "god file 500 lines",
    "dead ends failed attempts",
    "zero downtime rollback",
]


def hook_payload(tool: str, args: Dict[str, str]) -> str:
    return json.dumps({"tool_name": tool, "tool_args": args})


def call_hook(repo: Path, payload: str) -> Dict[str, object]:
    started = time.perf_counter()
    res = subprocess.run(
        [PY, "scripts/hooks/pre_tool_guard.py"],
        cwd=str(repo), input=payload, capture_output=True, text=True,
    )
    elapsed = (time.perf_counter() - started) * 1000
    try:
        decision = json.loads(res.stdout).get("decision")
    except json.JSONDecodeError:
        decision = "error"
    return {"decision": decision, "ms": elapsed}


def percentile(values: List[float], pct: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(pct / 100 * len(ordered))) - 1))
    return ordered[index]


def measure_hook(repo: Path) -> Dict[str, object]:
    latencies: List[float] = []
    benign_decisions: List[str] = []
    for _ in range(5):
        for command in BENIGN_COMMANDS:
            result = call_hook(repo, hook_payload("Bash", {"command": command}))
            latencies.append(result["ms"])
            benign_decisions.append(result["decision"])
    for _ in range(5):
        for command in DANGEROUS_COMMANDS:
            result = call_hook(repo, hook_payload("Bash", {"command": command}))
            latencies.append(result["ms"])
    dangerous_hits = 0
    for command in DANGEROUS_COMMANDS:
        if call_hook(repo, hook_payload("Bash", {"command": command}))["decision"] == "deny":
            dangerous_hits += 1
    for path in DANGEROUS_WRITES:
        if call_hook(repo, hook_payload("Write", {"Path": path}))["decision"] == "deny":
            dangerous_hits += 1
    return {
        "calls": len(latencies) + len(DANGEROUS_WRITES),
        "median_ms": round(statistics.median(latencies), 1),
        "p95_ms": round(percentile(latencies, 95), 1),
        "min_ms": round(min(latencies), 1),
        "max_ms": round(max(latencies), 1),
        "benign_allowed": sum(1 for d in benign_decisions if d == "allow"),
        "benign_total": len(benign_decisions),
        "dangerous_blocked": dangerous_hits,
        "dangerous_total": len(DANGEROUS_COMMANDS) + len(DANGEROUS_WRITES),
        "projected_ms_per_50_calls": round(statistics.median(latencies) * 50, 0),
    }


def measure_gate(repo: Path, rounds: int = 3) -> Dict[str, object]:
    times: List[float] = []
    codes: List[int] = []
    for _ in range(rounds):
        code, _out, elapsed = runner.run_cmd(repo, [PY, "scripts/xp_gate.py", "check"])
        times.append(elapsed)
        codes.append(code)
    return {
        "rounds": rounds,
        "median_s": round(statistics.median(times), 3),
        "min_s": round(min(times), 3),
        "max_s": round(max(times), 3),
        "exit_codes": codes,
    }


def measure_jit(repo: Path) -> Dict[str, object]:
    corpus = 0
    for rel in [Path("AGENTS.md"), Path(".agents/memory/PROJECT_MEMORY.md")]:
        path = repo / rel
        if path.is_file():
            corpus += path.stat().st_size
    for path in Path(repo / ".agents/policies").glob("*.md"):
        corpus += path.stat().st_size
    samples = []
    for query in JIT_QUERIES:
        code, out, elapsed = runner.run_cmd(repo, [PY, "scripts/context_retriever.py", query])
        samples.append({
            "query": query,
            "bytes": len(out),
            "items": out.count("- **["),
            "ms": round(elapsed * 1000, 0),
            "empty": len(out.strip()) == 0,
            "exit": code,
        })
    sizes = [s["bytes"] for s in samples]
    return {
        "corpus_bytes": corpus,
        "samples": samples,
        "median_bytes": round(statistics.median(sizes), 0),
        "max_bytes": max(sizes),
        "reduction_pct": round((1 - statistics.median(sizes) / corpus) * 100, 1) if corpus else 0.0,
    }


def measure_suite(repo: Path, rounds: int = 3) -> Dict[str, object]:
    times: List[float] = []
    codes: List[int] = []
    for _ in range(rounds):
        code, _out, elapsed = runner.run_cmd(
            repo, [PY, "-m", "unittest", "discover", "-s", "tests", "-q"]
        )
        times.append(elapsed)
        codes.append(code)
    return {
        "rounds": rounds,
        "median_s": round(statistics.median(times), 3),
        "min_s": round(min(times), 3),
        "max_s": round(max(times), 3),
        "exit_codes": codes,
    }


def measure_token_optimizers(kit_root_path: Path | None = None) -> Dict[str, object]:
    """Measure deterministic token reduction from Lean v4 optimizers."""
    import os
    import tempfile

    root = (kit_root_path or BENCH.parent).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from scripts.context_compactor import compress_ci_output, compress_diff, compress_git_output, compress_logs
    from scripts.hooks.smart_tool_optimizer import optimize_tool_call, reset_tool_loop_history
    from scripts.hooks.smart_tool_optimizer_state import record_file_edit
    from scripts.repo_map import generate_repo_map

    # 1. Context compactor reduction across realistic noisy outputs
    sample_ci = "\n".join(
        [f"PASS tests/test_mod_{i}.py::test_case_{j} (0.01s)" for i in range(40) for j in range(3)]
        + ["FAIL tests/test_auth.py::test_rejects_expired_token", "AssertionError: expected 401 got 200"]
    )
    sample_diff = "\n".join(
        ["diff --git a/app/service.py b/app/service.py", "--- a/app/service.py", "+++ b/app/service.py", "@@ -1,50 +1,52 @@"]
        + [f" unchanged line {i}" for i in range(60)]
        + ["+    cleaned = clean_title(title)", "-    cleaned = title.strip()"]
        + [f" trailing line {i}" for i in range(40)]
    )
    sample_git = "\n".join([f"{i:07x} feat: commit message number {i} touching module" for i in range(80)])
    sample_logs = "\n".join(
        ["INFO starting worker"] * 30 + ["ERROR connection refused on port 5432"] * 12 + ["INFO done"] * 20
    )
    raw_samples = [sample_ci, sample_diff, sample_git, sample_logs]
    comp_samples = [
        compress_ci_output(sample_ci),
        compress_diff(sample_diff),
        compress_git_output(sample_git),
        compress_logs(sample_logs),
    ]
    raw_bytes = sum(len(s.encode("utf-8")) for s in raw_samples)
    comp_bytes = sum(len(s.encode("utf-8")) for s in comp_samples)

    # 2. Repo map vs full source tree read
    substrate_dir = BENCH / "substrate"
    full_tree_bytes = sum(
        p.stat().st_size
        for p in substrate_dir.rglob("*.py")
        if "__pycache__" not in str(p)
    )
    map_text = generate_repo_map(substrate_dir)
    map_bytes = len(map_text.encode("utf-8"))

    # 3. Smart tool optimizer checks (in isolated temp runtime dir)
    prev_rt = os.environ.get("KIT_RUNTIME_DIR")
    with tempfile.TemporaryDirectory() as tmp_rt:
        os.environ["KIT_RUNTIME_DIR"] = tmp_rt
        try:
            reset_tool_loop_history()
            rewrites = 0
            for cmd in ("pytest -v", "git log", "find . -name '*.py'"):
                res = optimize_tool_call({"toolCall": {"name": "run_command", "args": {"CommandLine": cmd}}})
                if res.get("overwrite"):
                    rewrites += 1

            target_py = str(substrate_dir / "app" / "service.py")
            record_file_edit(target_py)
            reread_res = optimize_tool_call({"toolCall": {"name": "view_file", "args": {"AbsolutePath": target_py}}})

            loop_blocked = False
            for _ in range(5):
                loop_res = optimize_tool_call({"toolCall": {"name": "grep_search", "args": {"Query": "foo", "SearchPath": str(substrate_dir)}}})
                if loop_res.get("decision") == "deny":
                    loop_blocked = True
                    break
        finally:
            if prev_rt is None:
                os.environ.pop("KIT_RUNTIME_DIR", None)
            else:
                os.environ["KIT_RUNTIME_DIR"] = prev_rt

    fixed_bytes = runner.fixed_context_bytes(root)
    return {
        "context_compactor": {
            "raw_bytes": raw_bytes,
            "compacted_bytes": comp_bytes,
            "reduction_pct": round((1 - comp_bytes / raw_bytes) * 100, 1) if raw_bytes else 0.0,
        },
        "repo_map": {
            "full_tree_bytes": full_tree_bytes,
            "map_bytes": map_bytes,
            "reduction_pct": round((1 - map_bytes / full_tree_bytes) * 100, 1) if full_tree_bytes else 0.0,
        },
        "smart_tool_optimizer": {
            "verbose_rewrites": rewrites,
            "reread_blocked": reread_res.get("decision") == "deny",
            "loop_blocked": loop_blocked,
        },
        "context_base_lean": {
            "fixed_bytes": fixed_bytes,
            "approx_tokens": round(fixed_bytes / 4),
        },
    }


def main() -> int:
    workdir = Path("/tmp/opencode/xp-overhead")
    kit_repo = runner.build_sandbox(workdir / "kit", with_kit=True)
    base_repo = runner.build_sandbox(workdir / "base", with_kit=False)
    # Garante o índice de políticas no sandbox (equivalente ao estado entregue).
    runner._ensure_policy_index(kit_repo)

    scenario = __import__("scenarios").BY_ID["B02_small_feature"]
    runner.arm_kit(kit_repo, scenario)

    data = {
        "governance": {
            "agents_md_bytes": (kit_repo / "AGENTS.md").stat().st_size,
            "memory_bytes": (kit_repo / ".agents/memory/PROJECT_MEMORY.md").stat().st_size,
            "policies_index_bytes": (kit_repo / ".agents/policies/INDEX.md").stat().st_size
                                    if (kit_repo / ".agents/policies/INDEX.md").is_file() else 0,
            "policies_full_bytes": sum(p.stat().st_size for p in (kit_repo / ".agents/policies").glob("*.md")
                                       if p.name != "INDEX.md"),
            "fixed_context_bytes": runner.fixed_context_bytes(kit_repo),
            "approx_tokens": round(runner.governance_bytes(kit_repo) / 4),
        },
        "hook": measure_hook(kit_repo),
        "gate_kit": measure_gate(kit_repo),
        "suite_baseline": measure_suite(base_repo),
        "jit": measure_jit(kit_repo),
        "token_optimizers": measure_token_optimizers(runner.KIT_ROOT),
    }
    out_path = BENCH / "results" / "overhead.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
