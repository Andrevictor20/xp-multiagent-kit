# SPEC-NNN: {{FEATURE_TITLE}}

> **Status:** DRAFT
> **Risco:** L2
> **Autor:** Antigravity (Navigator)
> **Data:** {{DATE}}

---

## 1. Contexto, Problema de Negócio & Catecismo de Heilmeier (EGM Zoom-Out)

- **Objetivo / Problem Statement (O que estamos tentando fazer):**
  [Descreva o problema de negócio ou engenharia sem jargões]

- **Estado Atual / How is it done today (Como isso é feito hoje e limites da prática atual):**
  [Explique o funcionamento atual e seus gargalos/limitações]

- **Nova Abordagem / What is new (O que há de novo e por que terá sucesso):**
  [Detalhe a inovação arquitetural e o mecanismo técnico]

- **Impacto / Who cares (Quem se importa e que diferença fará):**
  [Impacto mensurável para usuários, sistema e operação]

- **Riscos e Custos / Trade-offs:**
  [Riscos técnicos, custos de recursos/latência/tokens e estratégias de mitigação]

- **Métricas e Testes / Evaluation (Critérios de sucesso intermediários e finais):**
  [Métricas determinísticas e comandos de verificação]

---

## 2. Alternativas Consideradas (EGM Feature Spec Standard)

1. **Alternativa A (Rejeitada):** [Descrição e motivo técnico da rejeição]
2. **Alternativa B (Rejeitada):** [Descrição e motivo técnico da rejeição]
3. **Alternativa C (Escolhida):** [Descrição e justificativa técnica da escolha]

---

## 3. Plano de Implementação Zero-Decision (EGM Implementation Readiness)

| Arquivo Alvo | Operação (`Create` \| `Modify` \| `Delete`) | Mudança Exata, Assinaturas e Contratos |
| :--- | :--- | :--- |
| `src/...` | `Modify` | [Assinaturas exatas, schemas e regras sem deixar decisões em aberto] |
| `tests/...` | `Create` | [Casos de teste cobrindo AC-1..AC-N] |

---

## 4. Acceptance Criteria (ATDD)

### AC-1: [Título descritivo]
- **Dado:** [pré-condição]
- **Quando:** [ação do usuário ou sistema]
- **Então:** [resultado esperado verificável]
- **Métrica:** [status code, campo, evento, threshold]

### AC-2: [Título descritivo]
- **Dado:** [pré-condição]
- **Quando:** [ação]
- **Então:** [resultado]
- **Métrica:** [como medir]

---

## 5. Specification by Example (SbE)

| Input A | Input B | Pré-condição | Resultado Esperado | Código | Motivo |
|---------|---------|--------------|--------------------|--------|--------|
| val_1   | val_2   | ativo        | sucesso            | 200    | Happy Path |
| inval   | val_2   | ativo        | erro_validacao     | 422    | Edge Case |

---

## 6. Cenários de Aceite (Gherkin BDD)

```gherkin
Feature: [Nome da funcionalidade]

  Scenario: [Cenário de sucesso principal]
    Given [pré-condição]
    When [ação]
    Then [resultado esperado]

  Scenario: [Cenário de erro / edge case]
    Given [pré-condição]
    When [ação que deve falhar]
    Then [resultado de erro esperado]
```

---

## 7. Invariantes & Propriedades

- [Invariante 1: propriedade que nunca deve ser violada]
- [Invariante 2: idempotência, segurança e limites]

---

## 8. Conformance Tracking & Multi-Pass EGM Audit

| # | Acceptance Criteria | Test File | Test Name | Status |
|---|---|---|---|---|
| AC-1 | [descrição] | `tests/...` | `test_ac1_...` | ⬜ PENDING |
| AC-2 | [descrição] | `tests/...` | `test_ac2_...` | ⬜ PENDING |

- **EGM Pass 1 (Spec & Zero-Decision Readiness):** ⬜ PENDING
- **EGM Pass 2 (Codebase Details & Completeness):** ⬜ PENDING
- **EGM Pass 3 (Spec-vs-Code Drift & Conformance):** ⬜ PENDING
