---
name: critical
description: "Workflow crítico para mudanças arquiteturais, infraestrutura ou auth, com Pirâmide de Especificação ATDD/BDD integral, Stop Gate e Conformance Report."
---
# Critical Workflow (L3)

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) [com Auto-Onboarding se não inicializado/divergente] → navigator → codebase mapping → architecture/domain analysis → threat model → database/API/design review → **Pirâmide de Especificação integral: Acceptance Criteria + Specification by Example + Cenários Gherkin (`SPEC-NNN-ATDD.md`)** → **⏸️ Stop Gate: Aprovação Humana da Spec** → `test-guardian` converte em Acceptance Tests (RED) → decompõe em Integration/Unit Tests (RED) → builder (GREEN) → integration/E2E → security testing → performance/availability if relevant → refactor → `conformance-tracker` gera **Conformance Report** (cross-reference com Threat Model) → CI/security gate → **Passo Final OBRIGATÓRIO (Hard-Enforcement Gate): Escrita Física em Disco no `.agents/memory/PROJECT_MEMORY.md` (com ADRs, Gotchas e Evidências) pelo `archivist`** → staging → observability window → production → post-release verification

## Guidelines
- **Passo 0 & Auto-Onboarding:** Carrega o contexto e histórico antes de mapear impacto arquitetural.
- **Pirâmide de Especificação Obrigatória (ATDD/BDD):** Em L3 nenhuma das camadas é opcional — Acceptance Criteria verificáveis, tabelas SbE cobrindo limites/erros/edge cases e cenários Gherkin, todos consolidados no template `SPEC-NNN-ATDD.md`. Referência: policy `atdd-bdd-tdd.md`, skills `acceptance-test-driven` e `specification-by-example`.
- **⏸️ Stop Gate Humano (Regra Anti-Self-Test):** A implementação NÃO inicia sem aprovação explícita da spec pelo humano. É proibido que a IA defina os Acceptance Criteria E os testes sem aprovação intermediária.
- **Threat Model ↔ Acceptance Criteria:** Cada ameaça STRIDE relevante (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege) DEVE gerar pelo menos um Acceptance Criteria de segurança com controle verificável e teste correspondente.
- Análise minuciosa e aprovação em cada fase.
- Passagem obrigatória por Threat Model e Revisão Arquitetural.
- **Conformance Report Obrigatório (`conformance-tracker`):** Matriz completa `AC → SbE Lines → Test File → Test Name → Status` com resumo "N/N critérios cobertos e aprovados" e cross-reference explícito com as ameaças mitigadas. Status `NON-COMPLIANT` (critério sem teste ou teste RED) BLOQUEIA staging e produção, independentemente dos demais testes passarem.
- **Evidência Real:** Todo status GREEN do Conformance Report deve ser sustentado por output nativo de execução (evidence level ≥ L1). Declarações verbais são rejeitadas (`evidence.md`).
- **Hard-Enforced Auto-Sync:** Persistência física em disco OBRIGATÓRIA de ADRs, Gotchas, arquivos modificados, spec aprovada, Conformance Report resumido e evidências comprovadas no `.agents/memory/PROJECT_MEMORY.md` antes de prosseguir para staging e produção.
