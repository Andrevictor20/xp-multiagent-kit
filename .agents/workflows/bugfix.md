---
name: bugfix
description: "Root-cause bugfix workflow using 4-phase systematic debugging and regression TDD."
---
# Bugfix Workflow

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → Reproduce & isolate root cause (`systematic-debugging`) → `test-guardian`/`builder` writes failing regression test reproducing the exact bug (RED) → `builder` fixes root cause without workarounds (GREEN) → capture `[L-NNN]` lesson in `lesson-learned` if structural → `archivist` updates `.agents/memory/PROJECT_MEMORY.md`.

## Rules
- Never patch symptoms or silence errors. Always reply to the user in Portuguese.
