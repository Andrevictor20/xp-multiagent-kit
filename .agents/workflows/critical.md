---
name: critical
description: "Workflow crítico para mudanças arquiteturais, infraestrutura ou auth."
---
# Critical Workflow (L3)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator → codebase mapping → architecture/domain analysis → threat model → database/API/design review → acceptance criteria → TDD RED → builder → integration/E2E → security testing → performance/availability if relevant → refactor → CI/security gate → Passo Final: archivist (Auto-Sync obrigatório de `PROJECT_MEMORY.md`, ADRs & Gotchas) → staging → observability window → production → post-release verification

## Guidelines
- **Passo 0 & Auto-Onboarding:** Carrega o contexto e histórico antes de mapear impacto arquitetural.
- Análise minuciosa e aprovação em cada fase.
- Passagem obrigatória por Threat Model e Revisão Arquitetural.
- **Zero-Prompt Auto-Sync:** Registro obrigatório de ADRs, Gotchas e sincronização detalhada em `.agents/memory/PROJECT_MEMORY.md` pelo `archivist` ao finalizar.
