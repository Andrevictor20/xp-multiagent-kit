# Memory & Context Policy

## 1. 5-Tier Continuous Memory
1. **Working Memory:** Current task goals, active files, and pending validations.
2. **Episodic Memory:** Sliding window of recent commits, deliveries, and execution summaries.
3. **Semantic Memory:** Project architectural patterns, domain glossary, and ADRs.
4. **Procedural Memory:** Actionable lessons learned (`[L-NNN]`) with forbidden patterns (`never` list) and policies.
5. **Negative Memory (Dead-Ends):** Catalog of failed attempts, rejected approaches, and forbidden anti-patterns to prevent cyclic regressions.

## 2. Context Optimization & JIT Retrieval
1. **Base Context Budget:** Keep base governance lean (total fixed base context ≤ 8000 bytes; `AGENTS.md` ≤ 3000 bytes, `PROJECT_MEMORY.md` ≤ 3000 bytes).
2. **Step 0 Mandatory Inspection:** Always read `PROJECT_MEMORY.md` (specifically Section 5 Dead-Ends) before planning or modifying code.
3. **JIT Context Retrieval (`xp context`):** Retrieve surgical knowledge snippets via search instead of dumping full files into context.
4. **Prompt Cache Boundary:** Keep static system rules in the prompt prefix and dynamic memory/context in the suffix to preserve prompt cache hits.
5. **Physical Memory Gate:** Every completed task must update `.agents/memory/PROJECT_MEMORY.md` on disk before final response, recording progress, decisions, and any failed attempts. Rotate older entries via `memory_archiver`.
