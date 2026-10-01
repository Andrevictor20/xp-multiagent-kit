---
name: feature
description: "Workflow adaptativo para novas funcionalidades e endpoints com ATDD/BDD integrado."
---
# Feature Workflow (L2)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → `navigator` formula **Acceptance Criteria + Specification by Example + Cenários Gherkin** (template `SPEC-NNN-ATDD.md`) → specialized analysis → security/design/data as applicable → **⏸️ Stop Gate: Aprovação Humana da Spec** → `test-guardian` converte Acceptance Criteria em Acceptance Tests (RED) → `test-guardian` decompõe em Unit/Integration Tests (RED) → `builder` implementa (GREEN) → integration validation → UI validation if applicable → `refactor-warden` → `conformance-tracker` gera **Conformance Report** (N/N critérios) → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → release

## Guidelines
- Workflow primário para a maior parte das entregas.
- **Passo 0 & Auto-Onboarding:** O fluxo inicia lendo `.agents/memory/PROJECT_MEMORY.md`. Se o arquivo estiver ausente ou desatualizado em relação ao projeto atual, roda o Auto-Onboarding autônomo.
- **ATDD/BDD Obrigatório (Pirâmide de Especificação):** Antes de qualquer código, o `navigator` DEVE formular Acceptance Criteria verificáveis, tabelas de Specification by Example e cenários Gherkin. O humano DEVE aprovar a spec no Stop Gate antes de prosseguir. Isso garante a separação: humano define "o que deve acontecer", IA implementa "como". Referência: policy `atdd-bdd-tdd.md`, skills `acceptance-test-driven` e `specification-by-example`.
- **TDD Enforcement & Targeted Testing:** É PROIBIDO avançar para a fase de implementação no Builder sem que os Acceptance Tests e Unit Tests estejam configurados para falhar (RED). O Builder exige um Handoff com `tests.status = RED` e uma amostra de `tests.output_snippet`. Execute **apenas os testes da função ou módulo sob desenvolvimento** (ex: `python3 -m unittest tests/test_<modulo>.py`); a suíte completa de regressão do projeto é reservada exclusivamente para o release gatekeeper final.
- **Conformance Report Obrigatório:** Após todos os testes estarem GREEN, o agente DEVE gerar o Conformance Report rastreando cada Acceptance Criteria → teste correspondente → status. Entregas com critérios não cobertos ou RED são BLOQUEADAS.
- **Hard-Enforced Memory Auto-Sync:** Ao concluir a implementação e os testes, o `archivist` DEVE fisicamente persistir a atualização no `.agents/memory/PROJECT_MEMORY.md` (com nova feature, arquivos tocados, status de testes reais, Conformance Report resumido e backlog atualizado) antes de qualquer resposta final ou liberação de PR/release.
