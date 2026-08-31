---
name: bugfix
description: "Workflow obrigatório para correção de bugs com debugging sistemático, investigação de causa raiz e proibição estrita de workarounds."
---
# Bugfix Workflow

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → **Systematic Debugging (4 Fases: Investigação de Causa Raiz → Análise de Padrões → Hipótese → Teste RED)** → **No-Workarounds Check** → builder → GREEN → full suite → **Code Deslop Review** → refactor → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` & `lesson-learned` pelo `archivist`** → release

## Diretrizes Inegociáveis
1. **Passo 0 & Auto-Onboarding:**
   - Inicia obrigatoriamente lendo `PROJECT_MEMORY.md` e aplicando lições aprendidas (`Gotchas [L-NNN]`). Se for um projeto novo ou descompassado, executa o Auto-Onboarding inicial.
2. **Lei de Ferro do Debugging (`systematic-debugging`):**
   - É expressamente proibido propor ou escrever código de correção antes de investigar a causa raiz exata e rastrear o fluxo de dados até a fonte.
3. **Proibição de Remendos (`no-workarounds`):**
   - A correção deve atuar na fonte do problema. É proibido mascarar erros com `as any`, `@ts-ignore`, catches vazios ou sleeps arbitrários.
4. **Ciclo TDD Estrito:**
   - O teste de regressão DEVE ser criado e comprovadamente estar no estado **RED** antes de qualquer linha de produção ser alterada.
   - O `builder` DEVE recusar a implementação se o estado anterior não contiver a evidência real do teste falhando.
5. **A Regra dos 3 Fixes:**
   - Se 3 tentativas consecutivas de correção falharem, pare e questione a arquitetura antes de tentar qualquer novo remendo.
6. **Hard-Enforced Auto-Sync & Lições Aprendidas:**
   - Ao concluir a correção (**GREEN**), o `archivist` DEVE fisicamente persistir a atualização no `.agents/memory/PROJECT_MEMORY.md` e registrar a lição aprendida (`lesson-learned [L-NNN]`) em disco antes de finalizar.
