# PLANO DE CORREÇÃO: XP Multi-Agent Kit v4 (segunda rodada)

Como usar: cole este arquivo no agy, ou salve em `.agents/specs/SPEC-007-CORRECAO-V4.md` e diga "Execute o plano do SPEC-007".

A primeira rodada (SPEC-006) entregou o emagrecimento: contexto base 23.525 B → 5.267 B, 80 → 25 skills, 11 → 6 agentes, 9 → 2 personas. Mas a parte que dá inteligência ao kit ficou incompleta, e em vários pontos o código **declara** algo que **não faz**. Esta rodada corrige isso. Não é uma rodada de features novas.

---

## 0. Regras de execução (prevalecem sobre o AGENTS.md)

1. **Nada é "feito" por declaração.** Um item só conta quando (a) existe um teste novo que **falhou antes** da correção e passa depois (guarde as duas saídas), e (b) o cenário de reprodução da seção 2 passa. No relatório de cada etapa, cole a saída real dos comandos. Relatório sem saída de comando = etapa não concluída.
2. **Proibido** em código novo ou alterado: `pass` como corpo de regra, comentário do tipo "considera ok", número fixo apresentado como medição (ex.: `stubs=0`), `TODO`/`FIXME`. Ao final de cada etapa rode `grep -rnE "considera ok|stubs=0 big=0" scripts/` e `grep -rn "^\s*pass\s*$" scripts/xp_*.py scripts/kit_*.py`; o resultado deve estar vazio ou justificado linha a linha.
3. **Um verdicto nunca imprime número que não mediu.** Quando não der para medir, imprima `?`.
4. Uma etapa por vez, na branch `fix/v4-honesty`. Fim de etapa: testes verdes → commit atômico → relatório de ≤15 linhas → próxima. Testes verdes = toda a suíte passa **exceto** as 2 falhas ambientais conhecidas: `test_run_system_health_check` e `test_run_command_rewrites_via_rtk_when_supported` (falham no baseline sem RTK/code-review-graph). Qualquer outra falha bloqueia a etapa.
5. Sem subagentes e sem revisão LLM-goldfish. Esforço `medium`; `high` só na Etapa 1 e na Etapa 3.
6. Mesma falha duas vezes = pare e reporte. Não faça perguntas; decida pelo padrão indicado e registre em "Decisões" (≤15 linhas) no SPEC-007.
7. Não mexa no que funciona (seção 5). Não crie dependências nem engines novas. Responda em português; arquivos do kit em inglês conciso.
8. Antes de agir, confirme no repositório cada problema da seção 1. Se algum já estiver corrigido ou divergir, anote e siga o repositório.

---

## 1. Problemas verificados (24)

Reproduzidos por execução (E) ou por leitura de código (L), no repositório entregue.

| ID | Problema | Ev. |
|---|---|---|
| B01 | `xp gate check` sem contrato dá `GATE PASS`: `load_contract()` cria um contrato L0 padrão | E |
| B02 | Veredito com números falsos: `ac=N/N` usa `len/len`; `stubs=0 big=0` são literais; `tests` sempre 0. Um L1 com 3 ACs e nenhum teste deu `GATE PASS ac=3/3` | E |
| B03 | Passo 7 (RED→GREEN) é um `pass`; faltam o passo 6 (frescor da evidência) e o 9 (AC→teste) | L |
| B04 | `ESCALATE` nunca dispara: `record_dead_end` deduplica assinaturas e o gate conta ocorrências; 3 falhas idênticas deram exit 1 nas 3 | E |
| B05 | `--sync-memory` gera `## 3.` + linha + ` PROGRESSO` (título corrompido), não rotaciona e estoura o orçamento (3.006 → 3.035 B) | E |
| B06 | Tier `review` não exige nada: diff em `src/auth/` com risco L1 → `tier=review` e `PASS` | E |
| B07 | `pre_tool_guard.py` não está em `hooks.json` (só gate e evolve o chamam); o agente pode escrever `approvals.json` | L |
| B08 | Aprovação identificada pela 1ª palavra do objetivo (`goal.split()[0]`) e aceita pelo 1º diretório do arquivo | L |
| B09 | Mensagem efêmera com `tier=auto` fixo (`dynamic_effort_hook.py:268`) | L |
| B10 | `workflow.yaml`: 16 dos 24 nós apontam para agentes que não existem mais (archivist, navigator, refactor-warden, release-gatekeeper, test-guardian) | L |
| B11 | `exit_cmd` dos nós usa `python3 -m unittest discover tests` fixo, não o `verify_cmd` do projeto | L |
| B12 | `xp flow` só tem `run/status/reset/reopen`; faltam `validate/start/next/advance/where`; o YAML não tem `approve_spec`, `kind`, `skills`, `dispatch` | E |
| B13 | `freeze_test_files()` congela só `ROOT_DIR/tests/test_*.py` (Python, pasta de testes do kit) | L |
| B14 | `components.yaml` cobre só 11 scripts novos (0 das 25 skills, 6 agentes, 7 policies); `kit_lint` só valida as entradas que existem | L |
| B15 | Só o gate emite eventos; `xp evolve report` analisou 0 eventos | E |
| B16 | `PROJECT_MEMORY.md` com 3.006 B (teto 3.000); reprova `test_ac5_governance_and_mission_egm_passes` | E |
| B17 | `goldfish-spec-review/SKILL.md` com 5.784 B (teto 3.500) | E |
| B18 | Scripts 62 → 71; candidatos de poda presentes; sem `contrib/` e sem `REMOVED.md` | E |
| B19 | `agy_effort_router.py` com 494 linhas (meta ≤150); bancos de regex mantidos | E |
| B20 | `sync_dynamic_skill_profile` definida e nunca chamada (código morto) | L |
| B21 | Sem arquivo `VERSION`; `"4.0.0"` fixo em `kit_constants.py` e no fallback de `kit_lint.py` | E |
| B22 | Shims `agy-*` sem aviso de depreciação | E |
| B23 | README afirma gate de "10 steps", hook `pre_tool_guard` e 24 skills (são 7 passos reais, hook não ligado, 25 skills) | L |
| B24 | Regra "AST em vez de grep" sem fallback (`token-economy.md` item 5, AGENTS.md seção 3) | L |

**Pendências a investigar (não confirmadas):**
- P1: a telemetria do kit reporta `skills_catalog` com **29.378 B por turno**, contra 5.411 B de frontmatters. Descubra o que ela soma.
- P2: as 14 skills de segurança (14.234 B) viraram 3 (4.739 B); confira se regras únicas se perderam.
- P3: `mcp_installers.py` ainda tem `OpenDesignInstaller`; confirme se a instalação padrão o instala.
- P4: confirme se `runtime/` e `policy.yaml` resolvem relativos ao **projeto-alvo** e não ao diretório do kit (`get_runtime_dir()` usa `Path(__file__).parent.parent` sem `KIT_RUNTIME_DIR`). Se resolverem ao kit, corrija: a raiz do projeto vem de `git rev-parse --show-toplevel` a partir do cwd.

---

## 2. Cenários de aceite (viram `tests/test_mission_scenarios.py`)

Cada cenário roda num repositório git **temporário**, com `KIT_RUNTIME_DIR` apontando para um diretório temporário. Este arquivo de teste é o critério de aceite da missão: ao final, todos passam. Escreva-os **primeiro** (RED), à medida que cada etapa começa.

| # | Dado | Quando | Então |
|---|---|---|---|
| S1 | nenhum contrato | `xp gate check` | exit 1, `GATE FAIL step=1` |
| S2 | L1, 3 ACs, nenhum teste os referencia, `verify_cmd=true` | gate | exit 1 (AC sem teste); o veredito nunca contém `stubs=0 big=0` fixos |
| S3 | arquivo alterado com `# TODO` | gate | exit 1, `step=4` (já funciona; manter) |
| S4 | `verify_cmd` falha igual duas vezes | gate ×2 | 1ª: exit 1; 2ª: exit 3 `ESCALATE`; `DEAD ENDS` não vazio |
| S5 | L1, diff em `src/auth/` | gate sem registro de revisão | exit 2 `BLOCK tier=review`; com registro de revisão para o hash do diff atual → PASS |
| S6 | diff em `db/migrations/` | gate sem aprovação | exit 2 com o ID de ação; aprovar com a 1ª palavra do objetivo **não** libera; o ID correto libera |
| S7 | memória inicial | `--sync-memory` ×25 | título `## 3. PROGRESSO` intacto e único; tamanho ≤3.000 B; linhas antigas no archive |
| S8 | bugfix L1, `verify_cmd` passando, nenhuma execução falha registrada | gate | exit 1 `step=7`; após `xp gate record` falho e depois passando → PASS; com `refactor: true` → PASS sem RED |
| S9 | execução passando registrada, depois arquivo do escopo editado | gate | exit 1 `step=6` (evidência velha) |
| S10 | testes `*.test.ts` congelados na saída de `red` | alterar um congelado | exit 1 `step=3`; **acrescentar** teste novo é permitido |
| S11 | payload PreToolUse simulado | escrever `approvals.json`; o agente chamar `xp approve`; `rm -rf` sem aprovação; leitura comum | negado, negado, negado, permitido; e `hooks.json` contém o guard |
| S12 | `workflow.yaml` entregue | `xp flow validate` | exit 0; com um nó apontando para agente inexistente (fixture) → exit ≠ 0; `xp flow next` imprime ≤800 B |
| S13 | eventos de fixture: 1 assinatura repetida ×3 e 1 componente sem uso | `xp evolve report` | lista 1 promoção e 1 candidato à remoção; `apply` em `AGENTS.md` sem `--approve` é recusado |
| S14 | skill existente sem entrada em `components.yaml` | `kit_lint` | exit ≠ 0 |
| S15 | repositório entregue | testes de orçamento | AGENTS.md + memória ≤8.000 B; memória ≤3.000 B |

---

## 3. Etapas

### Etapa 0 — Imediato

- **B16:** reduza `PROJECT_MEMORY.md` a ≤3.000 B (rotacione linhas antigas para o archive com `memory_archiver`). **Aceite:** `test_ac5_governance_and_mission_egm_passes` verde; S15.

### Etapa 1 — Gate honesto (`xp_gate.py`, `xp_contract.py`; B01 a B05)

Antes de editar, leia a API de `evidence_recorder.py` e `conformance_report.py` e **reutilize-as** (não reimplemente). `xp_gate.py` pode chegar a ≤320 linhas.

1. **B01:** `load_contract()` não cria mais contrato por conta própria. Sem contrato, o gate falha no passo 1. Quem precisar criar chama `init_contract` explicitamente. Ajuste os chamadores (`record_dead_end`, `xp_flow`).
2. **B03, passo 9:** conformidade AC→teste via `conformance_report` com `contract.acs`. AC sem teste = FAIL.
3. **B03, passos 6 e 7:** `xp gate record -- <comando>` executa o comando, grava exit code, timestamp e hash do diff no evidence log. Passo 7 (bugfix e L1+, exceto `refactor: true`): exige uma execução registrada com exit ≠ 0 **antes** de uma com exit 0. Passo 6: a última execução passando deve ser mais nova que a última edição de qualquer arquivo do escopo (ou ter o mesmo hash de diff).
4. **B02:** o veredito mostra só o que mediu: `verify=pass|fail|not_run`, `ac=<rastreados>/<declarados>`, `stubs=<n>` e `big=<n>` vindos de `audit_code_completeness`, `ev=<id real>`. `tests=` só se for extraído da saída do `verify_cmd` (unittest/pytest/jest); senão `?`. Em L1+ sem `verify_cmd`, FAIL ("nada prova a conclusão").
5. **B04:** `record_dead_end` passa a incrementar `count` e `last_seen` por assinatura em vez de ignorar. O gate recarrega `tried` depois de gravar e devolve **exit 3 `ESCALATE` na 2ª ocorrência** da mesma assinatura (ou ao atingir `max_attempts`). O bloco `FAILED/EXPECTED/SAW/FENCE/DEAD ENDS` mostra o `tried` atualizado.
6. **B05:** `--sync-memory` localiza a seção por regex de título (`^## 3\.`), insere o marcador depois da linha de título e rotaciona as linhas mais antigas via `memory_archiver` até caber em 3.000 B. Se não couber, falha com mensagem clara.

**Aceite:** S1, S2, S3, S4, S7, S8, S9; nenhum resultado dos `grep` da regra 2.

### Etapa 2 — Política imposta por código (B06 a B09, P4)

1. **P4 primeiro:** teste com um projeto temporário e o kit copiado em outro diretório; `run.json`, `policy.yaml` e `approvals.json` devem resolver pelo projeto-alvo. Corrija se falhar.
2. **B07:** registre `pre_tool_guard` em `hooks.json` (PreToolUse) e nos adaptadores dos hosts que suportam esse evento, usando o mesmo formato de payload/saída que `smart_tool_optimizer.py` já usa. Em hosts sem hook, mantenha a linha do AGENTS.md e documente o risco residual. O guard nega: escrita em `policy.yaml` e `approvals.json`, o agente chamando `xp approve`, e comandos do tier `human` sem aprovação.
3. **B08:** o ID de ação é determinístico: `sha1(tier + caminhos e comandos do tier human, ordenados)[:8]`, mostrado na mensagem de BLOCK. `has_approval` aceita só o ID exato. Remova `goal.split()[0]` e o aceite por 1º diretório.
4. **B06:** o tier `review` exige `xp review record --reviewer <nome> --verdict approve`, gravado com o hash do diff atual; o gate só dá PASS se o registro existir, vier de um revisor diferente do builder e casar com o diff. Documente o limite: o registro é de convenção, não de criptografia.
5. **B09:** a mensagem efêmera usa o tier efetivo (`calculate_effective_tier` com contrato e diff); sem contrato, `tier=n/a`. Mantenha ≤400 B.

**Aceite:** S5, S6, S11.

### Etapa 3 — Grafo reconectado (B10 a B13)

`xp_flow.py` pode ir até ≤320 linhas. Não adicione paralelismo nem retries novos.

1. **B10:** reaponte `run:` para os 6 agentes (`orchestrator`, `builder`, `reviewer`, `sentinel`, `designer`, `shipper`) ou `code`. Mapa sugerido: navigator → orchestrator; test-guardian → builder; refactor-warden e release-gatekeeper → reviewer (release → shipper); archivist → nó `code` de sync de memória.
2. **B11:** `exit_cmd` usa o placeholder `{verify_cmd}` do contrato. O nó `red` roda `! {verify_cmd}` e **registra a execução como evidência** (alimenta o passo 7); o nó `green` registra a execução passando.
3. **B12:** acrescente `validate` (agentes e skills existem, ≤2 skills por nó, último nó é `gate`, `exit_cmd` não vazio, placeholders resolvíveis), `start`, `next` (≤800 B: objetivo, agente, skills, `exit_cmd`), `advance` e `where`; mantenha `run/status/reset/reopen`. No YAML: `kind: model|code`, `skills`, `soft_turns`, nó humano `approve_spec` nos fluxos `feature` (L2/L3) e `migration`, um mapa `risk → fluxo` padrão, e o fluxo `design`.
4. **B13:** o congelamento usa `contract.test_globs` (padrão por stack: `tests/**/test_*.py`, `**/*.test.{ts,js,tsx}`, `**/*_test.go`, `src/test/**`), relativos à raiz do projeto. O gate (passo 3) bloqueia edição e remoção; acrescentar teste novo é permitido.

**Aceite:** S10, S12.

### Etapa 4 — Auto-melhoria alimentada (B14, B15)

1. **B14:** crie `xp kit components --sync`, que lista tudo o que existe em disco (skills, agentes, policies, hooks, personas, scripts) e acrescenta entradas faltantes com `prevents: ""`. Você preenche `prevents` com uma frase por componente. `kit_lint` falha se houver componente em disco sem entrada ou com `prevents` vazio.
2. **B15:** emita eventos de verdade, cada um ≤300 B e com `run_id` do contrato:
   - `failure` (com `class` e `signature`) a partir do PostToolUse quando `exit_code != 0`;
   - `usage` quando `smart_tool_optimizer` vê leitura de `.agents/**`, resolvendo o componente pelo `components.yaml`;
   - `node` na entrada e saída de cada nó do `xp flow`;
   - `approval` em `xp approve`;
   - `cost` a partir do `turn_telemetry`.
   O PostToolUse também chama `xp gate record` automaticamente quando o comando executado equivale ao `verify_cmd` do contrato (rastro observável, sem depender do agente).
3. **Reincidência pós-promoção:** confirme se o `xp evolve` já marca como ineficaz a assinatura promovida que reaparece. Se não existir, implemente e teste (promoções gravam `promoted_at`; reaparecimento depois disso gera alerta e sobe um degrau: teste → hook → regra).

**Aceite:** S13, S14.

### Etapa 5 — Poda, limpeza e pendências (B17 a B24, P1 a P3)

1. **B18, poda por evidência:** para cada `scripts/*`, registre quem o importa, quem o referencia (hooks, instalador, workflow, skills, README) e se só os testes o usam. Sem referência real → `contrib/` (com seus testes) ou apagar, e liste em `REMOVED.md` com justificativa. Candidatos: `agy_dashboard`, `agy_daemon`, `skill_packer` (+ doc Agensi), `context_compactor`, `output_noise` (funda no `tool-size-guard`), `session_compactor`, `session_resumer`, `agy-handoff` (reaproveite `xp_session.py` se já faz isso), `agy-sanitize` e `sanitize-tool-output.sh`. Só remova um compressor depois que os testes provarem cobertura equivalente. **Meta:** `scripts/` abaixo de 62 entradas.
2. **B19:** reduza `agy_effort_router.py` a ≤150 linhas (mapeamento risco/nó → esforço + heurística mínima para o primeiro prompt); remova os bancos de regex se os testes confirmarem que não são necessários; se um teste exigir um comportamento, mantenha-o e registre a decisão.
3. **B20:** remova `sync_dynamic_skill_profile`.
4. **B21:** crie `VERSION`; `kit_constants.py`, `kit_lint.py`, README e instalador leem dele; `kit_lint` falha se houver divergência.
5. **B22:** os shims `agy-*` imprimem uma linha de depreciação apontando para o comando `xp` equivalente.
6. **B17:** reduza `goldfish-spec-review/SKILL.md` a ≤3.500 B movendo detalhe para `sections/`.
7. **B23:** o README não tem contagens digitadas à mão; `kit_lint` compara qualquer "N skills/agents/steps" com a realidade. Toda afirmação do README precisa ser verdadeira depois das Etapas 1 a 3.
8. **B24:** a regra de AST ganha fallback sem bloqueio (se `code-review-graph` não existir, usar busca textual e seguir).
9. **SKILLS_INDEX.md:** gerado sob demanda em `runtime/`, fora do versionamento (`.gitignore`); confirme que nenhum host o carrega por padrão.
10. **P1:** descubra o que compõe os 29.378 B de `skills_catalog`; registre a conclusão em "Decisões". Se for injeção real por turno, reduza as descriptions (≤110 caracteres cada) até a medição cair.
11. **P2, auditoria de fusão:** extraia as regras imperativas (linhas de lista) das skills do `v3.9.2-baseline` e liste as que não aparecem, em termos equivalentes, na skill que as absorveu. Restaure em `sections/` as que forem regras únicas e registre as descartadas em `REMOVED.md`.
12. **P3:** o OpenDesign só é instalado por `xp kit pack enable design`; teste a instalação padrão num projeto limpo.

### Etapa 6 — Verificação final (você não decide sozinho que acabou)

1. `python3 -m unittest tests.test_mission_scenarios` com S1 a S15 verdes.
2. Suíte completa: só as 2 falhas ambientais conhecidas.
3. `xp kit doctor` e `kit_lint` verdes.
4. Os dois `grep` da regra 2 vazios.
5. `xp gate --receipt` do próprio trabalho, colado no relatório.
6. Relatório final (≤30 linhas): tabela antes/depois dos indicadores abaixo, status de B01 a B24 e P1 a P4, riscos em aberto (hosts sem hooks: política e anti-bypass só por convenção).

| Indicador | Hoje | Meta |
|---|---|---|
| AGENTS.md + memória | 5.267 B | ≤8.000 B |
| PROJECT_MEMORY.md | 3.006 B | ≤3.000 B |
| Testes com falha | 3 (2 ambientais) | 2 (as mesmas ambientais) |
| Passos do gate realmente implementados | 7 de 10 | 10 de 10 |
| Nós do `workflow.yaml` com agente inexistente | 16 de 24 | 0 |
| Componentes cobertos em `components.yaml` | 11 | todos |
| Eventos analisados pelo `xp evolve` (fixture) | 0 | >0, com 1 promoção e 1 remoção |
| Entradas em `scripts/` | 71 | <62 |
| Linhas do roteador de esforço | 494 | ≤150 |
| SKILL.md acima de 3.500 B | 1 | 0 |

---

## 4. Ordem e dependências

Etapa 0 → 1 → 2 → 3 → 4 → 5 → 6. A Etapa 3 depende da 1 (o nó `red` grava evidência para o passo 7). A Etapa 4 depende da 3 (eventos `node`). A 2 só pode ser fechada com S11 passando; sem isso o README não pode afirmar que a política é imposta.

## 5. Não mexer (funciona e foi verificado)

Derivação do tier por caminho (`migrations/` bloqueia sem aprovação); varredura de TODO e God-file (passo 4); `checks[]` (passo 5); `verify_cmd` (passo 8); estrutura do AGENTS.md em 8 seções; `XP_EGM_LLM` e `EGM_LLM_REVIEW`; as 2 personas goldfish; os 4 packs; a mensagem efêmera ≤400 B; o benchmark (`xp_eval.py`, `tests/evals`); os 25 diretórios de skills e os 6 agentes; o instalador **não** envia os specs do kit aos projetos-alvo (confirmado).

## 6. Proibições

- Não reescrever histórico git nem fazer force push.
- Não alterar `AGENTS.md`, `policies/` ou `policy.yaml` por auto-melhoria sem `--approve`.
- Não apagar nem pular teste para ficar verde; todo teste removido vai para `REMOVED.md` com justificativa.
- Não adicionar prosa onde um teste, hook ou script resolve.
- Nunca permitir que o agente escreva `approvals.json` ou `policy.yaml`.
