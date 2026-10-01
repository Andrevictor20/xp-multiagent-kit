---
name: small
description: "Workflow para alterações pequenas (pequeno bugfix, refatoração) com Acceptance Criteria informais."
---
# Small Workflow (L1)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator (Acceptance Criteria informais em bullets) → builder (RED → GREEN → refactor no mesmo contexto) → Conformance resumido (1-2 linhas) → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → release-gatekeeper

## Colapso de Agentes (E3)
`navigator` → `builder` → `archivist` → `release-gatekeeper`. O ciclo RED/GREEN e a refatoração ocorrem **dentro do contexto do `builder`**: trocar de agente a cada fase cria um contexto novo que relê spec, memória e código. `test-guardian` e `refactor-warden` só entram se houver suspeita de teste burlado ou dívida estrutural.

## Orçamento
- **Máximo de 8 chamadas de ferramenta** (`TURN_BUDGET["L1"]` em `scripts/kit_constants.py`).
- Chamadas independentes no mesmo turno (batching); declarar o plano se o orçamento apertar.
- Leitura de arquivo ≤ 800 linhas é feita **inteira em uma chamada**; proibido fatiar.
- Testes e comandos via `agy-run` / `agy-evidence run` (log completo fica em `.agents/runtime/evidence/`, só o resumo vai para o `walkthrough.md`).

## Guidelines
- **Passo 0:** Leitura proativa da memória (com Auto-Onboarding se necessário).
- **Acceptance Criteria Informais (ATDD Light):** O `navigator` registra em bullets o comportamento esperado verificável (ex: "sacar valor acima do saldo deve rejeitar e não alterar o saldo"). Tabelas SbE e cenários Gherkin são **opcionais** — recomendados apenas quando a regra tem mais de 2 cenários possíveis. Não há Stop Gate formal, mas os bullets devem aparecer no handoff.
- **TDD & Targeted Testing:** Exige ciclo RED/GREEN verificado com comandos reais de teste, direcionados **exclusivamente ao arquivo ou módulo modificado** (ex: `python3 -m unittest tests/test_<modulo>.py`). É proibido rodar a suíte inteira indiscriminadamente.
- **Conformance Resumido:** Ao fechar, declarar em 1-2 linhas se cada Acceptance Criteria informal possui teste correspondente GREEN (ex: "Conformance: 3/3 critérios cobertos e GREEN"). Critério sem teste impede a entrega. Quando houver spec formal, usar `agy-conformance --spec ... --tests ...` em vez de escrever a matriz em prosa.
- **Escala para L2:** Se durante a execução surgirem múltiplas regras de negócio, edge cases conflitantes ou mudança de contrato público, RECLASSIFIQUE para L2 (`feature.md`) e aplique a Pirâmide de Especificação completa com Stop Gate.
- **Qualidade:** Exige validação antes de liberar.
- **Hard-Enforced Auto-Sync:** O `archivist` DEVE obrigatoriamente persistir em disco a alteração, arquivos tocados e evidência real no `.agents/memory/PROJECT_MEMORY.md`. A entrega é bloqueada sem essa gravação física.
