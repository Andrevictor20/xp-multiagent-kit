---
name: small
description: "Workflow para alterações pequenas (pequeno bugfix, refatoração)."
---
# Small Workflow (L1)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator → test-guardian RED → builder GREEN → test-guardian GREEN → refactor → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → release

## Guidelines
- **Passo 0:** Leitura proativa da memória (com Auto-Onboarding se necessário).
- **TDD & Targeted Testing:** Exige ciclo RED/GREEN verificado com comandos reais de teste, direcionados **exclusivamente ao arquivo ou módulo modificado** (ex: `python3 -m unittest tests/test_<modulo>.py`). É proibido rodar a suíte inteira indiscriminadamente.
- **Qualidade:** Exige validação antes de liberar.
- **Hard-Enforced Auto-Sync:** O `archivist` DEVE obrigatoriamente persistir em disco a alteração, arquivos tocados e evidência real no `.agents/memory/PROJECT_MEMORY.md`. A entrega é bloqueada sem essa gravação física.
