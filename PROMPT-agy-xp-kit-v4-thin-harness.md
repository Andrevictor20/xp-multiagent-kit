# MISSÃO: XP Multi-Agent Kit v4 — "Thin Harness" (v2 do prompt)

Objetivo: simplificar o kit, torná-lo auto-melhorável com evidência e cortar tokens **sem perder as garantias de qualidade** (TDD estrito, rastreio AC→teste, gate de release, segurança L3).

Como usar: cole este arquivo no agy, ou salve em `.agents/specs/SPEC-006-THIN-HARNESS.md` e diga "Execute a missão do SPEC-006".

---

## 0. Regras de execução (prevalecem sobre o AGENTS.md atual)

Esta missão é L2. O Stop Gate de spec é **pré-autorizado**. Essa pré-autorização vale só para `approve_spec` e **nunca cobre ações sem desfazer** (seção 3, Fase 1, `policy.yaml`).

1. NÃO despache subagentes e NÃO rode revisão LLM-goldfish. Use só CLIs determinísticos (`xp-spec validate`, `xp-goldfish --check-readiness|--check-code|--multipass`, `xp-conformance`).
2. Esforço: `high` só nas Fases 0 e 3; `medium` no resto; `low` em edição mecânica.
3. Uma fase por vez, na branch `refactor/thin-harness`. Fim de fase: testes verdes → commit atômico → relatório de ≤15 linhas → próxima. Atualize `PROJECT_MEMORY.md` só no fim de cada fase.
4. Não faça perguntas. Decida pelo padrão indicado e registre em "Decisões" (≤20 linhas) no SPEC-006.
5. **Mesma falha duas vezes (mesmo erro, mesma causa aparente) = pare e reporte.** Não tente uma terceira vez. Outros motivos de parada: ACs em conflito; operação destrutiva fora do repositório.
6. Confirme cada fato da seção 2 no repositório antes de agir. Se divergir, vale o repositório; anote.
7. Responda em português; arquivos internos do kit em inglês conciso.
8. Primeiro comando: `git tag v3.9.2-baseline && python3 -m unittest discover tests` (registre o nº de testes).
9. **Projete a partir do meio:** antes de tocar em qualquer corte, o gate (Fase 1) precisa existir e estar testado. Nenhuma regra em prosa é removida antes de o mecanismo que a substitui passar nos testes.
10. Todo componente novo que você criar entra em `components.yaml` com `prevents:` e critério de remoção (P7). Complexidade se ganha por falha observada.

---

## 1. Princípios

Fontes (lidas na íntegra): "Harness Engineering: The Complete Guide…" (@LunarResearcher, 6 set) e "Harness, Loops, Graphs: What Each Layer Fixes and What It Breaks" (@m4lkxx, 25 out).

| Camada | Função | Kit hoje | Kit v4 |
|---|---|---|---|
| Harness | o que o agente pode fazer, estado, limites | gordo: regras em prosa repetidas em 8–14 arquivos | fino: AGENTS.md ≤3 KB; o resto vira código e política |
| Loop | verificação honesta | auto-auditoria de 5 pontos em prosa: o modelo diz "pronto" | `xp gate` determinístico, evidência em escada |
| Graph | o que acontece depois, e quem decide | 11 workflows em prosa, 3 orçamentos conflitantes, risco rotulado só pelo modelo | `workflow.yaml` mínimo + `policy.yaml` imposta por código |
| Learning | melhora com o uso | lições `[L-NNN]` manuais | `xp evolve`: lição vira restrição na camada dona, com evidência |

Oito regras:

- **P1 Thin harness, fat code (escada de instrução).** explicação → checklist → template → checagem automática → política imposta. Cada regra sobe o máximo possível; ao subir, sai da prosa. Teste, hook ou script resolve? Não vira texto.
- **P2 Contrato antes de agir.** Cinco perguntas: resultado, escopo, o que não pode mudar, evidência de conclusão, o que exige aprovação humana.
- **P3 Pronto = evidência.** Do mais forte ao mais fraco: determinístico (testes exit 0, tipos, schema) > observável (o traço prova que rodou) > independente (revisor em contexto separado) > auto-relato (**nunca conta**). Checagem mais barata primeiro, para na primeira falha. Onde código responde, não use modelo.
- **P4 O modelo rotula, o código decide o que o rótulo libera.** O nível de desfazer vem de caminhos e comandos reais, não do que o modelo declarou. Atenção humana só onde não há como desfazer.
- **P5 Falha tem classe e muda uma condição.** Retry idêntico é repetição, não recuperação. Mesmo resultado duas vezes = o agente parou de aprender: pare e escale.
- **P6 Lição é restrição de 1 linha, na camada dona.** Não é transcrição de log. Lição na camada errada vira conselho.
- **P7 Cada componente paga aluguel e declara o que previne.** Se a falha que ele previne não ocorre mais, ele sai. Construir para apagar.
- **P8 Grafo mínimo.** A maioria das tarefas termina no nível "loop com feedback". Só suba quando a falha atual custar mais que construir o próximo nível.

---

## 2. Fatos medidos (verificar antes de agir)

- Contexto base fixo: `AGENTS.md` 5.930 B + `PROJECT_MEMORY.md` 6.674 B + `SKILLS_INDEX.md` 8.679 B + `token-economy.md` 2.242 B = **23.525 B (~6k tokens por turno)**. Frontmatters das 80 skills: mais 15.189 B, repetidos no índice.
- 80 skills = 155.873 B. `goldfish-spec-review` = 50.696 B (9 personas). 14 skills de segurança de 0,7–2 KB; ~21 de UI/marketing sobrepostas.
- Frases repetidas: "Completeness Over Speed" em 8 arquivos, Heilmeier em 12, EGM Pass em 12, Stop Gate em 14, PROJECT_MEMORY.md em 35.
- Orçamentos de turno conflitantes: task-routing 3/8/20, workflows 3/8, token-economy 5/25/100/∞.
- `trivial.md` (L0) exige gravar `PROJECT_MEMORY.md` mesmo em typo.
- O risco (L0–L3) é inferido pelo modelo; nenhum código decide o que o rótulo libera. A pré-autorização "em equipe/EGM" pode se estender além da spec.
- Anti-test-bypass ("nunca apagar/pular teste") existe só em prosa.
- "Pronto" depende da auto-auditoria de 5 pontos e do "Relatório de Execução Multiagente" em prosa; não há recibo gerado por código.
- O hook PreInvocation troca perfil de skills por symlink (`all` em L3 ou "equipe") e reescreve settings a cada prompt (provável quebra de cache de prefixo).
- ~25 CLIs duplicados em `xp-*` e `agy-*`; RTK, OpenDesign e code-review-graph instalados sempre; AGENTS.md exige code-review-graph "mandatoriamente", sem fallback.
- 5+ compressores de saída sobrepostos: tool-size-guard, smart_tool_optimizer (28 KB), context_compactor, agy-sanitize, output_noise, além do RTK.
- Cursor/Qoder/Codex copiam o AGENTS.md inteiro como regra always-on.
- Inconsistências: README v3.1 vs AGENTS v3.9; skills contadas como 77/79/80; description do goldfish no índice quebrada (`>-`); `goldfish-spec-review/SKILL.md` com 6.015 B (teto 6.000); `REPO_MAP.md` commitado e desatualizado (cita `token_tracker.py` inexistente).
- scripts 466 KB e tests 273 KB; boa parte (dashboard, daemon, skill_packer, 3 ferramentas de checkpoint) não afeta tokens de runtime. **A verificar por evidência.**
- A verificar: o instalador copia para projetos-alvo arquivos de desenvolvimento do próprio kit (memory, specs 001–005, mission-report, HISTORY)?

---

## 3. Fases

### Fase 0 — Baseline e plano (somente leitura)

1. Tag `v3.9.2-baseline`, testes, `python3 scripts/skill_index.py audit`.
2. Confirme a seção 2. Gere `SPEC-006-THIN-HARNESS.md` com os ACs abaixo, a tabela de merge de skills/agentes (≤40 linhas), "Decisões" e a **tabela da escada de regras**: toda regra de `AGENTS.md` e `policies/` com seu degrau atual e o degrau-alvo. Regra cujo alvo é automático sai da prosa só depois que o mecanismo existir.
3. Valide só com `xp-spec validate` e `xp-goldfish --check-readiness`.

### Fase 1 — Contrato, política, gate, eventos e recibo (TDD: RED primeiro)

**AC-1 Contrato e estado de execução.** `scripts/xp_contract.py` (≤150 linhas) mantém `.agents/runtime/run.json` (gitignored):
`{risk, goal, acs[], scope_files[], constraints[], approval_required[], verify_cmd, checks[], max_attempts, refactor, tried[], known, next, never[]}`.
O modelo cria o contrato em **uma** chamada de ferramenta (≤8 linhas). L0 só `risk` + `goal`. `tried[]` (becos sem saída) e `never[]` fazem parte do estado: o gate escreve em `tried[]` automaticamente. É a "memória do loop", para a tentativa 3 não virar a tentativa 1. Histórico bruto fica em eventos (AC-4); estado compilado fica em `run.json` e `PROJECT_MEMORY.md`.

**AC-2 Política por custo de desfazer.** `.agents/policy.yaml` (≤40 linhas; o instalador gera padrões por stack) com 3 níveis:
- `auto`: docs, testes, uma função, qualquer coisa revertível por commit.
- `review`: auth, pagamentos, helpers compartilhados, schemas, config de CI. Exige verde + traço + revisão independente (`reviewer`).
- `human`: migrations, `*.tf`, deploy/push/publish, `rm -rf`, `DROP`, escrita em `.env`, gasto. Exige aprovação humana. Não existe score que "libere".

O gate calcula `tier_efetivo = max(declarado, derivado)` a partir de caminhos do diff e comandos vistos nos eventos. Se o modelo declarou L1 mas o diff toca `auth/`, o gate escala e bloqueia até haver threat model e aprovação. Aprovações vêm de `xp approve <id>` rodado pelo humano.
Um hook PreToolUse nega ao agente escrita em `policy.yaml` e em `approvals.json`, e bloqueia comandos `human` sem aprovação. Em hosts sem hook, valem `xp-run` e uma linha no AGENTS.md; documente o risco residual.

**AC-3 `xp gate`.** `scripts/xp_gate.py` (≤300 linhas; reutilize `goldfish_review.audit_code_completeness`, `conformance_report`, `evidence_recorder`, `memory_archiver`; não reimplemente nada). Ordem, **barato primeiro, para na primeira falha**:
1. contrato existe e é válido;
2. cerca de escopo: diff ⊆ `scope_files`, `constraints` respeitados, tier efetivo derivado;
3. arquivos congelados intactos (ver Fase 3: testes aprovados em `red` não podem ser editados ou apagados; testes novos podem ser acrescentados);
4. varredura estática nos arquivos alterados: `TODO`/`FIXME`/`NotImplementedError`/`as any`/`@ts-ignore`, arquivo >500 linhas;
5. `checks[]` baratos (lint, tipos), se configurados;
6. frescor da evidência: nenhum arquivo editado depois da última execução registrada de teste (conceito `dirty_code_untested` que o kit já tem);
7. **RED→GREEN observável** em bugfix e L1+: o evidence log precisa ter uma execução falha do teste-alvo antes da passa, exceto com `refactor: true`. Teste que já passava antes da correção não prova nada;
8. `verify_cmd`;
9. conformidade AC→teste;
10. requisitos do tier (`review`/`human` satisfeitos?).

Veredito em uma linha: `GATE PASS|FAIL|BLOCK|ESCALATE risk=L1 tier=auto tests=12/12 ac=3/3 stubs=0 big=0 ev=EV-…`. Exit codes 0/1/2/3 (3 = escalar).
Em falha, bloco de ≤30 linhas no formato do artigo: `FAILED / EXPECTED / SAW (arquivo:linha) / FENCE / DEAD ENDS`, mais uma linha `hint:` pela classe da falha. O bloco é anexado a `tried[]`. Segunda falha com a mesma `signature` (ou `max_attempts` esgotado) devolve `ESCALATE`: pare e reporte; o gate nunca sugere "tente de novo igual".
`xp gate --sync-memory "<resumo de 1 linha>"` acrescenta a linha em `PROJECT_MEMORY.md` e rotaciona. Memória rotineira deixa de exigir agente (`archivist` some na Fase 4).
`xp gate --receipt` imprime o **recibo de mudança** (≤15 linhas), gerado só por código: `OBJETIVO / ALTERADO / VERIFICADO / NÃO VERIFICADO / DECISÕES / RISCOS / APROVAÇÃO NECESSÁRIA`. "Não verificado" lista as checagens do contrato que não rodaram. **O recibo é a resposta final ao usuário** (em PT) e substitui a auto-auditoria de 5 pontos e o relatório de roster; reduz também tokens de saída. É também o handoff: estado + evidência + risco em aberto.
Um teste por regra de bloqueio. Onde o host tiver hook de parada/pós-invocação, chame o gate ali; senão, uma linha no AGENTS.md ("rode `xp gate --receipt` e responda com ele"). Verifique em `host_adapters.py` o que cada host suporta; não presuma.

**AC-4 Eventos e classes de falha.** `scripts/kit_events.py` (≤100 linhas): `emit(kind, **campos)` grava JSONL em `.agents/runtime/` (rotação em 1 MB, ≤300 B por linha, só os primeiros 200 caracteres de qualquer texto, só local, `XP_EVENTS=0` desliga). Tipos: `node`, `gate`, `approval`, `failure`, `usage`, `cost`.
`failure` leva `signature = sha1(tool + 1ª linha de erro normalizada)[:10]` e `class ∈ {timeout, invalid_args, test_fail, permission, other}` por classificador determinístico. `usage` vem de `smart_tool_optimizer` quando vê leitura de `.agents/**`. Em hosts sem hook, a cobertura é parcial; documente.

### Fase 2 — Cortes seguros (só agora, com o gate pronto)

**AC-5 Contexto base ≤ 8.000 B** (AGENTS.md ≤3.000 B + PROJECT_MEMORY.md ≤3.000 B, sem índice carregado). Injeção por prompt ≤400 B.
- `AGENTS.md` segue a **especificação de harness em 8 seções**, 1–3 linhas cada, cada uma apontando seu mecanismo: CONTRATO (`xp contract`), CONTEXTO (mapa + `xp context`), FERRAMENTAS (`xp`, hooks), ESTADO (`run.json`, PROJECT_MEMORY), POLÍTICA (`policy.yaml`), VERIFICAÇÃO (`xp gate`), RECUPERAÇÃO (classes de falha, parar na 2ª repetição), OBSERVABILIDADE (eventos + recibo). `xp-kit doctor` falha se alguma seção não tiver mecanismo definido (campo indefinido = agente improvisando). Mais: regra de idioma (1 linha) e invariantes.
- `SKILLS_INDEX.md` deixa de ser carregado: `skill_index.py generate` o gera sob demanda em `runtime/`. Corrija o bug do `>-`. `REPO_MAP.md` deixa de ser commitado: gerado sob demanda.
- Remova o mandato "Completeness Over Speed / independentemente do tempo" e sua constante. Novo critério: **pronto = ACs rastreados + gate PASS**. Zero TODO/stub continua, imposto pelo gate.
- `PROJECT_MEMORY.md` ≤3.000 B nas quatro categorias do artigo: FATOS, DECISÕES (com motivo), PROGRESSO, LIÇÕES (+ lista `never`). Cada linha com data; o excedente rotaciona com `memory_archiver`.
- Funda as 12 policies em ≤7 arquivos.

**AC-6 Fonte única.** Cada conceito-chave (EGM, Stop Gate, Heilmeier, critério de pronto, orçamento de turnos, política de memória) é definido em ≤1 arquivo; os demais só linkam. Números de orçamento só em `kit_constants.py` e `workflow.yaml`. `tests/test_kit_lint.py` conta ocorrências. Contagens e versão nunca à mão: geradas por script; versão lida do arquivo `VERSION`. Corrija todas as inconsistências da seção 2.
**CLI única:** `xp <contract|gate|flow|evolve|kit|memory|context|approve|run>`. Os `xp-*`/`agy-*` viram shims finos marcados como deprecados por uma versão; o AGENTS.md só cita `xp`. Reduzir superfície de ferramentas é parte do harness.
Se o instalador enviar arquivos de desenvolvimento do kit aos projetos-alvo, pare de enviá-los.

### Fase 3 — Grafo mínimo

**AC-7** `.agents/graph/workflow.yaml` (≤150 linhas) + `scripts/xp_flow.py` (≤250 linhas).
- Cada nó: `kind: model|code`, `agent`, `skills` (≤2), `exit_cmd` (**comando determinístico de saída do nó**, não só no fim), `soft_turns`. Nós `kind: code` (`gate`, `sync_memory`, `merge`) nunca invocam LLM: se o passo dá sempre a mesma saída para a mesma entrada, é código. Gate onde o trabalho sai do nó, não só no final.
- Fluxos L0–L3, bugfix, design, migration, incident, release por composição (`classify → contract → spec → approve_spec → red → green → review → gate → done`).
- **Congelar o que passou.** Ao sair de `red`, `xp flow` grava SHA-256 dos testes aprovados em `run.json`; o gate bloqueia edição ou remoção desses arquivos (anti-test-bypass mecânico). `xp flow reopen <nó> --reason` reabre explicitamente e é registrado. Só o nó que falhou roda de novo, com o bloco de feedback.
- `approve_spec` é a trava humana L2/L3 (preserva a regra Anti-Self-Test). A pré-autorização do usuário vale só para ela.
- Nó opcional `dispatch`, só se o contrato listar `independent_units ≥ 2` (teste de início antecipado: o que quebraria se B começasse antes de A?). Cada unidade ganha worktree próprio, `scope_files` como cerca e um nó `merge` determinístico. Sem isso, nada de multiagente.
- Comandos: `validate` (nós alcançáveis; todo caminho terminal passa por `gate`; nenhum nó com >2 skills), `start`, `next` (imprime ≤800 B: objetivo, agente, skills, `exit_cmd`), `advance`, `reopen`, `where`. Estado em `runtime/flow_state.json`.
- Gere stubs finos para os hosts (`.opencode/command/*.md` etc.) a partir do YAML no instalador; depois apague os 11 `.agents/workflows/*.md`.
- Não implemente paralelismo, retries nem engine. O grafo só vale o que cada nó paga.

### Fase 4 — Consolidação

**AC-8** Agentes ≤6; skills ≤36; soma dos frontmatters ≤6.000 B; cada `SKILL.md` ≤3.500 B, com detalhe em `sections/` sob demanda. Fundir ≠ perder: mova checklists únicos para `sections/`, deduplique o repetido e liste regras descartadas e o motivo no apêndice do SPEC.
- **Agentes (6):** `orchestrator` (absorve navigator e genesis, esta como nó `bootstrap`), `builder` (absorve test-guardian), `reviewer` (refactor-warden + release-gatekeeper), `sentinel`, `designer`, `shipper`. `archivist` vira o script de sync do gate.
- **Segurança (14 → 3):** `security-review` (api, authn, authz, availability, crypto, privacy, secrets, supply-chain, container, security-testing, security-observability como seções), `threat-modeling`, `cloud-and-iac-security`.
- **Processo:** `spec-pyramid` (acceptance-test-driven + specification-by-example + spec-driven-development + pair-navigator), `tdd-safety-net` (+ test-evidence-walkthrough, conformance-tracker; property-based e mutation como seções), `code-hygiene-review` (no-workarounds + code-deslop + refactor-watchdog + diff-simplifier), `project-memory` (+ lesson-learned, adr-architect-tracker, living-docs-keeper), `release-and-deploy` (zero-downtime + deploy-pipeline + ci-security-gate).
- **UI (~21 → ~7):** `frontend-taste-engineering` com variantes (minimalist, high-end, industrial-brutalist, visual-direction-studio como seções), `design-system` (tokens + architecture + component-architecture + component-registry), `ui-accessibility-responsive`, `ui-quality-gate` (+ visual-regression, redesign-ui-audit), `design-intelligence`, `mobile-app-design`, `conversion-and-seo`.
- **Packs opcionais** (marketing, brutalist, roadmapping etc.) em `.agents/packs/<nome>/`, fora da instalação padrão: `xp kit pack enable <nome>`. **OpenDesign vira opt-in** (pack `design`); RTK e code-review-graph ficam. Onde code-review-graph não estiver instalado, a regra "AST em vez de grep" tem **fallback sem bloqueio** (precondição e comportamento de falha são parte do contrato de qualquer ferramenta).
- **Perfil estático** escolhido na instalação por detecção de stack. **Remova a troca dinâmica de perfil do hook** (`sync_dynamic_skill_profile`).
- **`.agents/components.yaml`** (≤120 linhas, **não carregado no contexto**): para cada skill, agente, policy, hook e persona: `id`, `kind`, `prevents` (a falha que previne), `added`, `review_by`. `kit_lint` falha se faltar entrada. Sem `prevents` = candidato a remoção.

### Fase 5 — EGM, esforço e hooks

**AC-9**
- **Verificação como tentativa de refutação.** Persona `spec_reviewer` (≤2 KB; funde design_critic + implementation_readiness) com rubrica explícita de **rejeição**, contexto novo, acesso à spec e ao contrato, **sem permissão de reparar nem elogiar**. Só devolve evidência de rejeição ou aceite.
- **EGM em 3 passes, com LLM só onde paga.** Pass 1: `--check-readiness` sempre; revisão cega por LLM com **um** revisor apenas em L3, ou em L2 quando o check emitir warning ou a spec tocar >8 arquivos. Pass 2: `--check-code` + gate sempre; LLM `code_reviewer` só se pedido, se o tier efetivo for `review`, ou se o gate sinalizar ambiguidade. Pass 3: `xp-conformance` + `--multipass` sempre.
- Config em `kit_constants.EGM_LLM_REVIEW = {"L2": "on_warning", "L3": "single"}`; override `XP_EGM_LLM=always|off` (chave de rollback).
- Personas goldfish 9 → 2 (≤2 KB cada); recursos de padrão ≤2 arquivos; sem instâncias A/B e sem synthesizer. Preserve como bullets os checks únicos de zoom_out, comprehension, structural e style.
- **Esforço por evidência.** `low` em L0; `medium` por padrão; `high` só para autoria de spec L2/L3 e threat model L3. **Falha repetida não escala esforço: escala para o humano** (regra P5). `agy_effort_router.py` ≤150 linhas: mapeia `risk`/nó atual → esforço, com heurística mínima só para o primeiro prompt. Remova os bancos de regex (CONTINUATION/DIRECTIVE) se os testes confirmarem que são desnecessários.
- **Hook PreInvocation:** mensagem efêmera ≤400 B (`[xp] risk=L1 tier=auto effort=medium node=red | jit: …`); JIT só acima de um limiar de score FTS, ≤80 tokens; sem reescrever settings quando nada mudou.
- **Compressores:** manter RTK (se presente) + `tool-size-guard` + `smart_tool_optimizer` (loop detection, leitura de arquivo inteiro ≤800 linhas). Funda `output_noise` no guard; remova context_compactor e agy-sanitize/sanitize-tool-output.sh só se o grafo de imports e os testes provarem cobertura equivalente.

### Fase 6 — Auto-melhoria (`xp evolve`)

**AC-10** `scripts/xp_evolve.py` (≤350 linhas, sem rede, sem LLM). Entradas: `events` (failure/usage/gate/cost), `turn_log.jsonl`, `components.yaml`.
- `xp evolve report`: por componente, as cinco perguntas do artigo de harness: o que previne (`prevents`), quanto a falha ainda ocorre (recorrência nas últimas N sessões), custo (bytes + ativações), se dá para ser mais simples, o que acontece se remover. Candidatos:
  - **Remoção:** 0 ativações em ≥10 sessões e >1 KB, ou `prevents` que não recorre em 30 sessões (decay).
  - **Promoção:** mesma `signature` ≥3 vezes.
  - **Inchaço:** contexto base acima do orçamento.
- **Escada de promoção e camada dona.** Toda proposta indica a camada que possui a falha: harness (ferramenta, entrada em `never`, política), loop (nova checagem), graph (nova regra de divisão ou gate). Degrau, nesta ordem: teste de regressão → hook/política → regra de ≤2 linhas (com `signature`, `layer`, `added`, `review_by`). Entradas `never` que são padrão de caminho ou comando viram `deny` em `policy.yaml` (parede, não desejo).
- **Teste do nível 7:** após promover uma `signature`, se ela **reaparece**, a proposta foi ineficaz: marque, suba um degrau ou mude de camada. KPI: a mesma classe de falha nunca custa duas vezes.
- `xp evolve propose`: grava `.agents/proposals/PR-NNN.md` com diff, evidência, camada, degrau e rollback. O template inclui as 8 perguntas de diagnóstico do artigo (contrato ambíguo? contexto invisível? ferramenta errada exposta? precondição faltando? resultado não verificável? política dentro do prompt? recuperação ampla demais? traço insuficiente?).
- `xp evolve apply PR-NNN`: só com testes + `kit_lint` verdes. Mudanças em `AGENTS.md`, `policies/` e `policy.yaml` exigem `--approve` humano. Nunca altera o núcleo sozinho.
- **Ablação (se couber em ≤30 linhas):** `components.local.yaml` (gitignored) com `disabled:`; fluxo e hooks respeitam; usado no benchmark para responder "o que acontece se remover?".
- `lesson-learned` passa a gravar `signature`, `layer` e `fix_type: test|hook|rule`. A injeção JIT de lições envia **só a restrição de 1 linha** que casa com a tarefa, nunca o log.
- Passo automático e sem LLM no fim de cada L1+: o gate já emite os eventos que o `evolve` consome (zero turnos extras). Fixtures de teste para report, propose, apply, reaparecimento pós-promoção e bloqueio sem `--approve`.

### Fase 7 — Poda, docs e release

**AC-11**
- **Auditoria de scripts por evidência.** Para cada `scripts/*`: importado por quem, referenciado por skill/fluxo/hook/instalador, ou só por testes. Sem referência real → `contrib/` (não instalado) ou apagar. Candidatos prováveis: agy_dashboard, agy_daemon, skill_packer + doc Agensi. Consolide session_compactor / session_resumer / agy-handoff em **uma** ferramenta que serializa `run.json` + recibo. `antigravity_multiagent.py` e `multiagent_drivers.py` ficam opt-in, só via nó `dispatch`. Mantenha os adaptadores dos 5 hosts.
- README ≤120 linhas: diagrama das 4 camadas, instalação, 6 comandos `xp`. `VERSION` = `4.0.0` em todo lugar. `xp kit doctor` ganha `lint`: orçamentos, duplicação, versão, contagens, 8 seções do AGENTS.md com mecanismo, `components.yaml` completo.

**AC-12 Benchmark (o usuário roda; você não).** Crie `tests/evals/` com 4 tarefas de referência (L0 typo, L1 bugfix, L2 feature, L3 auth) e `xp kit eval compare a.jsonl b.jsonl`. **Métrica principal: tokens por tarefa aceita** (`tokens totais / tarefas com gate PASS`); tokens por tarefa sozinhos recompensam desistir cedo. Demais métricas: taxa de PASS no primeiro gate; taxa de falha repetida (mesma `signature` ≥2 na sessão); intervenções humanas por tarefa; sessões L1+ que terminam sem veredito do gate (proxy de "conclusão sem suporte"); turnos; tempo até resultado verificado. `docs/BENCHMARK.md` ≤40 linhas explica como rodar as 4 tarefas em `v3.9.2-baseline` e em `v4.0.0`.

---

## 4. Invariantes (não podem regredir)

- **AC-13.** Todos os testes das funcionalidades mantidas passam. Todo teste removido vai para `REMOVED.md` com justificativa. Nenhum teste é apagado ou pulado para ficar verde.
- Instaladores dos 5 hosts e o Windows continuam gerando seus arquivos (testes de host passam).
- Mantidos: TDD estrito, anti-test-bypass (agora com congelamento), bloqueio por AC sem teste, STRIDE em L3, trava humana L2/L3 em single-agent, Canary/Blue-Green + rollback, <500 linhas por arquivo, saída ao usuário em PT-BR.
- Sem novas dependências. Scripts novos sem rede. Sem TODO/stub no código novo.

## 5. Proibições

- Não reescrever histórico git nem fazer force push.
- Não alterar `AGENTS.md`, policies ou `policy.yaml` por auto-melhoria sem `--approve`.
- Não adicionar prosa para resolver o que teste, hook ou script resolve.
- Não criar engine de orquestração, dashboard novo ou dependências.
- Nunca deixar o agente escrever `approvals.json` ou `policy.yaml`.

## 6. Entrega final (use `xp gate --receipt` e acrescente ≤25 linhas)

1. Tabela antes/depois: bytes de contexto base, nº de skills/agentes/personas/policies/workflows/CLIs, bytes de frontmatter, linhas de scripts, nº de testes (e removidos justificados).
2. Status de AC-1…AC-13 via `xp-conformance`.
3. Chaves de rollback (`XP_EGM_LLM`, `XP_EVENTS`, tag `v3.9.2-baseline`).
4. Riscos em aberto: hosts sem hooks (política e anti-bypass só por convenção), cobertura parcial de eventos, o que ficou em `contrib/` e `packs/`.
5. Próximo passo do usuário: rodar `docs/BENCHMARK.md` e comparar tokens por tarefa aceita.

Metas de referência (propostas, ainda não medidas): contexto base de ~23,5 KB para ≤8 KB; skills 80 → ≤36; agentes 11 → 6; personas 9 → 2; CLIs ~25 → 1 entrada. A redução real de tokens só vale o que o benchmark mostrar.
