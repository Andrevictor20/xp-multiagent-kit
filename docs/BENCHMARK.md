# Benchmark de Eficiência — XP Multi-Agent Kit v4 vs v3.9

Guia de execução das 4 tarefas de referência para medição empírica de tokens e gates.

## 1. Tarefas de Referência (`tests/evals/tasks.jsonl`)
- `task_l0_typo`: Documentação/typo (L0, chore).
- `task_l1_bugfix`: Regressão com teste unitário RED (L1, fix).
- `task_l2_feature`: Especificação + SbE + implementação TDD (L2, feature).
- `task_l3_auth`: Validação de tokens com STRIDE e mitigação (L3, migration).

## 2. Como Rodar o Benchmark
Execute as tarefas no baseline (`v3.9.2-baseline`) e na versão atual (`v4.0.0`):

```bash
# 1. Executar bateria no baseline (gere baseline.jsonl com os resultados)
git checkout v3.9.2-baseline
# Execute as 4 tarefas e grave os recibos em /tmp/eval_v39.jsonl

# 2. Executar bateria no v4.0.0 Thin Harness (gere target.jsonl)
git checkout refactor/thin-harness
# Execute as 4 tarefas com o Thin Harness e grave em /tmp/eval_v40.jsonl

# 3. Comparar métricas canônicas
xp kit eval compare /tmp/eval_v39.jsonl /tmp/eval_v40.jsonl
```

## 3. Métricas Avaliadas
- **Principal:** Tokens totais / Tarefas com gate PASS (custo por tarefa aceita).
- **Secundárias:** Taxa PASS no 1º Gate, Falhas Repetidas (`signature` ≥ 2), Intervenções Humanas, Sessões L1+ sem Veredito, Turnos Médios e Tempo Total (s).
