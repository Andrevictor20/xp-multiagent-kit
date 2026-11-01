---
name: spec-pyramid
description: Specification Pyramid combining ATDD/BDD, Spec-Driven Development (SDD), Specification by Example (SbE), and pair navigation.
---

# Specification Pyramid (`spec-pyramid`)

Consolida as disciplinas de **ATDD/BDD**, **SDD**, **SbE** e **Pair Navigation** em uma fonte única e concisa.

## 1. Separação de Contrato: O QUÊ vs COMO
- **Humano define O QUÊ:** Critérios de Aceitação (ACs), tabelas de Specification by Example (SbE) e cenários de negócio.
- **IA implementa COMO:** Testes unitários RED determinísticos, implementação mínima GREEN e refatoração sem regressão.
- **Regra Anti-Self-Test:** O agente nunca redige a especificação e os testes sem submeter a spec ao Stop Gate humano (`approve_spec`).

## 2. Specification by Example (SbE)
- Regras ambíguas de negócio DEVEM ser expressas através de tabelas concretas com entradas e saídas esperadas:
  - Cenários de caminho feliz (Happy Path).
  - Casos de borda (Boundary values: limites zero, nulos, vazios, extremos).
  - Casos de erro e exceções controladas.

## 3. Estrutura SDD (Specification-Driven Development)
- Toda especificação em `.agents/specs/` deve conter:
  1. **Objetivo & Contexto:** O problema real resolvido e quem é impactado.
  2. **Alternativas Rejeitadas:** Pelo menos duas alternativas descartadas com justificativa técnica.
  3. **Critérios de Aceitação (ACs):** Mensuráveis, testáveis e com rastreabilidade direta aos testes.
  4. **Restrições de Escopo:** Arquivos permitidos para alteração e o que está expressamente proibido mudar.

## 4. Pair Navigation & Anti-Over-Engineering
- Implementar a solução mais simples que atenda aos critérios.
- Sem abstrações prematuras ou antecipação de requisitos inexistentes (YAGNI).
- Parar na segunda tentativa de falha idêntica (Circuit Breaker).
