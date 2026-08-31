---
name: incident
description: "Workflow rápido para mitigação de incidentes em produção."
---
# Incident Workflow

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → detect → stop rollout → rollback/mitigate → verify recovery → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` com incidente & lição aprendida `[L-NNN]` pelo `archivist`**

## Guidelines
- Prioridade máxima: restaurar disponibilidade.
- TDD é obrigatório para o fix definitivo pós-incidente, mas o rollback pode e deve ser instantâneo se suportado pelo pipeline.
- **Hard-Enforced Auto-Sync:** O `archivist` DEVE obrigatoriamente persistir em disco o incidente, a mitigação e a lição aprendida na seção de Gotchas & Hurdles do `.agents/memory/PROJECT_MEMORY.md`.
