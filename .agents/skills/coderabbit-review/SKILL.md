---
name: coderabbit-review
version: 1.0.0
description: External AI diff review and security audit using CodeRabbit CLI with graceful fallback.
author: André Victor
license: MIT
tags: [code-review, coderabbit, static-analysis, diff-audit, security]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode, antigravity]
entrypoint: SKILL.md
---

# CodeRabbit Review (External Diff & Security Audit)

Audits local diffs and code security using CodeRabbit CLI as an optional external verification. Operates in a 100% non-blocking manner: if the CLI is not installed or authenticated, it applies automatic fallback to internal EGM Pass 2 and local tooling.

## 1. Core Principle: Non-Blocking & Zero Hard-Dependency

- **Never block the pipeline due to missing CodeRabbit:** The XP Kit is self-contained and operates offline with `code-review-graph`, local linters, and the 3-step EGM model (`xp-goldfish`).
- **Optional/Additive Usage:** CodeRabbit acts as an external second opinion specializing in diffs, regression bugs, and code security.
- If the CLI is unavailable or unauthenticated, emit `[CODERABBIT_SKIPPED]` and proceed normally without failing the gate.

## 2. Environment Verification Protocol

Before executing any review command:

1. **Check Binary Presence:**
   ```bash
   command -v coderabbit >/dev/null 2>&1
   ```
2. **Check Authentication:**
   ```bash
   coderabbit auth status 2>/dev/null || coderabbit --version >/dev/null 2>&1
   ```
3. **Decision:**
   - **Available and Authenticated:** Proceed to Step 3.
   - **Unavailable / Unauthenticated:** Log status and proceed with native governance:
     ```text
     ℹ️ [CODERABBIT_SKIPPED]: CodeRabbit CLI not installed or not authenticated.
     Proceeding with local linters, AST graph (code-review-graph), and native EGM Pass 2.
     ```

## 3. Local Execution Commands (`--agent`)

Always use the `--agent` flag for structured NDJSON output tailored for AI agents:

### 3.A Review Uncommitted Modifications (Inner Loop)
```bash
coderabbit review --agent --uncommitted
```

### 3.B Review Changes Against Base Branch (Pre-PR / Conformance)
```bash
coderabbit review --agent --base main
```

### 3.C Review Specific Directory
```bash
coderabbit review --agent --dir <module_path>
```

## 4. Severity Handling and Remediation

When processing NDJSON output:
- `critical` and `major`: Must be addressed mandatorily. If they represent genuine defects (vulnerabilities, race conditions, leaks, contract breaches), they must be fixed before approval by `refactor-warden` or `release-gatekeeper`.
- `minor`, `trivial`, `info`: Evaluated against kit directives (`No God Files < 500 lines`, `No Workarounds`, slop removal).
- **No false positives:** If a CodeRabbit finding conflicts with an explicit XP Kit rule or approved specification, the kit specification takes precedence.

## 5. Integration with Kit Subagents

- **`refactor-warden` (EGM Pass 2):** Triggers `coderabbit review --agent --uncommitted` after code reaches GREEN status to detect static complexity, duplications, and additional code smells.
- **`release-gatekeeper` (Conformance Gate):** Validates that no open critical issues flagged by CodeRabbit remain before issuing the `PASS` seal.
