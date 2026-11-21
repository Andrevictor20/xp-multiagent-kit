# Benchmark com e sem o XP Multi-Agent Kit v4

## 1. Pergunta que o benchmark responde

Medidas que o kit **ganha** contra um repositório sem kit, e **paga** para ganhar.
As duas perguntas são simétricas e aparecem no relatório final:

- **Ganho**: quantas falhas reais (defeito, risco de processo, lacuna de
  rastreabilidade) são *contidas* no caminho do gate/hook?
- **Perda**: quanto o desenvolvedor e o agente pagam em contexto fixo,
  latência por chamada de ferramenta, cerimônia e passos humanos para
  ter esse ganho?

## 2. Metodologia (fundamentada em pesquisa)

O desenho segue as convenções que surgiram dos estudos de benchmark de
agentes de código de 2026, e é documentada para ser reproduzível.

### 2.1 Referências consultadas

| Fonte | Método adotado neste benchmark |
|---|---|
| **Gloaguen et al., "Evaluating AGENTS.md"** (arXiv 2602.11988, ICLR 2026 workshop) | Contexto por repositório costuma *aumentar* custo (tokens +20%) e não necessariamente *taxa de sucesso*. Por isso medimos custo fixo de contexto separado de capacidade de detecção, e registramos explicitamente os 2 cenários onde a baseline já puxa o ganho (D05, D07) para não viés. |
| **SWE-bench / CodeScaleBench (Sourcegraph 2026)** | Comparação *pareada no mesmo commit* — cada cenário é executado em duas sandboxes idênticas (mesma linha-base `git commit`), com e sem kit. |
| **FeatureLoop (Oct 2026)** | Medir **FDAC** — "First-Do-Accurate-Complete" — ou seja, *não* só sucesso final, mas custo de correção. Por isso registramos tempo por tarefa, passos do gate e tokens de cerimônia, e não apenas o veredito. |
| **AWS "Tokenomics for coding agents" (2026)** | **Vary one lever at a time**. Aqui, a alavanca é *um único* mecanismo: a presença do kit. O modelo (subprocesses do Python) e o repositório (substrato) são fixos em ambos os braços. |
| **Cycode / Augment / SAST studies (2024–2026)** | **False-positive rate é a métrica de confiança**. Um gate que bloqueia todo mundo não é "seguro"; é inusável. Por isso medimos FPR sobre 6 mudanças legítimas e o FPR precisa ser < ~20% para o kit não gerar "alert fatigue". |
| **Ciclos de TDD com anti-bypass** (própria política do kit) | Os oráculos são *independentes* do kit — o `oracles.py` decide se o cenário é "deficitário" por regex/git/inspeção direta, nunca pelo veredito do gate. Isso evita circularidade ("o gate acha que bloqueou porque o oráculo perguntou ao gate"). |

### 2.2 Substrato controlado

`benchmark/substrate/` é um repositório Python de propósito realista:

- 3 módulos de domínio (`parser`, `pricing`, `service`)
- 24 testes `unittest` verdes no commit base
- Sem dependências externas
- `.gitignore` idêntico nos dois braços

Cada cenário é executado em **duas sandboxes** (uma com kit, uma sem)
a partir do *mesmo* commit base (`git init && git add -A && git commit`).
Os 32 cenários×braços usam arquivos independentes.

### 2.3 Cenários

| Cenário | Tipo | O que é plantado | Oráculo |
|---|---|---|---|
| D01 | Defeito | `# TODO` em implementação | Regex `TODO\|TBD\|FIXME\|HACK` |
| D02 | Defeito | Arquivo com 520 linhas | `len(lines) > 500` |
| D03 | Defeito | Teste congelado removido | Diferença SHA vs base |
| D04 | Risco de processo | AC-02 declarado, sem teste | Escaneamento de `AC-\d+` em `tests/` |
| D05 | Defeito | Teste de regressão falhando | `python3 -m unittest` exit ≠ 0 |
| D06 | Risco de processo | Diff fora do `scope_files` | `git status --porcelain` vs lista |
| D07 | **Lacuna esperada** | Teste com `@unittest.skip` | Regex de skip |
| D08 | **Lacuna esperada** | `sk_live_…` hardcoded | Regex de segredo |
| D09 | Risco de processo | Sem evidência RED antes do GREEN | Escaneamento do log de evidência |
| D10 | Risco de processo | Alteração em `auth/` sem revisão | Arquivo de revisão ausente |
| B01 | Legítimo | Typo em `README.md` | Clean |
| B02 | Legítimo | Feature `format_percent` + teste | Clean |
| B03 | Legítimo | Bugfix `parse_date` com RED→GREEN | Clean |
| B04 | Legítimo | Refactor (extração de `clean_title`) | Clean |
| B05 | Legítimo | Mudança em `auth/` **com** revisão registrada | Clean |
| B06 | Legítimo | Migration **com** aprovação humana registrada | Clean |

### 2.4 Métricas

Para cada cenário×braço:

- **Veredito** (`pass` / `blocked`) — o gate permitiu a entrega?
- **Passo do gate** onde bloqueou (quando aplicável)
- **Tempo total** da cerimônia
- **Tokens de contexto (proxy)**: `bytes/4` de (arquivos tocados + saídas de comando + contexto fixo de governança + artefatos de cerimônia)
- **Passos humanos** (revisão/aprovação)
- **Comandos executados**
- **Verdade fundamental**: o oráculo responde `defect=True/False` *antes* de o gate ser chamado

KPIs agregadas:

- **Recall de defeitos** = `veredito == "blocked" AND oráculo == "defect"` / nº de defeitos
- **Falsos positivos** = `veredito == "blocked" AND oráculo == "clean"` / nº de legítimos
- **Tokens por tarefa** — compara o custo de contexto
- **Tempo por tarefa** — compara a latência do fluxo

### 2.5 O que o benchmark **não** mede

- **Não há LLM no loop**. Não há custo real de token de um provedor,
  nem taxa de sucesso real de um agente escrevendo código. O "agente"
  aqui é um *harness determinístico* que executa a cerimônia do kit
  (ou a ausência dela). Isso é uma limitação explícita documentada.
- **Uma execução por cenário**. Determinístico, sem ICs. Para ter
  confiança estatística, `runner.py` pode ser repetido N vezes e
  agregado (todo o resultado já é JSONL).

## 3. Como executar

```bash
python3 benchmark/runner.py       # 16 cenários pareados -> results/raw.jsonl
python3 benchmark/overhead.py     # custos mecânicos -> results/overhead.json
python3 benchmark/aggregate.py    # KPIs + resultados.md + baseline/kit.jsonl
python3 scripts/xp kit eval compare benchmark/results/baseline.jsonl benchmark/results/kit.jsonl
```

## 4. Arquivos

- `substrate/` — repositório controlado (3 módulos + 24 testes)
- `scenarios.py` — os 16 cenários declarativos (dados, não código)
- `oracles.py` — verdades fundamentais independentes do kit
- `runner.py` — construção de sandboxes + execução dos dois braços
- `overhead.py` — custo fixo, latência do hook, JIT context retrieval
- `aggregate.py` — KPIs, eval-JSONL compatível com `xp kit eval` e `RESULTS.md`
- `results/` — artefatos gerados (`raw.jsonl`, `overhead.json`, `summary.json`, `baseline.jsonl`, `kit.jsonl`, `RESULTS.md`)
