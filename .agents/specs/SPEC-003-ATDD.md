# SPEC-003: XP Multi-Agent Kit v3.0 — Multi-Host Agnosticism, Token-Dense English Core, Compact Colored Telemetry & Self-Healing Engine

> **Status:** APPROVED (Stop Gate Confirmed by User on 2026-10-16)  
> **Risk Level:** L2/L3  
> **Workflow:** `/feature` (ATDD Specification Pyramid)

---

## 1. Acceptance Criteria (AC)

### AC-1: Multi-Host Agnostic Installer (Antigravity, OpenCode, Cursor, Qoder — IDE & CLI)
- **Given:** A user on any workspace or system using Antigravity, OpenCode, Cursor, or Qoder (IDE or CLI)
- **When:** Running `install.sh` or `xp-kit` / `agy-kit` (`init`, `install`, `sync`, `doctor`) with `--target [all|antigravity|opencode|cursor|qoder]`
- **Then:** The installer provisions global and/or project-level configurations for the selected target(s):
  - **Antigravity (IDE & CLI):** `.agents/`, `AGENTS.md`, `.geminiignore`, `.antigravityignore`, `~/.gemini/config/` & hooks.
  - **OpenCode (IDE & CLI):** `opencode.json` (instructions + MCP servers), `.opencode/agent/*.md` (11 agents), `.opencode/command/*.md` (11 workflows), and `~/.config/opencode/` global sync.
  - **Cursor (IDE & CLI):** `.cursor/rules/*.mdc` (`00-xp-core.mdc`, `10-frontend-design.mdc`, `20-tdd-testing.mdc`), `.cursor/mcp.json`, `.cursorignore`.
  - **Qoder (IDE & CLI):** `.qoder/rules/xp-governance.md`, `.qoderignore`, `AGENTS.md`, `.qoder/mcp.json`.
- **Metric:** `tests/test_kit_installer.py` and `tests/test_spec_003_v3.py` verify all 4 host adapters (project & global).

### AC-2: Bilingual Installer (PT/EN) with Automatic OS Locale Detection
- **Given:** A computer with OS locale set to Portuguese (`pt_BR`, `pt_PT`) or English/other (`en_US`, `C`, etc.)
- **When:** Running `install.sh` or `scripts/kit_installer.py` (interactive wizard, CLI flags, or `doctor`)
- **Then:** The installer automatically detects the system language from environment variables (`LC_ALL`, `LC_MESSAGES`, `LANG`) or `--lang [pt|en]` flag and renders all prompts, diagnostics, and status messages in Portuguese or English accordingly.
- **Metric:** Unit & acceptance tests verify `detect_system_language()` and bilingual output in `pt` and `en`.

### AC-3: Token-Dense English Internal Core with Portuguese User Output Preservation
- **Given:** The kit's internal `.agents/` governance files (`AGENTS.md`, 77 `skills/*/SKILL.md`, 11 `workflows/*.md`, 11 `agents/*/agent.md`, 12 `policies/*.md`, `rules/*.md`, `SKILLS_INDEX.md`)
- **When:** Loaded into the LLM context
- **Then:** All internal instructions, rules, workflows, and skills are written in concise, token-dense imperative English, while explicitly enforcing that **all user-facing responses, explanations, and reports remain in Portuguese** (or the user's prompt language).
- **Metric:** Audit confirms English frontmatter/instructions across `.agents/{skills,workflows,agents,policies}` and explicit Portuguese output mandate in `AGENTS.md`.

### AC-4: Compact, Visually Clean & ANSI-Colored Token Telemetry
- **Given:** Token telemetry execution via `agy-tokens` / `xp-tokens` (`--turn`, `--color`, default CLI)
- **When:** Formatting the turn footer or terminal view
- **Then:**
  1. Displays **only** the essential metrics: **Contexto, Limites (5h & Semanal), Consumo, and Modelo** in a clean, compact 3-line (or 4-line) layout without `Reenvio:` or `RTK:` clutter.
  2. Supports **ANSI colors** in terminal output (Green `<50%`, Yellow `50-80%`, Red `>80%`, Cyan/Bold headers) via `--color` or TTY auto-detection, while keeping Markdown chat footers clean of raw ANSI escape codes.
  3. Dynamically detects any new model name (e.g., `Gemini 4 Argon (High)`) from transcript/settings without falling back to a hardcoded `Gemini 3.8 Flash`.
  4. Probes CLI Language Server local HTTP/HTTPS ports from `cli.log` even when `--csrf_token` is absent from `/proc/*/cmdline`, and falls back to local rolling window usage (`X.Xk usados na janela local`) instead of `"Não está sendo possível aferir no momento"`.
- **Metric:** Unit tests verify dynamic model detection (`Gemini 4 Argon (High)`), compact 3-line footer structure, ANSI color rendering, and 5h/weekly fallback.

### AC-5: Autonomous Self-Correction & Error Reflexion Engine
- **Given:** An agent executing commands or editing files during a task
- **When:** A tool call fails (`exit_code != 0`, traceback, test failure) or code is edited without running subsequent verification tests
- **Then:**
  1. `tool-size-guard.py` (PostToolUse) and `agy-run` detect failure signatures and inject an immediate `[SELF-HEAL TRIGGER]` directive instructing the agent to diagnose and fix the root cause autonomously before responding.
  2. `smart_tool_optimizer.py` tracks turn state (`dirty_code_untested`, `edited_files`, `errors_pending`) in `.agents/runtime/turn_state.json`.
  3. `AGENTS.md` and workflows enforce a mandatory **Pre-Response Self-Audit** (Goal Check, Green Check, Memory Check).
- **Metric:** Unit tests verify `[SELF-HEAL TRIGGER]` injection on failed command payloads and `turn_state.json` dirty/clean tracking.

### AC-6: Token & Tool-Call Reduction + God File Decomposition (< 500 Lines)
- **Given:** Multi-step tool execution in a single user turn and the kit's Python codebase
- **When:** `dynamic_effort_hook.py` and `smart_tool_optimizer.py` run, and the codebase is audited for file size
- **Then:**
  1. `dynamic_effort_hook.py` deduplicates `ephemeralMessage` injection per user prompt (`conversation_id + prompt_hash`), injecting at most once per user turn instead of on every tool step.
  2. `smart_tool_optimizer.py` allows explicit `view_file` ranges up to `WHOLE_FILE_READ_MAX_LINES` (800 lines) in a single call.
  3. `scripts/token_tracker.py` is decomposed into `scripts/telemetry/` modules so `scripts/token_tracker.py` is `< 500` lines while preserving 100% backward-compatible imports.
- **Metric:** All unit tests pass (`GREEN`) and `wc -l scripts/token_tracker.py` is `< 500`.
