"""Multi-CLI LLM runner adapters and baseline isolation for the XP kit benchmark."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

SUPPORTED_RUNNERS = ("agy", "claude", "codex", "gemini")


@dataclass
class LLMRunResult:
    """Normalized execution and token telemetry returned by any agent CLI."""

    runner: str
    model: str
    exit_code: int
    duration_s: float
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    turns: int = 0
    tool_calls: int = 0
    status: str = "ok"
    response_preview: str = ""
    raw_log_path: str = ""
    error: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def resolve_binary(runner_name: str) -> Optional[str]:
    """Resolve the underlying executable for a runner (preferring agy-native)."""
    if runner_name == "agy":
        for candidate in (
            shutil.which("agy-native"),
            str(Path.home() / ".local" / "bin" / "agy-native"),
            shutil.which("agy"),
        ):
            if candidate and Path(candidate).is_file():
                return str(candidate)
        return None
    return shutil.which(runner_name)


def build_command(
    runner_name: str,
    prompt: str,
    model: Optional[str] = None,
    effort: Optional[str] = None,
    disable_slash_commands: bool = False,
    binary: Optional[str] = None,
) -> List[str]:
    """Build a non-interactive CLI command for the given agent runner."""
    exe = binary or resolve_binary(runner_name) or runner_name
    if runner_name == "agy":
        cmd = [
            exe,
            "--output-format",
            "json",
            "--mode",
            "auto",
            "--dangerously-skip-permissions",
        ]
        if disable_slash_commands:
            cmd.append("--disable-slash-commands")
        if model:
            cmd.extend(["--model", model])
        if effort:
            cmd.extend(["--effort", effort])
        cmd.append(f"--print={prompt}")
        return cmd

    if runner_name == "claude":
        cmd = [exe, "-p", prompt, "--output-format", "json", "--dangerously-skip-permissions"]
        if model:
            cmd.extend(["--model", model])
        return cmd

    if runner_name == "codex":
        cmd = [exe, "exec", "--json", "--sandbox", "workspace-write"]
        if model:
            cmd.extend(["-m", model])
        cmd.append(prompt)
        return cmd

    if runner_name == "gemini":
        cmd = [exe, "-p", prompt, "-y", "--output-format", "json"]
        if model:
            cmd.extend(["-m", model])
        return cmd

    raise ValueError(f"Unsupported runner: {runner_name}")


def _symlink_if_exists(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)


def prepare_isolated_env(
    runner_name: str,
    with_kit: bool,
    sandbox_dir: Path,
    env_home: Path,
) -> Dict[str, str]:
    """Prepare an isolated environment so baseline runs without global kit hooks/rules."""
    env = os.environ.copy()
    real_home = Path.home()
    env_home.mkdir(parents=True, exist_ok=True)

    # Preserve baseline auth/session stores while stripping global XP kit config/hooks.
    gemini_dst = env_home / ".gemini"
    gemini_cfg_dst = gemini_dst / "config"
    gemini_cfg_dst.mkdir(parents=True, exist_ok=True)
    for auth_dir in ("antigravity", "user_id", "oauth_creds.json"):
        _symlink_if_exists(real_home / ".gemini" / auth_dir, gemini_dst / auth_dir)

    cli_src = real_home / ".gemini" / "antigravity-cli"
    cli_dst = gemini_dst / "antigravity-cli"
    cli_dst.mkdir(parents=True, exist_ok=True)
    kit_cli_entries = {"AGENTS.md", "agents", "hooks.json", "memory", "policies", "skills", "templates"}
    if cli_src.is_dir():
        for entry in cli_src.iterdir():
            if entry.name in kit_cli_entries and not with_kit:
                continue
            if entry.name == "hooks.json" and with_kit:
                continue
            _symlink_if_exists(entry, cli_dst / entry.name)

    if not with_kit:
        settings_src = real_home / ".gemini" / "config" / "settings.json"
        if settings_src.is_file():
            shutil.copy2(settings_src, gemini_cfg_dst / "settings.json")
        (gemini_cfg_dst / "hooks.json").write_text("{}", encoding="utf-8")
        (cli_dst / "hooks.json").write_text("{}", encoding="utf-8")
        (gemini_cfg_dst / "AGENTS.md").write_text("", encoding="utf-8")
        (cli_dst / "AGENTS.md").write_text("", encoding="utf-8")
        _symlink_if_exists(real_home / ".claude", env_home / ".claude")
        _symlink_if_exists(real_home / ".codex", env_home / ".codex")
        env["HOME"] = str(env_home)
        env.pop("KIT_ROOT", None)
        env.pop("KIT_RUNTIME_DIR", None)
        return env

    # Kit arm: mirror auth + bind hooks/runtime explicitly to the sandbox repo.
    _symlink_if_exists(real_home / ".claude", env_home / ".claude")
    _symlink_if_exists(real_home / ".codex", env_home / ".codex")
    settings_src = real_home / ".gemini" / "config" / "settings.json"
    if settings_src.is_file():
        shutil.copy2(settings_src, gemini_cfg_dst / "settings.json")
    sandbox_hooks = sandbox_dir / ".agents" / "hooks.json"
    if sandbox_hooks.is_file():
        rendered = sandbox_hooks.read_text(encoding="utf-8").replace(
            "${KIT_ROOT}", str(sandbox_dir)
        )
        (gemini_cfg_dst / "hooks.json").write_text(rendered, encoding="utf-8")
        (cli_dst / "hooks.json").write_text(rendered, encoding="utf-8")
    env["HOME"] = str(env_home)
    env["KIT_ROOT"] = str(sandbox_dir)
    env["KIT_RUNTIME_DIR"] = str(sandbox_dir / ".agents" / "runtime")
    return env


def _safe_int(val: Any) -> int:
    try:
        return int(val or 0)
    except (TypeError, ValueError):
        return 0


def _extract_json_objects(raw_text: str) -> List[Dict[str, Any]]:
    stripped = raw_text.strip()
    if not stripped:
        return []
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return [obj]
        if isinstance(obj, list):
            return [item for item in obj if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass

    objs: List[Dict[str, Any]] = []
    for line in stripped.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            objs.append(item)
    return objs


def parse_runner_output(
    runner_name: str,
    raw_text: str,
    exit_code: int,
    elapsed_s: float,
    model: str = "",
) -> LLMRunResult:
    """Parse JSON or NDJSON output from supported CLIs into LLMRunResult."""
    objs = _extract_json_objects(raw_text)
    if not objs:
        return LLMRunResult(
            runner=runner_name,
            model=model,
            exit_code=exit_code,
            duration_s=round(elapsed_s, 3),
            status="error" if exit_code != 0 else "ok",
            response_preview=raw_text.strip()[:240],
            error="" if exit_code == 0 else raw_text.strip()[:240],
        )

    result_obj = next((o for o in reversed(objs) if o.get("type") == "result"), objs[-1])
    tool_calls = 0
    for o in objs:
        msg = o.get("message")
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            tool_calls += sum(1 for c in msg["content"] if isinstance(c, dict) and c.get("type") == "tool_use")
        item = o.get("item")
        if o.get("type") == "item.completed" and isinstance(item, dict):
            if item.get("type") in ("command_execution", "file_change", "mcp_tool_call", "tool_call"):
                tool_calls += 1

    # Gemini CLI stats.models schema
    stats = result_obj.get("stats")
    if isinstance(stats, dict) and isinstance(stats.get("models"), dict):
        inp = out = cached = thoughts = tot = reqs = 0
        for m_data in stats["models"].values():
            if not isinstance(m_data, dict):
                continue
            tok = m_data.get("tokens", {})
            inp += _safe_int(tok.get("input"))
            out += _safe_int(tok.get("candidates"))
            cached += _safe_int(tok.get("cached"))
            thoughts += _safe_int(tok.get("thoughts"))
            tot += _safe_int(tok.get("total"))
            reqs += _safe_int(m_data.get("api", {}).get("totalRequests"))
        return LLMRunResult(
            runner=runner_name,
            model=model or next(iter(stats["models"].keys()), ""),
            exit_code=exit_code,
            duration_s=round(elapsed_s, 3),
            input_tokens=inp,
            output_tokens=out + thoughts,
            cache_read_tokens=cached,
            thinking_tokens=thoughts,
            total_tokens=tot or (inp + out + thoughts),
            turns=reqs or 1,
            tool_calls=tool_calls,
            status="error" if exit_code != 0 else "ok",
            response_preview=str(result_obj.get("response", ""))[:240],
        )

    # Codex turn.completed / Agy / Claude usage schema
    usage = result_obj.get("usage")
    if not isinstance(usage, dict):
        turn_ev = next((o for o in reversed(objs) if isinstance(o.get("usage"), dict)), {})
        usage = turn_ev.get("usage", {}) if isinstance(turn_ev, dict) else {}

    inp = _safe_int(usage.get("input_tokens"))
    out = _safe_int(usage.get("output_tokens"))
    thinking = _safe_int(usage.get("thinking_tokens"))
    cache_read = _safe_int(
        usage.get("cache_read_tokens")
        or usage.get("cache_read_input_tokens")
        or usage.get("cached_input_tokens")
    )
    cache_write = _safe_int(usage.get("cache_creation_input_tokens"))
    if runner_name == "codex":
        total = _safe_int(usage.get("total_tokens")) or (inp + out)
    else:
        total = _safe_int(usage.get("total_tokens")) or (inp + out + thinking + cache_read + cache_write)

    turns = _safe_int(result_obj.get("num_turns")) or sum(1 for o in objs if o.get("type") == "turn.completed") or 1
    duration = float(result_obj.get("duration_seconds") or (result_obj.get("duration_ms", 0) / 1000.0) or elapsed_s)
    cost = float(result_obj.get("total_cost_usd") or 0.0)
    is_err = bool(result_obj.get("is_error")) or exit_code != 0 or str(result_obj.get("status", "")).upper() == "ERROR"
    preview = str(result_obj.get("response") or result_obj.get("result") or "")[:240]

    return LLMRunResult(
        runner=runner_name,
        model=model or str(result_obj.get("model", "")),
        exit_code=exit_code,
        duration_s=round(duration, 3),
        input_tokens=inp,
        output_tokens=out,
        cache_read_tokens=cache_read,
        cache_creation_tokens=cache_write,
        thinking_tokens=thinking,
        total_tokens=total,
        cost_usd=round(cost, 6),
        turns=turns,
        tool_calls=tool_calls,
        status="error" if is_err else "ok",
        response_preview=preview,
        error=preview if is_err else "",
    )


def execute_runner(
    runner_name: str,
    prompt: str,
    sandbox_dir: Path,
    with_kit: bool,
    env_home: Path,
    log_path: Path,
    model: Optional[str] = None,
    effort: Optional[str] = None,
    timeout_s: int = 240,
) -> LLMRunResult:
    """Invoke the selected agent CLI inside `sandbox_dir` and parse token telemetry."""
    exe = resolve_binary(runner_name)
    if not exe:
        return LLMRunResult(
            runner=runner_name,
            model=model or "",
            exit_code=127,
            duration_s=0.0,
            status="missing_binary",
            error=f"CLI '{runner_name}' not found on PATH",
        )

    env = prepare_isolated_env(runner_name, with_kit=with_kit, sandbox_dir=sandbox_dir, env_home=env_home)
    cmd = build_command(
        runner_name=runner_name,
        prompt=prompt,
        model=model,
        effort=effort,
        disable_slash_commands=(runner_name == "agy" and not with_kit),
        binary=exe,
    )
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(sandbox_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        elapsed = time.perf_counter() - started
        raw_out = proc.stdout or ""
        raw_err = proc.stderr or ""
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(raw_out + ("\n[STDERR]\n" + raw_err if raw_err else ""), encoding="utf-8")
        res = parse_runner_output(runner_name, raw_out, proc.returncode, elapsed, model=model or "")
        res.raw_log_path = str(log_path)
        if proc.returncode != 0 and not res.error:
            res.error = raw_err.strip()[:240]
        return res
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(f"TIMEOUT after {timeout_s}s\n{exc.stdout or ''}\n{exc.stderr or ''}", encoding="utf-8")
        return LLMRunResult(
            runner=runner_name,
            model=model or "",
            exit_code=124,
            duration_s=round(elapsed, 3),
            status="timeout",
            raw_log_path=str(log_path),
            error=f"Timed out after {timeout_s}s",
        )
