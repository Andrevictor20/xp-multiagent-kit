---
name: acceptance-test-driven
description: ATDD/BDD com separação de contrato humano-IA e Pirâmide de Especificação.
---

# Acceptance Test-Driven Development (ATDD) Skill

Esta skill governa a metodologia de **Acceptance Test-Driven Development (ATDD)** no XP Multi-Agent Kit. O princípio central é a **separação explícita de responsabilidades**: o humano define *o que* deve acontecer (contrato comportamental), a IA implementa *como* (código e testes unitários).

---

## 1. Princípio Fundamental: Contrato Humano-IA

> **O humano define o contrato. A IA implementa dentro das restrições do contrato.**

### Zona do Humano (O Que)
- Intent e requisito de negócio
- Acceptance Criteria formais
- Specification by Example (tabelas parametrizadas)
- Aprovação formal da especificação (Stop Gate)
- Review final do Conformance Report

### Zona da IA (Como)
- Conversão de Gherkin em Acceptance Tests automatizados
- Decomposição em Integration e Unit Tests (TDD RED)
- Implementação do código de produção (GREEN)
- Refatoração e documentação
- Geração do Conformance Report

---

## 2. Pirâmide de Especificação (Ordem Obrigatória)

A ordem de execução é estritamente top-down — nunca se inicia pela implementação:

```text
              PRODUTO / INTENT
                     │
                     ▼
            ┌─────────────────┐
            │  ATDD / BDD     │  ← Humano define Acceptance Criteria
            │  Acceptance     │  ← Cenários Gherkin + SbE Tables
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Integration     │  ← IA decompõe em testes de fronteira
            │ Tests           │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ TDD             │  ← IA decompõe em testes unitários
            │ Unit Tests      │
            └────────┬────────┘
                     │
                     ▼
                  CÓDIGO
```

### Regra de Ativação por Nível de Risco
- **L0 (Trivial):** Dispensado — typos, docs e CSS não requerem ATDD.
- **L1 (Small):** Acceptance Criteria informais em bullet points são suficientes.
- **L2 (Feature):** ATDD formal obrigatório — Acceptance Criteria + Gherkin + Stop Gate.
- **L3 (Critical):** ATDD formal + Specification by Example + Threat Modeling integrado.

---

## 3. Estrutura dos Acceptance Criteria

Acceptance Criteria devem ser **verificáveis por máquina**, não vagos. Cada critério segue o padrão:

### Formato Canônico
```markdown
## Acceptance Criteria

### AC-1: [Título descritivo]
- **Dado:** [pré-condição]
- **Quando:** [ação]
- **Então:** [resultado esperado verificável]
- **Métrica:** [como medir: status code, campo no payload, evento emitido, etc.]

### AC-2: [Título descritivo]
...
```

### Anti-Padrões Proibidos
- ❌ "O sistema deve funcionar corretamente" — vago, não verificável.
- ❌ "A resposta deve ser rápida" — sem métrica concreta.
- ❌ "Deve ser seguro" — sem especificação de ameaça ou controle.
- ✅ "POST /users com email duplicado retorna 409 e não cria registro" — verificável.

---

## 4. Ciclo Operacional ATDD

1. **`navigator`:** Elicita o requisito e formula Acceptance Criteria + cenários Gherkin.
2. **Stop Gate (Aprovação Humana):** Apresenta a spec completa e obtém confirmação explícita.
3. **`test-guardian`:** Converte os Acceptance Criteria em Acceptance Tests automatizados (RED).
4. **`test-guardian`:** Decompõe em Integration Tests e Unit Tests (RED).
5. **`builder`:** Implementa exclusivamente a lógica necessária para satisfazer os testes (GREEN).
6. **`refactor-warden`:** Refatoração controlada mantendo todos os testes GREEN.
7. **`conformance-tracker`:** Gera Conformance Report: N/N critérios cobertos e aprovados.
8. **`archivist`:** Persiste spec, relatório e atualiza `PROJECT_MEMORY.md`.

---

## 5. Conformance Report Obrigatório

Ao final de toda entrega L2+, o agente DEVE produzir um relatório de conformidade:

```markdown
## Conformance Report — SPEC-NNN

| # | Acceptance Criteria | Test File | Status |
|---|---|---|---|
| AC-1 | Email único e válido | `tests/test_user_creation.py::test_duplicate_email` | ✅ GREEN |
| AC-2 | Senha hasheada bcrypt | `tests/test_user_creation.py::test_password_hashed` | ✅ GREEN |
| AC-3 | Evento UserCreated | `tests/test_user_events.py::test_created_event` | ✅ GREEN |
| AC-4 | DTO sem password | `tests/test_user_creation.py::test_dto_no_password` | ✅ GREEN |

**Resultado: 4/4 critérios cobertos e aprovados.**
```

### Regra de Bloqueio
- Se qualquer critério estiver com status RED ou sem teste correspondente, a entrega é **BLOQUEADA**.
- O agente NÃO pode declarar DONE com critérios pendentes.
