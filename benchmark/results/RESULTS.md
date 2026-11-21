# Benchmark: uso com e sem o XP Multi-Agent Kit v4

Relatório gerado por `benchmark/aggregate.py`. Dados brutos em
`benchmark/results/raw.jsonl` e `benchmark/results/overhead.json`.

## 1. Veredito em uma tabela

| KPI | Sem kit | Com kit | Δ |
|---|---:|---:|---:|
| Defeitos reais capturados (de 10) | 1 | 10 | **+9** |
| Recall de defeitos | 10.0% | 100.0% | +90.0 p.p. |
| Falsos positivos em 6 mudanças legítimas | 0 | 0 | 0 |
| Tokens de contexto por tarefa (proxy) | 508 | 2610 | 414% |
| Tempo médio por tarefa | 0.402 s | 1.369 s | 241% |
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
| `AGENTS.md` | 2950 | 738 |
| `PROJECT_MEMORY.md` | 2654 | 664 |
| `.agents/policies/INDEX.md` (índice JIT) | 586 | 146 |
| **Total fixo por turno** | **6190** | **~1548** |
| 7 políticas inteiras (JIT, sob gatilho) | 9236 | 2309 |

O índice compacto substitui a injeção integral das 7 políticas. O ganho por turno é
de 9236 B para 586 B (~94% de redução).

## 4. Custo de execução

| Medida | Valor |
|---|---:|
| Hook por chamada de ferramenta (mediana) | 78.0 ms |
| Hook p95 | 104.8 ms |
| Overhead projetado em 50 chamadas | 3900 ms |
| Gate `check` (caminho PASS) | 0.26 s |
| Suíte `unittest` do projeto | 0.102 s |
| Comandos benignos permitidos pelo hook | 40/40 |
| Comandos perigosos bloqueados pelo hook | 8/8 |

## 5. Recuperação de contexto JIT

- Corpus de governança disponível: **15426 B**
- Mediana devolvida por `xp context <query>`: **1537 B**
- Redução de contexto: **90.0%**
- Latência mediana: **106 ms**
- Consultas testadas: `policy approval destructive command`, `tdd red green evidence`, `token budget base context`, `god file 500 lines`, `dead ends failed attempts`, `zero downtime rollback`

## 6. Ganhos e perdas

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
1. **Custo fixo de contexto**: +1548 tokens por turno (com o índice JIT já ativo).
   Antes da otimização era +3710 tokens.
2. **Latência de hook**: 78.0 ms por chamada de ferramenta (~3.9 s em 50 chamadas).
3. **Cerimônia**: 4.1 comandos por tarefa contra 2.0; 2 passos humanos no total (revisão/aprovação).
4. **Lacuna — testes desativados**: o passo 4 do gate agora detecta `@unittest.skip`/`skipTest`/`pytest.mark.skip` (D07).
5. **Lacuna — segredos hardcoded**: o passo 4 do gate agora detecta `sk_live_*`, `AKIA…`, `ghp_…` e `api_key='…'` (D08).
6. **Melhoria aplicada**: a regra de supressão de tipo cobre `as any`, `@ts-ignore`, `@ts-expect-error`, `# type: ignore` e `# noqa`.

## 7. O que mudou nesta iteração

1. `goldfish_review.audit_code_completeness` detecta skip, segredos e `# type: ignore`.
2. `scripts/policy_index.py` gera `.agents/policies/INDEX.md` (586 B) que substitui a injeção
   integral das 7 políticas (9.2 KB) — **redução de ~94% no custo fixo de contexto**.
3. `xp kit eval compare` agora reporta `defect_escape_rate` (recalculado em todos os cenários).
4. `AGENTS.md` atualizado com as novas regras mecânicas do passo 4.

## 7. Ameaças à validade

- **Sem LLM no loop**: tokens são um proxy (`bytes/4`), não telemetria de provedor.
  O benchmark mede o *arnês* (gates, hooks, contexto), não a inteligência do agente.
- **Substrato sintético**: 24 testes, 3 módulos. Repositórios grandes têm custo de gate maior.
- **Linha de base**: sem kit = `compileall` + `unittest`, pois não há `ruff`/`mypy`/`pytest`
  instalados. Uma equipe com SAST/linters teria linha de base mais forte.
- **Autor do benchmark = autor do kit**: mitigado por oráculos independentes do gate,
  cenários com lacunas esperadas e FPR medido em mudanças legítimas.
- **Uma execução por cenário**: determinístico, mas sem intervalo de confiança estatístico.

## 8. Recomendações

1. **Implementado nesta iteração**: `defect_escape_rate` no `xp kit eval`; detecção mecânica de
   skip/segredos/`# type: ignore` no passo 4; índice JIT de políticas substituindo injeção integral.
2. **Carregar o índice JIT por gatilho** (não só por consulta explícita): injetar automaticamente
   quando o diff tocar `auth/`, `migrations/`, `tests/` — reduz o custo de consulta JIT de ~100 ms por query.
3. **Cachear o hook** como processo residente: 74 ms por chamada é aceitável, mas 5× melhorável.
4. **Medir em repositórios reais**: adicionar um benchmark de regressão em um repo grande (≥10k linhas,
   ≥200 testes) para validar o custo do gate e do EGM multipass em escala.
5. **Adotar `defect_escape_rate` como métrica canônica de regressão**: o kit agora reporta
   `defects_escaped / defects_observed` em cada `xp kit eval compare`.

## 9. Como reproduzir

```bash
python3 scripts/policy_index.py generate   # atualiza .agents/policies/INDEX.md
python3 benchmark/runner.py              # 16 cenários pareados -> results/raw.jsonl
python3 benchmark/overhead.py          # custo mecânico -> results/overhead.json
python3 benchmark/aggregate.py        # KPIs + eval JSONL + RESULTS.md
python3 scripts/xp kit eval compare benchmark/results/baseline.jsonl benchmark/results/kit.jsonl
```
