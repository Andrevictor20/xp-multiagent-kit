---
name: small
description: "Workflow para alterações pequenas (pequeno bugfix, refatoração)."
---
# Small Workflow (L1)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator → test-guardian RED → builder GREEN → test-guardian GREEN → refactor → Passo Final: archivist (Auto-Sync obrigatório de `.agents/memory/PROJECT_MEMORY.md`) → release

## Guidelines
- **Passo 0:** Leitura proativa da memória (com Auto-Onboarding se necessário).
- **TDD:** Exige ciclo RED/GREEN verificado com comandos reais de teste.
- **Qualidade:** Exige validação antes de liberar.
- **Zero-Prompt Auto-Sync:** Sincronização concisa e automática em `.agents/memory/PROJECT_MEMORY.md` pelo `archivist` ao finalizar.
