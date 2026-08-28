---
name: incident
description: "Workflow rápido para mitigação de incidentes em produção."
---
# Incident Workflow

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → detect → stop rollout → rollback/mitigate → verify recovery → Passo Final: archivist (Auto-Sync obrigatório de `PROJECT_MEMORY.md` com incidente & lição aprendida `[L-NNN]`)

## Guidelines
- Prioridade máxima: restaurar disponibilidade.
- TDD é obrigatório para o fix definitivo pós-incidente, mas o rollback pode e deve ser instantâneo se suportado pelo pipeline.
- **Auto-Sync:** O `archivist` documenta o incidente, mitigação e a lição aprendida na seção de Gotchas & Hurdles do `PROJECT_MEMORY.md`.
