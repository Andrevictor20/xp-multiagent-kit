---
name: migration
description: "Zero-downtime database and schema migration workflow using Expand-and-Contract."
---
# Migration Workflow

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `navigator` + `sentinel` design Expand-and-Contract plan → **⏸️ Stop Gate** → Phase 1: Expand (additive schema, dual-write, backward compatible) → Phase 2: Backfill & Verify → Phase 3: Contract (remove legacy columns only after full rollout) → `archivist` updates `.agents/memory/PROJECT_MEMORY.md`.
