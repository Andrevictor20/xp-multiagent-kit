---
name: spec-driven-development
description: Engenharia guiada por especificação formal (SDD) com ATDD/BDD integrado.
---

# Spec-Driven Development (SDD) Skill

Esta skill governa a metodologia de **Spec-Driven Development (SDD)** no XP Multi-Agent Kit. Em vez de partir de prompts abertos ("vibe coding"), o sistema trata a **especificação estruturada e versionada como a única fonte da verdade**, tratando o código como um artefato derivado e verificável.

> **Ecossistema ATDD/BDD:** Esta skill faz parte da Pirâmide de Especificação e integra-se com:
> - **`acceptance-test-driven`:** Governa Acceptance Criteria e o contrato humano-IA.
> - **`specification-by-example`:** Transforma regras em tabelas parametrizadas de exemplos.
> - **`conformance-tracker`:** Rastreia cobertura AC → testes → status.
> - **Policy `atdd-bdd-tdd.md`:** Governança formal da Pirâmide de Especificação.

---

## 1. Princípios Fundamentais (Maturidade Nível 3)
1. **Spec as Source of Truth:** Nenhum código é gerado antes que a especificação em Markdown estruturado seja aprovada.
2. **Acceptance Criteria em Gherkin:** Todo requisito deve ser expresso em cenários `Given / When / Then` testáveis por máquina.
3. **Specification by Example:** Regras de negócio com múltiplas condições DEVEM ser acompanhadas de tabelas SbE parametrizadas.
4. **Validação Bidirecional:** A suíte de testes deve espelhar 1:1 os cenários da especificação. Se a spec mudar, a suíte de testes quebra (RED) e o código é corrigido (GREEN).
5. **Living Spec:** Especificações residem em `.agents/specs/` ou `docs/specs/` e são mantidas vivas e sincronizadas.

---

## 2. Estrutura Canônica da Especificação

Utilize o template expandido **`SPEC-NNN-ATDD.md`** (em `.agents/templates/`) que inclui:

1. **Contexto & Problema de Negócio**
2. **Acceptance Criteria (ATDD)** — critérios verificáveis com Dado/Quando/Então/Métrica
3. **Specification by Example (SbE)** — tabelas parametrizadas com edge cases
4. **Cenários de Aceite (Gherkin BDD)** — `Given / When / Then` + `Scenario Outline`
5. **Contrato de Domínio & Interfaces** — schemas, endpoints, eventos
6. **Invariantes & Propriedades** — regras que nunca podem ser violadas
7. **Conformance Tracking** — preenchido pela IA após implementação

---

## 3. Ciclo Operacional do Agente
1. **`navigator`**: Formula a especificação canônica com base no pedido do usuário, incluindo AC, SbE e Gherkin.
2. **Stop Gate (Aprovação do Usuário):** Apresenta a especificação e obtém o "De Acordo" formal.
3. **`test-guardian`**: Converte os Acceptance Criteria e tabelas SbE em testes parametrizados que falham (**RED**).
4. **`test-guardian`**: Decompõe em Integration e Unit Tests (**RED**).
5. **`builder`**: Codifica exclusivamente a lógica necessária para satisfazer os cenários da spec (**GREEN**).
6. **`conformance-tracker`**: Gera Conformance Report com rastreabilidade completa.
7. **`archivist`**: Arquiva a spec em disco e atualiza o `PROJECT_MEMORY.md`.

