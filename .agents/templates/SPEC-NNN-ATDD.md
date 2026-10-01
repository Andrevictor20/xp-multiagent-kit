# SPEC-NNN: [Título Conciso da Funcionalidade]

> **Status:** {{DRAFT | APPROVED | IMPLEMENTED | ARCHIVED}}
> **Risco:** {{L1 | L2 | L3}}
> **Autor:** {{Nome}}
> **Data:** {{YYYY-MM-DD}}

---

## 1. Contexto & Problema de Negócio

- **Por que estamos construindo isso?**
  {{Descrição do problema ou oportunidade de negócio}}

- **Impacto esperado:**
  {{Resultado mensurável: métrica de negócio, performance, segurança}}

- **Restrições não negociáveis:**
  {{Limites técnicos, regulatórios ou de prazo}}

---

## 2. Acceptance Criteria (ATDD)

> Cada critério deve ser **verificável por máquina**. Proibido critérios vagos.

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

### AC-3: [Título descritivo]
- **Dado:** [pré-condição]
- **Quando:** [ação]
- **Então:** [resultado]
- **Métrica:** [como medir]

---

## 3. Specification by Example (SbE)

> Tabelas parametrizadas com exemplos concretos. Cada linha vira um caso de teste.

### Regra: [Descrição da regra de negócio]

| Input A | Input B | Pré-condição | Resultado Esperado | Código | Motivo |
|---------|---------|--------------|--------------------|--------|--------|
| {{val}} | {{val}} | {{cond}}     | {{resultado}}      | {{HTTP}} | {{caso}} |
| {{val}} | {{val}} | {{cond}}     | {{resultado}}      | {{HTTP}} | {{edge case}} |
| {{val}} | {{val}} | {{cond}}     | {{resultado}}      | {{HTTP}} | {{erro}} |

### Regra: [Outra regra de negócio, se houver]

| Input | Condição | Resultado | Motivo |
|-------|----------|-----------|--------|
| {{val}} | {{cond}} | {{res}}   | {{caso}} |

---

## 4. Cenários de Aceite (Gherkin BDD)

```gherkin
Feature: [Nome da funcionalidade]

  Scenario: [Cenário de sucesso principal]
    Given [pré-condição]
    And [contexto adicional]
    When [ação]
    Then [resultado esperado]
    And [efeito colateral esperado]

  Scenario: [Cenário de erro / edge case]
    Given [pré-condição]
    When [ação que deve falhar]
    Then [resultado de erro esperado]
    And [nenhum efeito colateral]

  Scenario Outline: [Cenário parametrizado baseado em SbE]
    Given <pré-condição>
    When <ação> com <input>
    Then o resultado deve ser <resultado>

    Examples:
      | pré-condição | input | resultado |
      | {{cond}}     | {{in}}| {{out}}   |
```

---

## 5. Contrato de Domínio & Interfaces

- **Schemas de dados:** (TypeScript, Pydantic, Rust Structs ou Protobuf)
- **Endpoints:** método, rota, payloads e códigos de erro esperados.
- **Eventos emitidos:** nome, payload e condições de emissão.

---

## 6. Invariantes & Propriedades

> Propriedades matemáticas/lógicas que NUNCA devem ser violadas, independente da entrada.

- {{Invariante 1: ex: saldo nunca pode ser negativo}}
- {{Invariante 2: ex: hash de senha nunca aparece em response}}
- {{Invariante 3: ex: idempotência em operações de retry}}

---

## 7. Conformance Tracking (preenchido pela IA após implementação)

| # | Acceptance Criteria | Test File | Test Name | Status |
|---|---|---|---|---|
| AC-1 | {{descrição}} | {{path}} | {{test_name}} | ⬜ PENDING |
| AC-2 | {{descrição}} | {{path}} | {{test_name}} | ⬜ PENDING |
| AC-3 | {{descrição}} | {{path}} | {{test_name}} | ⬜ PENDING |

**Resultado: 0/N critérios cobertos.**

---

## 8. Notas de Implementação (preenchido pela IA)

- **Decisões técnicas tomadas:**
- **Trade-offs aceitos:**
- **Dívidas técnicas criadas:**
