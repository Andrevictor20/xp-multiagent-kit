# SPEC-005: Motor de Completude Exaustiva & Revisão Multi-Pass EGM (Elephant-Goldfish Model)

> **Status:** APPROVED (Pre-Authorized Multi-Agent & EGM Upgrade)
> **Risco:** L2 (Feature / Core Governance Upgrade)
> **Autor:** Antigravity (Navigator & Orchestrator)
> **Data:** 2026-10-31

---

## 1. Contexto, Problema de Negócio & Catecismo de Heilmeier (EGM Zoom-Out)

- **Objetivo / Problem Statement (O que estamos tentando fazer):**
  Transformar a governança, os agentes, os workflows, o roteador de esforço e o validador EGM do XP Multi-Agent Kit para priorizar **100% de completude no planejamento e na entrega de features acima de velocidade ou economia de turnos**, instituindo **múltiplas rodadas obrigatórias de revisão cega EGM (Elephant-Goldfish Model)** tanto no planejamento quanto no código implementado.

- **Estado Atual / How is it done today (Como isso é feito hoje e limites da prática atual):**
  Atualmente, o kit possui diretrizes em `AGENTS.md`, `token-economy.md`, `kit_constants.py`, `agy_effort_router.py` e `dynamic_effort_hook.py` que enfatizam "mínimo de turnos, agentes e steps", tetos curtos de turnos (`L1: 8`, `L2: 20`), baseline `low` para prompts de planejamento/melhoria sem palavras-chave estritas de código, e throttling automático (`_local_preflight`) que rebaixa o esforço `HIGH -> MEDIUM -> LOW` após 3 turnos. Além disso, a skill `goldfish-spec-review` não está no perfil `CORE_SKILLS`, não está acoplada aos agentes (`navigator`, `orchestrator`, `builder`, `refactor-warden`, `release-gatekeeper`) nem aos workflows (`feature.md`, `spec-driven.md`, `critical.md`), e o script `scripts/goldfish_review.py` valida apenas 6 regexes superficiais sem checar prontidão de implementação (*Zero-Decision Rule*), alternativas consideradas, ausência de placeholders (`TODO`/`TBD`/`{{...}}`) ou auditoria multi-pass de código vs. especificação.

- **Nova Abordagem / What is new (O que há de novo e por que terá sucesso):**
  1. **Mandato de Completude Acima de Velocidade (`COMPLETENESS_OVER_SPEED = True`):** Substituição da pressão por "terminar rápido em poucos turnos" pela diretriz inegociável de **Completude Exaustiva Sem Limite de Tempo**: planos e implementações jamais são truncados por orçamento de turnos, e o `_local_preflight` nunca rebaixa o `reasoningEffort` durante tarefas longas.
  2. **Protocolo Multi-Pass EGM Obrigatório (`EGM_MIN_REVIEW_PASSES = 2`):**
     - **Pass 1 (Planejamento & Spec Review):** Valida Catecismo de Heilmeier (6 dimensões), Regra de Alternativas Consideradas (`feature-spec-standard`), Regra Zero-Decision (`implementation-readiness-standard`: arquivos alvo explícitos `[Create|Modify|Delete]`, assinaturas/contratos exatos e plano de testes), Anti-Glazing e Zero Placeholders.
     - **Pass 2 (Revisão de Implementação & Codebase Details):** Audita o código implementado contra placeholders/workarounds (`TODO`, `FIXME`, `NotImplementedError`, `as any`, `@ts-ignore`) e verifica se todos os arquivos planejados existem e respeitam `< 500` linhas.
     - **Pass 3 (Auditoria de Desvio Spec-vs-Code & Rastreabilidade AC):** Confirma que 100% dos `AC-N` declarados na especificação possuem testes reais correspondentes e zero desvio de contrato.
  3. **Elevação Automática de Esforço em Planejamento e Revisão EGM:** Inclusão de vocabulário de planejamento, arquitetura, revisão e EGM em `L2_KEYWORDS` de `scripts/agy_effort_router.py`, garantindo `EFFORT_HIGH` tanto em planejamento quanto em execução L2/L3.
  4. **Exposição Global do CLI `xp-goldfish` / `agy-goldfish`:** Evolução de `scripts/goldfish_review.py` com subcomandos/flags (`--check-readiness`, `--check-code`, `--multipass`, `--json`) e instalação de binários globais em `~/.local/bin/` e shims Windows.

- **Impacto / Who cares (Quem se importa e que diferença fará):**
  Desenvolvedores e equipes que utilizam o XP Multi-Agent Kit em Antigravity, OpenCode, Cursor, Codex, Qoder e Claude terão planejamentos completos (sem decisões omitidas para adivinhação posterior) e features entregues de ponta a ponta com múltiplas revisões críticas independentes, eliminando entregas superficiais ou apressadas.

- **Riscos e Custos / Trade-offs:**
  - **Custo de Tokens e Tempo:** Múltiplas revisões EGM e manutenção de esforço `HIGH` consomem mais tempo de parede e mais tokens por feature (~100 tokens/turno adicionais no perfil `core` ao elevar `CORE_SKILLS` de 15 para 17 skills, mantendo-se dentro do invariante `12 <= len(CORE_SKILLS) <= 20` de `tests/test_skill_profiles.py`). Esse trade-off é intencional e explicitamente exigido pelo usuário (*"foco em entregar as features e planejamento não importando quanto tempo demore"*).
  - **Mitigação de Ruído:** Para evitar que revisões múltiplas gerem textos prolixos ou elogios vazios, o filtro Anti-Glazing e a triagem estruturada (`[Blocker]`, `[Major]`, `[Nit]`) mantêm o foco 100% técnico, respeitando o teto de bytes de `AGENTS.md` (`<= 6000` bytes) e `PROJECT_MEMORY.md` (`<= 8192` bytes).

- **Métricas e Testes / Evaluation (Critérios de sucesso intermediários e finais):**
  - 100% dos testes unitários e de aceitação passando (`python3 -m unittest discover -s tests -p "test_*.py"`).
  - `python3 scripts/goldfish_review.py --multipass .agents/specs/SPEC-005-EGM-COMPLETENESS-ENGINE.md --code-files scripts/goldfish_review.py scripts/agy_effort_router.py scripts/kit_constants.py --test-files tests/test_egm_completeness_engine.py` retornando `exit_code == 0` e score `100.0%`.
  - `python3 scripts/skill_index.py audit` retornando `0` bloqueios de orçamento (`AGENTS.md <= 6000B`, `PROJECT_MEMORY.md <= 8192B`, todas as `SKILL.md <= 6000B`).

---

## 2. Alternativas Consideradas (EGM Feature Spec Standard)

1. **Alternativa A (Rejeitada): Apenas aumentar `TURN_BUDGET` em `kit_constants.py` sem alterar prompts, hooks ou `goldfish_review.py`.**
   - *Motivo da Rejeição:* O comportamento apressado do LLM decorre das instruções textuais em `AGENTS.md`, `dynamic_effort_hook.py`, `agy_effort_router.py` (que classificava prompts de planejamento como `L0 low` e aplicava throttle no `_local_preflight`) e da ausência de gates mecânicos de revisão EGM nos agentes e workflows.
2. **Alternativa B (Rejeitada): Tornar `goldfish-spec-review` obrigatório apenas para tarefas L3 (Críticas).**
   - *Motivo da Rejeição:* A maioria dos planejamentos incompletos e features entregues pela metade ocorre em tarefas `L2 (Feature)` e refatorações estruturais. O protocolo EGM deve cobrir obrigatoriamente L2 e L3 (com verificação rápida de completude em L1).
3. **Alternativa C (Escolhida): Reforma Sistêmica de Completude + Motor Multi-Pass EGM (`xp-goldfish` / `agy-goldfish`) + Integração em Agentes, Workflows, Perfis de Skills e Router de Esforço.**
   - *Motivo da Escolha:* Ataca a causa raiz em todas as camadas (governança textual, injeção de hook por turno, classificador de esforço, templates ATDD, agentes especialistas e validador CLI automatizado).

---

## 3. Plano de Implementação Zero-Decision (EGM Implementation Readiness)

| Arquivo Alvo | Operação | Mudança Exata e Contratos / Assinaturas |
| :--- | :--- | :--- |
| `scripts/kit_constants.py` | `Modify` | Adicionar constantes `COMPLETENESS_OVER_SPEED = True`, `EGM_MIN_REVIEW_PASSES = 2`, `ZERO_DECISION_PLANNING_REQUIRED = True`; ajustar `TURN_BUDGET = {"L0": 5, "L1": 25, "L2": 100, "L3": None}` mantendo invariante `L0 < L1 < L2`. |
| `scripts/goldfish_review.py` | `Modify` | Preservar `check_anti_glazing(content: str) -> List[str]` e `validate_heilmeier_compliance(content: str) -> Dict[str, Any]`; adicionar `check_placeholders(content: str) -> List[str]`, `validate_implementation_readiness(content: str) -> Dict[str, Any]` (retornando chaves `compliant`, `score`, `checks`, `missing` com `heilmeier_catechism`, `alternatives_considered`, `zero_decision_target_files`, `acceptance_criteria`, `no_placeholders`, `anti_glazing`), `audit_code_completeness(code_paths: List[Path]) -> Dict[str, Any]`, `audit_spec_code_drift(spec_content: str, code_paths: List[Path], test_paths: List[Path]) -> Dict[str, Any]` e `run_multipass_egm_review(spec_path: Path, code_paths: Optional[List[Path]] = None, test_paths: Optional[List[Path]] = None) -> Dict[str, Any]` (retornando `passes_completed`, `pass1_spec`, `pass2_code`, `pass3_drift`, `overall_compliant`); suportar CLI `--multipass`, `--code-files`, `--test-files`, `--json`. |
| `scripts/agy_effort_router.py` | `Modify` | Expandir `L2_KEYWORDS` com termos de planejamento, revisão, EGM e melhoria completa (`planejamentos?`, `planejar`, `planos?`, `arquitetura`, `especifica[çc][ãa]o`, `specs?`, `egm`, `goldfish`, `revis[ãa]o`, `revis[õo]es`, `melhorar`, `melhorias?`, `features?`); ajustar `get_canonical_model_for_task` para retornar `EFFORT_HIGH` em L2 planning; desativar downgrade de esforço por contagem de turnos no bloco 9a (`_local_preflight`) preservando o bloco 9b (`rolling_5h > 80.0`). |
| `tests/test_agy_effort_router.py` | `Modify` | Atualizar asserção em `test_canonical_model_for_code_and_planning` (linha 184) para esperar `("Gemini Pro", EFFORT_HIGH)` em `LEVEL_L2_FEATURE` com `is_planning=True`. |
| `scripts/hooks/dynamic_effort_hook.py` | `Modify` | Atualizar `ephemeralMessage` em `handle_pre_invocation` para instruir completude total sobre velocidade e revisões multi-pass EGM em modos `HIGH` e `MEDIUM`. |
| `scripts/skill_profiles.py` | `Modify` | Incluir `goldfish-spec-review` e `spec-driven-development` em `CORE_SKILLS` e `goldfish-spec-review` em `SKILL_DESCRIPTIONS`. |
| `scripts/antigravity_multiagent.py` | `Modify` | Adicionar suporte a `egm_review_passes` (default `>= 2`) na validação/execução de missão e incluir resumo de Revisões Multi-Pass EGM no `mission-report.md`. |
| `scripts/kit_installer.py`, `scripts/install-global.sh`, `scripts/windows_support.py`, `scripts/host_adapters.py` | `Modify` | Registrar binários `xp-goldfish` e `agy-goldfish` apontando para `scripts/goldfish_review.py`; atualizar dispatcher global com diretriz de Completude Exaustiva e Revisão Multi-Pass EGM. |
| `AGENTS.md`, `.agents/policies/token-economy.md`, `.agents/policies/atdd-bdd-tdd.md` | `Modify` | Substituir viés de velocidade por **Completeness Over Speed & Multi-Pass EGM Review**; evoluir o Self-Audit pré-resposta mantendo `AGENTS.md <= 6000` bytes. |
| `.agents/agents/{orchestrator,navigator,builder,refactor-warden,release-gatekeeper}/agent.md` | `Modify` | Acoplar skill `goldfish-spec-review` e tornar obrigatórias as passadas de revisão EGM no planejamento e pós-implementação. |
| `.agents/workflows/{feature,spec-driven,critical}.md` e `.agents/templates/SPEC-NNN-ATDD.md` | `Modify` | Inserir as 3 passadas EGM no fluxo de trabalho e atualizar o template de especificação com Catecismo de Heilmeier, Alternativas e Plano Zero-Decision. |
| `tests/test_egm_completeness_engine.py` | `Create` | Testes unitários e de aceitação cobrindo `AC-1` a `AC-6`. |

---

## 4. Acceptance Criteria (ATDD)

### AC-1: Validação de Prontidão Zero-Decision, Alternativas e Anti-Placeholder no EGM (`scripts/goldfish_review.py`)
- **Dado:** Um documento de especificação submetido ao `scripts/goldfish_review.py`.
- **Quando:** A função `validate_implementation_readiness` e `check_placeholders` forem executadas.
- **Então:** Deve validar a presença de Alternativas Consideradas, Plano Zero-Decision (arquivos alvo com operação `Create`/`Modify`/`Delete`), Critérios de Aceitação (`AC-N`) e rejeitar documentos contendo placeholders inacabados (`TODO`, `TBD`, `FIXME`, `{{...}}`).
- **Métrica:** Retornar `compliant == True` e `score == 100.0` para especificações completas e `compliant == False` com lista detalhada de bloqueios para especificações incompletas.

### AC-2: Motor de Revisão Multi-Pass EGM (Spec + Código + Drift)
- **Dado:** Uma especificação aprovada, arquivos de código implementados e arquivos de teste.
- **Quando:** `run_multipass_egm_review` (ou `xp-goldfish --multipass`) for executado.
- **Então:** Deve executar **Pass 1** (Heilmeier + Anti-Glazing + Zero-Decision Readiness), **Pass 2** (Codebase Details: existência dos arquivos planejados, respeito ao limite de `< 500` linhas, ausência de workarounds/TODOs deixados no código) e **Pass 3** (Spec-vs-Code Drift: cobertura de 100% dos `AC-N` nos testes).
- **Métrica:** Retornar estrutura com `passes_completed == 3`, `overall_compliant == True` quando íntegro, ou bloquear (`overall_compliant == False`) quando houver código faltante, placeholder ou AC sem teste.

### AC-3: Prioridade de Completude e Elevação Automática de Esforço para Planejamento e EGM (`scripts/agy_effort_router.py`)
- **Dado:** Um prompt solicitando planejamento, melhoria arquitetural ou revisão EGM (ex.: *"Melhorar o kit multiagent - planejamentos completos e múltiplas revisões EGM"*), ou uma sessão longa com múltiplos turnos (`turns >= 3`).
- **Quando:** `classify_task_effort` e `get_canonical_model_for_task` forem invocados.
- **Então:** Deve classificar a tarefa como `L2 (Feature)` ou superior com esforço `high` (`EFFORT_HIGH`), retornar `EFFORT_HIGH` também quando `is_planning=True` em L2/L3, e jamais rebaixar o esforço via `_local_preflight` apenas por número de turnos.
- **Métrica:** `decision.effort == "high"` e `decision.throttled == False`.

### AC-4: Inclusão de `goldfish-spec-review` e `spec-driven-development` em `CORE_SKILLS`
- **Dado:** O gerenciador de perfis de skills (`scripts/skill_profiles.py`).
- **Quando:** O perfil `core` (ou `backend`/`frontend`) for consultado.
- **Então:** As skills `goldfish-spec-review` e `spec-driven-development` devem estar presentes em `CORE_SKILLS` e catalogadas em `SKILL_DESCRIPTIONS`.
- **Métrica:** `"goldfish-spec-review" in CORE_SKILLS` e `"spec-driven-development" in CORE_SKILLS`.

### AC-5: Governança Multi-Pass EGM em `AGENTS.md`, Agentes, Workflows e `AntigravityMissionEngine`
- **Dado:** Os arquivos de governança (`AGENTS.md`, `kit_constants.py`, `navigator/agent.md`, `orchestrator/agent.md`, `refactor-warden/agent.md`, `release-gatekeeper/agent.md`, `feature.md`) e o motor `AntigravityMissionEngine`.
- **Quando:** Inspecionados e executados.
- **Então:** `COMPLETENESS_OVER_SPEED` deve ser `True`, `EGM_MIN_REVIEW_PASSES >= 2`, `AGENTS.md` deve conter a regra de Completude Acima de Velocidade e Revisão Multi-Pass EGM respeitando `<= 6000` bytes, e `AntigravityMissionEngine` deve registrar as passadas de revisão EGM no relatório de missão.
- **Métrica:** Auditoria de orçamento `audit_context_budget` sem bloqueios (`blocking == False`) e relatório de missão contendo seção de revisão EGM.

### AC-6: Disponibilidade Global dos Binários `xp-goldfish` e `agy-goldfish`
- **Dado:** O instalador do kit (`scripts/kit_installer.py`, `scripts/install-global.sh`, `scripts/windows_support.py`).
- **Quando:** A instalação global e o diagnóstico `KitDoctor` forem executados.
- **Então:** `xp-goldfish` e `agy-goldfish` devem estar registrados em `SHIM_COMMANDS`, `essential_bins` e instalados em `~/.local/bin/`.
- **Métrica:** `xp-goldfish` e `agy-goldfish` presentes e executáveis com código de saída 0.

---

## 5. Specification by Example (SbE)

| Caso | Entrada / Artefato | Pass 1 (Spec/Heilmeier/Readiness) | Pass 2 (Codebase Details) | Pass 3 (Spec Drift / ACs) | Resultado Esperado | Código |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SbE-1: Entrega Completa** | Spec completa + código limpo + testes cobrindo AC-1..AC-6 | `PASS (100%)` | `PASS` | `PASS (6/6 ACs)` | `COMPLIANT (3/3 passes)` | `0` |
| **SbE-2: Spec com Placeholders** | Spec contendo `{{valor}}` ou `TODO: definir schema` | `FAIL (Placeholders)` | `SKIP/PASS` | `FAIL` | `NON-COMPLIANT (Blocker)` | `2` |
| **SbE-3: Plano Vagamente Definido** | Spec sem seção de Alternativas ou sem tabela de arquivos `[Create/Modify]` | `FAIL (Zero-Decision)` | `PASS` | `PASS` | `NON-COMPLIANT (Blocker)` | `2` |
| **SbE-4: Código Incompleto / Workaround** | Código implementado contém `NotImplementedError` ou `@ts-ignore` | `PASS` | `FAIL (Code Incomplete)` | `PASS` | `NON-COMPLIANT (Blocker)` | `2` |
| **SbE-5: Desvio Spec-vs-Testes** | Spec declara `AC-1` a `AC-4`, mas testes só cobrem `AC-1` e `AC-2` | `PASS` | `PASS` | `FAIL (Missing AC-3, AC-4)` | `NON-COMPLIANT (Blocker)` | `2` |
| **SbE-6: Prompt de Planejamento** | Prompt `"Melhorar planejamento e fazer múltiplas revisões EGM"` | Classificado `L2 (Feature)` | Esforço `HIGH` | Sem throttle por turnos | `EFFORT_HIGH` | `0` |

---

## 6. Cenários de Aceite (Gherkin BDD)

```gherkin
Feature: Motor de Completude Exaustiva e Revisão Multi-Pass EGM

  Scenario: Auditoria Multi-Pass aprova especificação Zero-Decision e código completo
    Given uma especificação ATDD contendo Catecismo de Heilmeier, Alternativas e Plano Zero-Decision
    And arquivos de código implementados sem placeholders e com menos de 500 linhas
    And testes automatizados cobrindo todos os critérios AC-1 a AC-6
    When o validador executa a revisão multi-pass EGM (3 passadas)
    Then todas as 3 passadas retornam status PASS
    And o veredito final é COMPLIANT com código de saída 0

  Scenario: Auditoria Multi-Pass bloqueia planejamento incompleto ou código com atalhos
    Given uma especificação com decisões em aberto ("TBD") ou código com "TODO"
    When o validador executa a revisão multi-pass EGM
    Then a revisão identifica findings de severidade Blocker
    And bloqueia a liberação com código de saída 2

  Scenario: Roteador de esforço prioriza profundidade máxima em planejamento sem throttling
    Given um prompt de melhoria de planejamento e revisão EGM em sessão com mais de 5 turnos
    When o classificador de esforço avalia a tarefa
    Then o nível de risco é L2 (Feature) e o esforço é HIGH
    And o esforço não sofre rebaixamento por contagem de turnos
```

---

## 7. Invariantes & Propriedades

- Nenhuma especificação aprovada pode conter marcadores `{{...}}`, `TODO`, `TBD` ou seções Heilmeier vazias.
- Nenhum plano de implementação pode omitir a lista explícita de arquivos e operações (`Create`, `Modify`, `Delete`).
- O orçamento de contexto base (`AGENTS.md <= 6000` bytes e `PROJECT_MEMORY.md <= 8192` bytes) jamais pode ser violado.
- Tarefas em andamento nunca têm seu `reasoningEffort` reduzido automaticamente pelo número de turnos decorridos.

---

## 8. Conformance Tracking

| # | Acceptance Criteria | Test File | Test Name | Status |
|---|---|---|---|---|
| AC-1 | Validação Zero-Decision, Alternativas e Anti-Placeholder | `tests/test_egm_completeness_engine.py` | `test_ac1_zero_decision_and_placeholder_validation` | ✅ PASS |
| AC-2 | Motor de Revisão Multi-Pass EGM (3 Passadas) | `tests/test_egm_completeness_engine.py` | `test_ac2_multipass_egm_review_engine` | ✅ PASS |
| AC-3 | Prioridade de Completude e Esforço HIGH em Planejamento sem Throttle | `tests/test_egm_completeness_engine.py` | `test_ac3_planning_effort_high_and_no_turn_throttle` | ✅ PASS |
| AC-4 | Inclusão de `goldfish-spec-review` em `CORE_SKILLS` | `tests/test_egm_completeness_engine.py` | `test_ac4_goldfish_in_core_skills` | ✅ PASS |
| AC-5 | Governança Multi-Pass EGM e Orçamento de Contexto | `tests/test_egm_completeness_engine.py` | `test_ac5_governance_and_mission_egm_passes` | ✅ PASS |
| AC-6 | Binários Globais `xp-goldfish` e `agy-goldfish` | `tests/test_egm_completeness_engine.py` | `test_ac6_goldfish_cli_binaries_registered` | ✅ PASS |
