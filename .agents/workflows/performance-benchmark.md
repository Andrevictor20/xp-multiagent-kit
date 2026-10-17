---
name: performance-benchmark
description: "Performance profiling, load testing, and bottleneck elimination workflow."
---
# Performance Benchmark Workflow

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → Measure baseline metrics (p50/p95/p99 latency, throughput, memory/CPU) → identify hot path via profiler/AST → implement targeted optimization → re-run benchmark and prove quantitative gain → `archivist` records before/after metrics in `.agents/memory/PROJECT_MEMORY.md`.
