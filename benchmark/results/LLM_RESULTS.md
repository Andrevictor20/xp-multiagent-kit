# Benchmark A/B com LLM Real: Sem Kit vs Com XP Multi-Agent Kit v4

- **Runner CLI:** `agy` | **Modelo:** `gemini-3.8-flash-low` | **Execuções por braço:** 6

## 1. Resumo Executivo (Ganhos Reais & Consumo Real de Tokens)

| Métrica | Sem Kit (`baseline`) | Com Kit (`kit`) | Δ |
|---|---:|---:|---:|
| Tarefas 100% resolvidas (testes ocultos + oráculos) | 6/6 (100.0%) | 6/6 (100.0%) | +0.0 p.p. |
| Escape de defeito / violação pós-entrega | 0 (0.0%) | 0 (0.0%) | +0.0 p.p. |
| **Tokens totais consumidos** | 177059 | 170642 | -3.6% |
| Média de tokens / tarefa | 29510 | 28440 | -3.6% |
| **Tokens / tarefa resolvida (KPI)** | 29510 | 28440 | -3.6% |
| Input tokens | 169322 | 162666 | -3.9% |
| Output tokens | 7737 | 7976 | +3.1% |
| Cache read tokens | 455759 | 392413 | -13.9% |
| Turnos médios / tarefa | 1.0 | 1.0 | +0.0% |
| Duração média / tarefa (s) | 29.89 s | 29.2 s | -2.3% |
| Custo USD reportado | $0.0000 | $0.0000 | — |
| Gate `xp gate check` PASS (braço kit) | — | 5/6 | — |
| Evidência RED→GREEN registrada (braço kit) | — | 5/6 | — |

## 2. Comparação Pareada por Tarefa

| Tarefa | Risco | Sem Kit (OK / Tokens / Turnos) | Com Kit (OK / Tokens / Turnos) | Δ Tokens | Oráculos violados |
|---|---|---|---|---:|---|
| `T01_l0_docs_typo` | L0 | PASS / 20033 / 1t | PASS / 20015 / 1t | -0.1% | base:none | kit:none |
| `T02_l1_bugfix_tdd` | L1 | PASS / 27015 / 1t | PASS / 23050 / 1t | -14.7% | base:none | kit:none |
| `T03_l1_feature_discount` | L1 | PASS / 33474 / 1t | PASS / 22723 / 1t | -32.1% | base:none | kit:none |
| `T04_l2_feature_acs` | L2 | PASS / 31886 / 1t | PASS / 25756 / 1t | -19.2% | base:none | kit:none |
| `T05_l2_refactor_scope` | L2 | PASS / 30581 / 1t | PASS / 34547 / 1t | +13.0% | base:none | kit:none |
| `T06_l3_auth_security` | L3 | PASS / 34070 / 1t | PASS / 44551 / 1t | +30.8% | base:none | kit:none |
