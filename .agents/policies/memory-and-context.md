# Memory & Context Policy

## 1. 4-Tier Continuous Memory
1. **Working Memory:** Current task goals, active files, and pending validations.
2. **Episodic Memory:** Sliding window of recent commits, deliveries, and execution summaries.
3. **Semantic Memory:** Project architectural patterns, domain glossary, and ADRs.
4. **Procedural Memory:** Actionable lessons learned (`[L-NNN]`) with forbidden patterns (`never` list) and policies.

## 2. Context Optimization & JIT Retrieval
1. **Base Context Budget:** Keep base governance lean (total fixed base context ≤ 8000 bytes; `AGENTS.md` ≤ 3000 bytes, `PROJECT_MEMORY.md` ≤ 3000 bytes).
2. **JIT Context Retrieval (`xp context`):** Retrieve surgical knowledge snippets via search instead of dumping full files into context.
3. **Prompt Cache Boundary:** Keep static system rules in the prompt prefix and dynamic memory/context in the suffix to preserve prompt cache hits.
4. **Physical Memory Gate:** Every completed task must update `.agents/memory/PROJECT_MEMORY.md` on disk before final response. Rotate older entries via `memory_archiver`.
