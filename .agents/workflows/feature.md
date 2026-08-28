---
name: feature
description: "Workflow adaptativo para novas funcionalidades e endpoints."
---
# Feature Workflow (L2)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator → specialized analysis → security/design/data as applicable → acceptance criteria → TDD RED → builder GREEN → integration validation → UI validation if applicable → refactor → Passo Final: archivist (Auto-Sync obrigatório de `.agents/memory/PROJECT_MEMORY.md` e Handoff) → release

## Guidelines
- Workflow primário para a maior parte das entregas.
- **Passo 0 & Auto-Onboarding:** O fluxo inicia lendo `.agents/memory/PROJECT_MEMORY.md`. Se o arquivo estiver ausente ou desatualizado em relação ao projeto atual, roda o Auto-Onboarding autônomo.
- **TDD Enforcement:** É PROIBIDO avançar para a fase de implementação no Builder sem um teste de aceitação ou teste unitário configurado para falhar. O Builder exige um Handoff com `tests.status = RED` e uma amostra de `tests.output_snippet`.
- **Zero-Prompt Memory Auto-Sync:** Ao concluir a implementação e os testes, o `archivist` atualiza automaticamente o `PROJECT_MEMORY.md` com a nova feature, arquivos tocados e evidência de testes reais antes da finalização, sem esperar pedido do usuário.
