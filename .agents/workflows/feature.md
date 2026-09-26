---
name: feature
description: "Workflow adaptativo para novas funcionalidades e endpoints."
---
# Feature Workflow (L2)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator → specialized analysis → security/design/data as applicable → acceptance criteria → TDD RED → builder GREEN → integration validation → UI validation if applicable → refactor → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → release

## Guidelines
- Workflow primário para a maior parte das entregas.
- **Passo 0 & Auto-Onboarding:** O fluxo inicia lendo `.agents/memory/PROJECT_MEMORY.md`. Se o arquivo estiver ausente ou desatualizado em relação ao projeto atual, roda o Auto-Onboarding autônomo.
- **TDD Enforcement & Targeted Testing:** É PROIBIDO avançar para a fase de implementação no Builder sem um teste de aceitação ou teste unitário configurado para falhar. O Builder exige um Handoff com `tests.status = RED` e uma amostra de `tests.output_snippet`. Execute **apenas os testes da função ou módulo sob desenvolvimento** (ex: `python3 -m unittest tests/test_<modulo>.py`); a suíte completa de regressão do projeto é reservada exclusivamente para o release gatekeeper final.
- **Hard-Enforced Memory Auto-Sync:** Ao concluir a implementação e os testes, o `archivist` DEVE fisicamente persistir a atualização no `.agents/memory/PROJECT_MEMORY.md` (com nova feature, arquivos tocados, status de testes reais e backlog atualizado) antes de qualquer resposta final ou liberação de PR/release.
