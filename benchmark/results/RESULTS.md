# Benchmark: uso com e sem o XP Multi-Agent Kit v4

Relatório gerado por `benchmark/aggregate.py`. Dados brutos em
`benchmark/results/raw.jsonl` e `benchmark/results/overhead.json`.

## 1. Veredito em uma tabela

| KPI | Sem kit | Com kit | Δ |
|---|---:|---:|---:|
| Defeitos reais capturados (de 10) | 1 | 10 | **+9** |
| Recall de defeitos | 10.0% | 100.0% | +90.0 p.p. |
| Falsos positivos em 6 mudanças legítimas | 0 | 0 | 0 |
| Tokens de contexto por tarefa (proxy) | 508 | 2568 | 406% |
| Tempo médio por tarefa | 0.174 s | 0.67 s | 285% |
| Comandos por tarefa | 2.0 | 4.1 | — |
| Passos humanos por tarefa | 0.0 | 0.12 | — |

## 2. Matriz por cenário

| Cenário | Tipo | Defeito (oráculo) | Sem kit | Com kit | Passo do gate |
|---|---|---|---|---|---|
| `D01_todo_stub` | defect | sim | pass | blocked | 4 |
| `D02_god_file` | defect | sim | pass | blocked | 4 |
| `D03_test_deleted` | defect | sim | pass | blocked | 3 |
| `D04_ac_untraced` | defect | sim | pass | blocked | 9 |
| `D05_regression_shipped` | defect | sim | blocked | blocked | 7 |
| `D06_out_of_scope` | defect | sim | pass | blocked | 2 |
| `D07_skip_bypass` | defect | sim | pass | blocked | 4 |
| `D08_hardcoded_secret` | defect | sim | pass | blocked | 4 |
| `D09_no_red_evidence` | defect | sim | pass | blocked | 7 |
| `D10_review_tier_bypass` | defect | sim | pass | blocked | 10 |
| `B01_docs_typo` | benign | não | pass | pass | — |
| `B02_small_feature` | benign | não | pass | pass | — |
| `B03_bugfix_red_green` | benign | não | pass | pass | — |
| `B04_refactor` | benign | não | pass | pass | — |
| `B05_auth_review_ok` | benign | não | pass | pass | — |
| `B06_migration_human_ok` | benign | não | pass | pass | — |

## 3. Custo fixo do kit (contexto base pago em cada turno)

| Item | Bytes | Tokens (B/4) |
|---|---:|---:|
| `AGENTS.md` | 2378 | 594 |
| `PROJECT_MEMORY.md` | 2627 | 657 |
| `.agents/policies/INDEX.md` (índice JIT) | 1053 | 263 |
| **Total fixo por turno** | **6058** | **~1514** |
| 7 políticas inteiras (JIT, sob gatilho) | 9254 | 2314 |

O índice compacto substitui a injeção integral das 7 políticas. O ganho por turno é
de 9254 B para 1053 B (~89% de redução).

## 4. Custo de execução

| Medida | Valor |
|---|---:|
| Hook por chamada de ferramenta (mediana) | 67.7 ms |
| Hook p95 | 74.3 ms |
| Overhead projetado em 50 chamadas | 3383 ms |
| Gate `check` (caminho PASS) | 0.225 s |
| Suíte `unittest` do projeto | 0.093 s |
| Comandos benignos permitidos pelo hook | 40/40 |
| Comandos perigosos bloqueados pelo hook | 8/8 |

## 5. Recuperação de contexto JIT

- Corpus de governança disponível: **15312 B**
- Mediana devolvida por `xp context <query>`: **1606 B**
- Redução de contexto: **89.5%**
- Latência mediana: **94 ms**
- Consultas testadas: `policy approval destructive command`, `tdd red green evidence`, `token budget base context`, `god file 500 lines`, `dead ends failed attempts`, `zero downtime rollback`

## 6. Otimizadores de Token (Lean v4)

| Mecanismo | Medida antes | Medida com kit | Redução / Efeito |
|---|---:|---:|---:|
| `context_compactor` (CI/diff/git/logs) | 13379 B | 5101 B | **61.9%** |
| `repo_map` (AST vs árvore completa) | 6981 B | 1164 B | **83.3%** |
| `smart_tool_optimizer` (rewrites/anti-loop/releitura) | — | 3 rewrites | reread=True, loop=True |

## 7. Ganhos e perdas

### Ganhos medidos
1. **Contenção de entrega incompleta**: `TODO`/stub e God-file (>499 linhas) bloqueados no passo 4.
2. **Anti-bypass de teste**: remoção de teste congelado bloqueada no passo 3.
3. **Rastreabilidade de AC**: AC declarado sem teste bloqueado no passo 9.
4. **Contenção de escopo**: diff fora do `scope_files` bloqueado no passo 2.
5. **Disciplina RED→GREEN**: ship sem evidência RED bloqueado no passo 7.
6. **Tier de risco**: alteração em `auth/` sem revisão e em `migrations/` sem aprovação bloqueadas no passo 10.
7. **Guarda de comando**: 8/8 comandos destrutivos negados, 40/40 benignos liberados.
8. **JIT**: ~90% menos contexto do que ler o corpus de governança inteiro.

### Perdas e lacunas medidas
1. **Custo fixo de contexto**: +1514 tokens por turno (com o índice JIT já ativo).
   Antes da otimização era +3565 tokens.
2. **Latência de hook**: 67.7 ms por chamada de ferramenta (~3.4 s em 50 chamadas).
3. **Cerimônia**: 4.1 comandos por tarefa contra 2.0; 2 passos humanos no total (revisão/aprovação).
4. **Lacuna — testes desativados**: o passo 4 do gate agora detecta `@unittest.skip`/`skipTest`/`pytest.mark.skip` (D07).
5. **Lacuna — segredos hardcoded**: o passo 4 do gate agora detecta `sk_live_*`, `AKIA…`, `ghp_…` e `api_key='…'` (D08).
6. **Melhoria aplicada**: a regra de supressão de tipo cobre `as any`, `@ts-ignore`, `@ts-expect-error`, `# type: ignore` e `# noqa`.

## 8. O que mudou nesta iteração

1. `goldfish_review.audit_code_completeness` detecta skip, segredos e `# type: ignore`.
2. `scripts/policy_index.py` gera `.agents/policies/INDEX.md` que substitui a injeção
   integral das 7 políticas (9254 B → 1053 B, **−89%**).
3. `xp kit eval compare` agora reporta `defect_escape_rate` (recalculado em todos os cenários).
4. `AGENTS.md`, `xp_contract.py`, `xp_gate.py`, `tool-size-guard.py` e `dynamic_effort_hook.py` otimizados para eliminar retrabalho e preservar KV-cache em L0/L1.

## 9. Ameaças à validade

- **Trilha determinística sem LLM:** tokens são proxy (`bytes/4`); consulte `LLM_RESULTS.md` para telemetria real de provedor.
- **Substrato sintético:** 24 testes, 3 módulos. Repositórios grandes têm custo de gate maior.
- **Linha de base:** sem kit = `compileall` + `unittest`, pois não há `ruff`/`mypy`/`pytest` instalados.
- **Autor do benchmark = autor do kit:** mitigado por oráculos independentes do gate e FPR medido em mudanças legítimas.
- **Uma execução por cenário:** determinístico; para ICs estatísticos, use `--runs N` no `llm_runner.py`.

## 10. Recomendações

1. **Implementado:** `defect_escape_rate` no `xp kit eval`; detecção mecânica de skip/segredos/`# type: ignore`; índice JIT de políticas; remoção de `ephemeralMessage` em L0/L1 (KV-cache).
2. **Carregar o índice JIT por gatilho** quando o diff tocar `auth/`, `migrations/`, `tests/`.
3. **Medir em repositórios reais (≥10k linhas, ≥200 testes)** para validar o custo do gate e do EGM multipass em escala.

## 11. Como reproduzir

```bash
python3 scripts/policy_index.py generate   # atualiza .agents/policies/INDEX.md
python3 benchmark/runner.py              # 16 cenários pareados -> results/raw.jsonl
python3 benchmark/overhead.py          # custo mecânico + otimizadores -> results/overhead.json
python3 benchmark/aggregate.py           # KPIs + eval JSONL + RESULTS.md + polyglot
python3 benchmark/llm_runner.py --runner agy --runs 1 && python3 benchmark/llm_aggregate.py
python3 scripts/xp kit eval compare benchmark/results/baseline.jsonl benchmark/results/kit.jsonl
```

## 12. Export para benchmark off-the-shelf

`benchmark/polyglot_adapter.py` exporta os 16 cenários no formato Aider
Polyglot (`polyglot_tasks.jsonl`) e SWE-bench (`polyglot_predictions.jsonl`).
Assim, o resultado do kit pode ser publicado em leaderboards de agente de código
sem reescrever a metodologia. O `score` por arm mostra recall/FPR/tokens/tempo
no mesmo contrato de dados.
