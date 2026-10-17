---
name: incident
description: "Production incident response: immediate mitigation, rollback, and blameless post-mortem."
---
# Incident Response Workflow

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → Triage severity & blast radius → `shipper` executes immediate rollback or feature-flag kill switch → verify RED metrics recovery (Rate, Errors, Duration) → isolate root cause & add RED regression test → record `[L-NNN]` post-mortem in `.agents/memory/PROJECT_MEMORY.md`.
