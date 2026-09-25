---
name: spec-driven
description: "Workflow de Spec-Driven Development: especificação executável (Gherkin BDD) como fonte da verdade antes de qualquer código."
---
# Spec-Driven Development Workflow (SDD)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `navigator` elabora Especificação Formal (`SPEC-NNN.md` com RFC e Cenários Gherkin) → **User Approval Gate (Confirmação Explícita da Spec)** → `test-guardian` converte Gherkin em Testes Automatizados (RED) → `builder` implementa código estrito (GREEN) → `refactor-warden` & `diff-simplifier-review` → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Persistência em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → `release-gatekeeper`

## Guidelines
- **Zero Vibe Coding:** Nenhuma linha de código de produção é autorizada sem que o arquivo `SPEC-NNN.md` tenha sido gerado e explicitamente aprovado pelo usuário.
- **Isolamento via Git Worktree:** Recomenda-se executar a implementação em worktree dedicado via `agy-worktree --create <spec-id>`.
- **Fidelidade 1:1:** Cada cenário `Given / When / Then` da especificação DEVE possuir um teste correspondente implementado pelo `test-guardian`.
- **Spec Sincronizada:** Ao final da entrega, a especificação é arquivada e versionada em conjunto com o código.
