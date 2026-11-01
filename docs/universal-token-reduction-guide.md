# 📘 Universal Token Reduction Guide — Antigravity (IDE & CLI)

This guide presents **operational best practices and tools** to maintain strict token consumption control in **Antigravity (IDE and CLI)**, in **any project or situation**, ensuring faster responses, lower latency, and quota preservation (5-hour and weekly windows).

---

## 🎯 The 5 Golden Rules of Token Economy

### 1. The 25 Turns / 50k Tokens Rule (Preventive Reset)
- **The Problem:** Antigravity retransmits the entire conversation history on every new turn. In chats exceeding 25 turns, a simple 2-line question can cost 80,000 tokens just in repeated history.
- **The Solution:** Upon reaching 20 to 25 turns or during long sessions, generate the transition package and start a fresh chat:
  ```bash
  agy-handoff --write-file
  ```
- **Outcome:** The new chat starts cleanly, loading only the ~25 lines of `SESSION_HANDOFF.md` (~300 tokens), saving **over 90% of tokens per message**.

---

### 2. Reasoning Modulation (Adaptive Thinking Tokens)
- **The Problem:** Advanced reasoning models generate between 3,000 and 8,000 internal thinking tokens even for trivial mechanical tasks (fixing CSS, renaming variables, creating commits).
- **The Solution:** In the CLI, select the corresponding effort profile:
  - `agy-fast "adjust button margin"`: Activates `--effort low` (saves ~80% of thinking tokens).
  - `agy "implement endpoint X"`: Standard balanced mode (`--effort medium`).
  - `agy-deep "analyze race condition"`: Reserves `--effort high` for deep reasoning.

---

### 3. Tool Anti-Flood Protocol (`agy-sanitize`)
- **The Problem:** Running commands like `npm test`, `pytest`, `docker build`, or `cargo build` dumps hundreds of log lines into the chat. Once in the history, these lines are billed on every subsequent turn.
- **The Solution:** Run commands via `agy-sanitize` or use pipes:
  ```bash
  # Direct wrapper:
  agy-sanitize pytest -v

  # Or via pipe:
  npm test | agy-sanitize
  cargo build | agy-sanitize
  ```
- **Outcome:** Preserves the first 10 lines and the last 20 lines (errors and diagnostics) while suppressing intermediate lines with a clear indicator, preserving 100% of the original command exit code.

---

### 4. Surgical Code Inspection vs Blind Chunking ($O(N^2)$)
- **The Problem:** Reading entire files consumes thousands of tokens, but blindly chunking into multiple sequential contiguous blocks (e.g. 1-40, then 41-80, then 81-120) creates quadratic history growth across intermediate sub-steps ($O(N^2)$), retransmitting previous tool outputs on each round-trip.
- **The Solution:**
  - Practice **Symbol-First Navigation**: consult the codebase map and locate the exact line of the symbol via targeted search.
  - When inspecting code, read the **entire file in one call** if it fits within the single-read threshold; only if it exceeds the limit should you target the exact symbol window. Reducing turns is worth more than shrinking each individual output.
  - The native `smart-tool-optimizer` hook enforces these thresholds (defined in `scripts/kit_constants.py`) and detects repeated contiguous reads, which are the hallmark of blind chunking.

---

### 5. Global Diet and Exclusion Templates (`.geminiignore`)
- **The Problem:** Leaving oversized rules in `~/.gemini/config/rules/` or forgetting to ignore `node_modules` / `.venv` causes the agent to index gigabytes of unnecessary code.
- **The Solution:**
  - Periodically audit global configurations:
    ```bash
    agy-audit
    ```
  - Copy the universal template to new projects:
    ```bash
    cp /path/to/kit/templates/universal.geminiignore .geminiignore
    ```

---

## 🛠️ Table of Available Global Tools

| Utility | Purpose | Usage |
| :--- | :--- | :--- |
| `agy-fast` | Runs CLI with reduced effort (thinking token savings) | `agy-fast "instruction"` |
| `agy-deep` | Runs CLI with maximum effort for critical problems | `agy-deep "complex instruction"` |
| `agy-sanitize` | Truncates terminal output and prevents log floods | `agy-sanitize <command>` or `<cmd> \| agy-sanitize` |
| `agy-handoff` | Generates ultra-compact summary (<30 lines) to reset chat | `agy-handoff --write-file` |
| `agy-audit` | Audits bloating in rules, MCPs, and global skills | `agy-audit` |

---

## 🚨 Atomic Surgical Mode (In Long or Complex Conversations)

When a complex task demands maximum focus:
1. **Avoid broad exploratory tasks:** Ask only for the strictly necessary modification.
2. **Execute a single RED -> GREEN cycle:** Do not initiate new epics or peripheral refactorings.
3. **Generate checkpoint immediately:** Save current state with `agy-handoff --write-file` to avoid leaving work half-done.
