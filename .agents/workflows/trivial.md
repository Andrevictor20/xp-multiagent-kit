---
name: trivial
description: "Workflow mínimo para alterações triviais (typo, doc, css)."
---
# Trivial Workflow (L0)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → orchestrator → builder → validation → Passo Final: archivist (Auto-Sync rápido de `PROJECT_MEMORY.md`)

## Guidelines
- Não executar pipeline completo de TDD/Segurança.
- Foco em resolver a tarefa com o mínimo de passos e tokens.
- **Auto-Sync:** O `archivist` registra a alteração concisa no `PROJECT_MEMORY.md` automaticamente.
