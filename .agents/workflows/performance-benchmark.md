---
name: performance-benchmark
description: "Workflow de otimização de performance baseada em profiling, medição de linha de base (baseline) e verificação de SLOs."
---
# Performance & Profiling Benchmark Workflow

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `navigator` (Definição de Métricas-Alvo, SLOs e P95/P99) → `test-guardian` (Execução do Benchmark Baseline e Teste de Carga RED - falha por SLA) → `builder` (Otimização Cirúrgica de Hotspots e Estruturas de Dados GREEN) → `refactor-warden` (Code Deslop & Memory Leak Audit) → `release-gatekeeper` (Auditoria de Não-Regressão de Performance) → **Passo Final OBRIGATÓRIO: Persistência em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`**

## Guidelines
- **Zero Otimização Prematura:** Toda otimização DEVE ser precedida por evidência concreta de profiling (Flamegraph, CPU/Memory profile, logs de consultas lentas `EXPLAIN ANALYZE`).
- **Métricas Concretas:** Defina previamente o objetivo numérico mensurável (ex: *Reduzir latência P99 de 420ms para < 80ms* ou *Diminuir consumo de RAM de 1.2GB para < 400MB*).
- **Sem Degradação de Legibilidade:** Otimizações que tornam o código ilegível são proibidas a menos que sejam estritamente exigidas por gargalos críticos de CPU/GPU documentados.
