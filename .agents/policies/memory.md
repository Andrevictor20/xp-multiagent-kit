# 4-Tier Continuous Project Memory Policy

1. **Step 0 Mandatory Read:** Read `.agents/memory/PROJECT_MEMORY.md` (< 8 KB) at the start of every session.
2. **4 Memory Tiers:** Working (Section 4 backlog), Episodic (Section 3 sliding window of 5-10 recent deliveries), Semantic (Section 1 summary & `details/` ADRs), Procedural (`details/` `[L-NNN]` lessons).
3. **Hard-Enforcement Gate:** Every completed task MUST physically update `.agents/memory/PROJECT_MEMORY.md` on disk before the final response. Rotate overflow via `agy-memory-archive`.
