# XP Multi-Agent Kit v3.1 (Agnostic Core)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Hosts: Antigravity | OpenCode | Cursor | Codex | Qoder](https://img.shields.io/badge/hosts-5%20platforms-brightgreen.svg)](#supported-hosts--architecture)
[![TDD: Strict RED-GREEN](https://img.shields.io/badge/TDD-strict-success.svg)](#strict-tdd--anti-test-bypass)

A high-performance, token-efficient multi-agent governance kit designed for AI pair programming. Built on Extreme Programming (XP) disciplines, adaptive risk routing (L0–L3), and native cross-platform support across **Antigravity**, **OpenCode**, **Cursor**, **Codex**, and **Qoder** (both IDE and CLI environments).

> **Golden Rule**: Always use the minimum number of agents, skills, and turns required to produce a correct, tested, secure, accessible, observable, and maintainable change.

---

## Architecture & Core Disciplines

```text
                                 [HUMAN GOAL]
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                 Risk Triage (L0-L3)      Host Detection & Adapter
                         │                (Antigravity/OpenCode/Cursor/Codex/Qoder)
                         ▼
             ATDD Specification Pyramid
             (ACs → SbE Tables → Gherkin)
                         │
             ⏸️ Human Stop Gate (L2/L3)
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
    RED Test Harness             RTK Token Compression
   (Multi-layer Matrix)          (Rust Token Killer v0.49)
         │                               │
         └───────────────┬───────────────┘
                         ▼
                GREEN Implementation
             (Minimal code, No Workarounds)
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
    Refactor & Deslop             Conformance Report
   (No God Files <500)            (Traceability AC → Tests)
                         │
                         ▼
             4-Tier Project Memory Sync
           (Working, Episodic, Semantic, Procedural)
```

1. **Specification Pyramid & Human-AI Contract Separation (`xp-spec`)**:
   - Solves the silent failure mode: *"100% of tests pass, but the tests test the wrong requirement."*
   - Humans define **WHAT** (Acceptance Criteria, Specification by Example tables, Gherkin scenarios).
   - AI implements **HOW** (parameterized RED tests, minimal GREEN implementation, atomic refactoring).
   - Strictly enforces the **Anti-Self-Test Rule**: AI never author both ACs and tests without human Stop Gate confirmation.
2. **Strict TDD & Anti-Test-Bypass Matrix**:
   - Zero Blind Mocks: production code must never mock its own core logic.
   - Zero Empty Assertions: every test must assert business invariants and concrete values.
   - Zero Unauthorized Skips: `.skip`, `xit`, or `@pytest.mark.skip` are strictly forbidden to hide failures.
   - Failures must be resolved at the root cause; failing tests may never be commented out or deleted.
3. **Continuous 4-Tier Memory & AST Cartography**:
   - Fast Context Bootstrap (< 2,000 tokens) via `.agents/memory/PROJECT_MEMORY.md`.
   - Hierarchical tiers: Working (active turn), Episodic (`archive/HISTORY.md`), Semantic (ADRs and architecture), Procedural (`[L-NNN]` lessons learned).
   - AST dependency mapping via `code-review-graph` (`xp-graph`) to prevent blind file exploration.
4. **Token Economy & Semantic Compression**:
   - PreToolUse optimization hooks (`smart_tool_optimizer.py`) with loop detection and output clamping.
   - Native integration with **RTK (Rust Token Killer)**: up to 90% semantic compression on command outputs.
   - Ultra-compact 4-line ANSI color telemetry footer (`xp-tokens --turn`).

---

## Supported Hosts & Architecture

The kit provides native adapters for all major agentic AI environments:

| Host | Supported Formats | Generated Configuration Files |
|------|-------------------|--------------------------------|
| **Antigravity** | IDE & CLI (`agy`) | `~/.gemini/config/AGENTS.md`, `hooks.json`, symlinked skills/agents |
| **OpenCode** | IDE & CLI (`opencode`) | `opencode.json`, `.opencode/agent/*.md`, `.opencode/command/*.md` |
| **Cursor** | IDE & CLI (`cursor`) | `.cursor/rules/*.mdc`, `.cursor/mcp.json`, `.cursorignore` |
| **Codex** | CLI (`codex`) | `.codex/rules/xp-governance.md`, `.codex/mcp.json`, `.codexignore` |
| **Qoder** | IDE & CLI (`qoder`) | `.qoder/rules/xp-governance.md`, `.qoder/mcp.json`, `.qoderignore` |

---

## Installation & Setup Guide

### 1. One-Liner Quick Install (Remote — Compatible with Bash, Zsh, Fish, and POSIX shells)

```sh
# Short URL (anti-line-wrap) — automatic global installation across all 5 hosts:
curl -sL https://cdn.jsdelivr.net/gh/Andrevictor20/xp-multiagent-kit/i | sh

# Direct GitHub Raw alternative:
curl -fsSL https://raw.githubusercontent.com/Andrevictor20/xp-multiagent-kit/main/install.sh | sh

# Pass custom flags explicitly via pipe:
curl -fsSL https://raw.githubusercontent.com/Andrevictor20/xp-multiagent-kit/main/install.sh | sh -s -- --global --target all --yes
```

### 2. Local Installation (Clone & Run)

```bash
git clone https://github.com/Andrevictor20/xp-multiagent-kit.git
cd xp-multiagent-kit
./install.sh
```

The installer detects your operating system language (`$LANG`, `$LC_MESSAGES`) and launches an interactive bilingual wizard (English / Portuguese).

### 3. Native Windows Installation (PowerShell & CMD)

On Windows 10/11, run natively using PowerShell or Command Prompt (CMD):

```powershell
# Interactive bilingual wizard via PowerShell:
.\install.ps1

# Non-interactive global installation for all hosts (PowerShell):
.\install.ps1 -Scope global -Target all -Yes

# Inject into a project repository with copy fallback:
.\install.ps1 -ProjectDir "C:\path\to\my-project" -Target cursor,codex -Yes

# From Command Prompt (CMD) or double-click in Explorer:
install.cmd --global --target all --yes
```

> **Windows CLI Shims & User PATH**: The Windows installer automatically generates `.cmd` shims (`xp-tokens.cmd`, `xp-spec.cmd`, `xp-kit.cmd`, `xp-run.cmd`, etc.) in `%USERPROFILE%\.local\bin` and configures your User Environment `PATH` persistently in the Windows Registry.

### 4. Non-Interactive Automation & Flags (Linux & macOS)

For Linux and macOS scripts or CI/CD pipelines:

```bash
# Global installation for ALL supported hosts (Antigravity, OpenCode, Cursor, Codex, Qoder):
./install.sh --global --target all --yes

# Install only into specific hosts:
./install.sh --global --target cursor,codex,opencode --yes

# Inject the kit into a single project workspace:
./install.sh --project /path/to/my-repo --target all --yes

# Both: update global environment AND inject into a target project:
./install.sh --both /path/to/my-repo --target cursor,qoder --yes

# Specify language explicitly (en or pt):
./install.sh --global --target all --lang en --yes

# Safe preview with dry-run mode:
./install.sh --dry-run
```

### 5. Bundled Toolchain

The installation process automatically installs and links auxiliary performance tools:
- **RTK (Rust Token Killer)**: Compiles from source or downloads binary to `~/.local/bin/rtk`.
- **OpenDesign (`od`)**: Installs daemon and links visual CLI to `~/.local/bin/od`.
- **CodeReviewGraph (`code-review-graph` / `crg`)**: Sets up isolated virtual environment in `~/.local/share/code-review-graph`.

---

## Autonomous Updates & Notifications

The kit includes a non-blocking update manager that checks for remote updates:

```bash
# Check for updates and automatically upgrade the kit:
xp-kit update

# Run diagnostic health check on the environment:
xp-kit doctor

# Synchronize global configuration across all hosts:
xp-kit sync
```

- **24-Hour Non-Blocking Cache**: Remote updates are checked asynchronously in `~/.xp_kit_update_cache.json` without slowing down CLI turns.
- **Discrete Notifications**: When a new version is published, `xp-tokens` and `xp-kit` print a discrete notification:
  ```text
  ✨ An update is available: v3.1.0 -> v3.2.0 (Run 'xp-kit update' to upgrade)
  ```

---

## Unified CLI Reference

All CLI tools are available under both `xp-*` (agnostic) and `agy-*` (Antigravity-native) aliases in `~/.local/bin`:

### Governance & Spec Tools
- `xp-kit` / `agy-kit`: Multi-host manager, installation wizard, doctor diagnostics, and auto-updater.
- `xp-spec` / `agy-spec`: ATDD specification scaffolding and validator:
  ```bash
  # Scaffold a new ATDD spec:
  xp-spec new user-authentication

  # Validate spec structure (ACs, SbE table, Gherkin scenarios):
  xp-spec validate .agents/specs/SPEC-004-user-authentication.md
  ```
- `xp-conformance` / `agy-conformance`: Generates the traceability matrix linking Acceptance Criteria to test executions.

### Token Telemetry & Execution
- `xp-tokens` / `agy-tokens`: Compact 4-line telemetry engine with color support and host-adaptive model catalog:
  ```bash
  # Print current turn footer with terminal colors:
  xp-tokens --turn --color

  # Target specific host model limit:
  xp-tokens --turn --color --host cursor
  ```
- `xp-run` / `agy-run`: Executes commands with output sanitization, preserving exit codes via `pipefail`.
- `xp-evidence` / `agy-evidence`: Records concrete test execution evidence for compliance audits.
- `xp-handoff` / `agy-handoff`: Creates structured handoff packets between agents or sessions.

### Design & Architecture Tools
- `xp-design` / `agy-design` / `od`: OpenDesign visual canvas and UI token management.
- `xp-graph` / `agy-graph` / `code-review-graph`: AST dependency analysis and blast-radius exploration.
- `agy-smart` / `agy-effort`: Dynamic reasoning effort router (`low`, `medium`, `high`).
- `agy-ci-heal`: Autonomous CI/CD pipeline diagnosis and auto-repair.

---

## Telemetry Footer Specification

Every response produced by an agent governed by the kit ends with the mandatory compact 4-line footer:

```text
Contexto: [▰▰▱▱▱▱▱▱▱▱] 11.2% (22.4k / 200.0k)  
Limites:  5h [▰▰▰▰▰▱▱▱] 52.1% usado • Semana [▰▰▱▱▱▱▱▱] **81.6% livre**  
Consumo:  1.6k tok (In: 1.2k | Tool: 0 | Out: 450)  
Modelo:   Claude 3.7 Sonnet (Host: Cursor) • Janela: 200.0k • Saída: 64.0k
```

---

## Directory Layout

```text
.agents/
├── agents/                 # Specialized agent definitions (orchestrator, navigator, builder, etc.)
├── memory/                 # 4-Tier living project memory and historical archives
│   ├── PROJECT_MEMORY.md   # Active context snapshot (< 2,000 tokens)
│   ├── REPO_MAP.md         # AST symbol tree for zero-blind exploration
│   └── archive/HISTORY.md  # Rotated deliverable history
├── policies/               # Non-negotiable policies (ATDD/TDD, Anti-Test-Bypass, Memory, Security)
├── rules/                  # Active runtime rule enforcement
├── skills/                 # 77 granular skills (token-dense English instruction sets)
├── templates/              # Reusable templates (SPEC-NNN-ATDD.md, PROJECT_MEMORY_TEMPLATE.md)
└── workflows/              # Structured workflow routes by risk level (L0 to L3, bugfix, migration)

scripts/
├── host_adapters.py        # Multi-host project configuration generator
├── kit_installer.py        # Interactive & automated CLI installer
├── mcp_installers.py       # RTK, OpenDesign, and CodeReviewGraph automated toolchain installers
├── spec_tool.py            # xp-spec CLI tool for ATDD spec scaffolding and validation
├── telemetry/              # Multi-host token tracking, model catalogs, and color formatting
└── update_manager.py       # Autonomous remote update checker and updater
```

---

## Contributing & Verification

To verify the test suite across all modules:

```bash
# Run unit tests across all kit components:
python3 -m unittest discover tests

# Run specific enhancement test suites:
python3 -m unittest tests/test_spec_003_enhancements.py tests/test_spec_003_v3.py
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.\n