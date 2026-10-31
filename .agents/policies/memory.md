# 4-Tier Continuous Project Memory & JIT Context Policy

1. **Step 0 Mandatory Context:** Read `.agents/memory/PROJECT_MEMORY.md` (< 8 KB) at the start of sessions or query `xp-context` / `agy-context` (< 300 tokens) for active task focus.
2. **4 Memory Tiers:** Working (Section 4 backlog), Episodic (Section 3 sliding window of 5-10 recent deliveries), Semantic (Section 1 summary, domain models & `details/` ADRs), Procedural (`details/` `[L-NNN]` lessons & `policies/`).
3. **JIT Context Retrieval (`xp-context`):** Query `xp-context <query> [--files ...]` to fetch surgical snippets instead of reading entire markdown files into context.
4. **Prompt Cache Boundary:** Keep static governance rules in the prompt prefix; place dynamic memory and JIT context in the suffix to preserve 80-90% prompt cache discounts across all providers.
5. **Hard-Enforcement Gate:** Every completed task MUST physically update `.agents/memory/PROJECT_MEMORY.md` on disk before the final response. Rotate overflow via `agy-memory-archive`.
