---
name: spec-driven
description: "Workflow ATDD/BDD/SbE/TDD completo: especificação executável com Acceptance Criteria, Specification by Example e Gherkin como fonte da verdade."
---
# Spec-Driven Development Workflow (SDD) — ATDD/BDD Expandido

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `navigator` elabora Especificação Formal (`SPEC-NNN-ATDD.md` com Acceptance Criteria, Specification by Example Tables e Cenários Gherkin) → **⏸️ User Approval Gate (Confirmação Explícita da Spec — Stop Gate Humano)** → `test-guardian` converte Acceptance Criteria + SbE Tables em Acceptance Tests Parametrizados (RED) → `test-guardian` decompõe em Integration e Unit Tests (RED) → `builder` implementa código estrito (GREEN) → `refactor-warden` & `diff-simplifier-review` → `conformance-tracker` gera **Conformance Report** (rastreabilidade AC → testes → status) → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Persistência em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → `release-gatekeeper`

## Guidelines
- **Zero Vibe Coding:** Nenhuma linha de código de produção é autorizada sem que o arquivo `SPEC-NNN-ATDD.md` tenha sido gerado e explicitamente aprovado pelo usuário.
- **Pirâmide de Especificação:** A spec DEVE conter as 3 camadas: (1) Acceptance Criteria verificáveis, (2) Specification by Example com tabelas parametrizadas e (3) Cenários Gherkin. Referência: skills `acceptance-test-driven`, `specification-by-example`.
- **Separação Humano-IA:** O humano define "o que deve acontecer" (AC + SbE). A IA implementa "como" (testes + código). Essa separação é a garantia contra "100% GREEN mas produto errado".
- **Isolamento via Git Worktree:** Recomenda-se executar a implementação em worktree dedicado via `agy-worktree --create <spec-id>`.
- **Fidelidade 1:1:** Cada Acceptance Criteria, cada linha SbE e cada cenário Gherkin DEVEM possuir testes correspondentes implementados pelo `test-guardian`.
- **Conformance Report Obrigatório:** Após GREEN, o agente gera o Conformance Report com a matriz de rastreabilidade completa. Critérios sem teste ou com teste RED bloqueiam a entrega.
- **Spec Sincronizada:** Ao final da entrega, a especificação é arquivada e versionada em conjunto com o código.
