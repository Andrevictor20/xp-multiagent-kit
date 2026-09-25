---
name: spec-driven-development
description: Engenharia de software guiada por especificação formal (SDD), invertendo vibe coding para Specification-as-Source-of-Truth.
---

# Spec-Driven Development (SDD) Skill

Esta skill governa a metodologia de **Spec-Driven Development (SDD)** no XP Multi-Agent Kit. Em vez de partir de prompts abertos ("vibe coding"), o sistema trata a **especificação estruturada e versionada como a única fonte da verdade**, tratando o código como um artefato derivado e verificável.

---

## 1. Princípios Fundamentais (Maturidade Nível 3)
1. **Spec as Source of Truth:** Nenhum código é gerado antes que a especificação em Markdown estruturado seja aprovada.
2. **Acceptance Criteria em Gherkin:** Todo requisito deve ser expresso em cenários `Given / When / Then` testáveis por máquina.
3. **Validação Bidirecional:** A suíte de testes deve espelhar 1:1 os cenários da especificação. Se a spec mudar, a suíte de testes quebra (RED) e o código é corrigido (GREEN).
4. **Living Spec:** Especificações residem em `.agents/specs/` ou `docs/specs/` e são mantidas vivas e sincronizadas.

---

## 2. Estrutura Canônica da Especificação (`SPEC-NNN.md`)

```markdown
# SPEC-001: [Título Conciso da Funcionalidade]

## 1. Contexto & Problema de Negócio
- Por que estamos construindo isso?
- Qual o impacto esperado e restrições não negociáveis?

## 2. Contrato de Domínio & Interfaces
- Schemas de dados (TypeScript, Pydantic, Rust Structs ou Protobuf).
- Endpoints, payloads e códigos de erro esperados.

## 3. Matriz de Cenários de Aceite (Gherkin BDD)
Scenario: Sucesso na autenticação com credenciais válidas
  Given um usuário cadastrado com email "user@example.com"
  When uma requisição POST é enviada para "/api/v1/auth/login" com a senha correta
  Then a resposta deve ter status 200
  And o payload deve conter um JWT assinado e tempo de expiração

Scenario: Bloqueio após 5 tentativas consecutivas com falha
  Given uma conta existente com 4 falhas prévias
  When a 5ª tentativa falha ocorrer
  Then a conta deve ser bloqueada temporariamente por 15 minutos
  And um evento de auditoria de segurança deve ser emitido

## 4. Testes de Conformidade & Invariantes
- Propriedades matemáticas/lógicas que nunca devem ser violadas.
- Limites de taxa (rate limiting), timeouts e comportamento sob carga.
```

---

## 3. Ciclo Operacional do Agente
1. **`navigator`**: Formula a especificação canônica com base no pedido do usuário.
2. **Stop Gate (Aprovação do Usuário):** Apresenta a especificação e obtém o "De Acordo" formal.
3. **`test-guardian`**: Converte os cenários Gherkin diretamente em testes unitários/integração que falham (**RED**).
4. **`builder`**: Codifica exclusivamente a lógica necessária para satisfazer os cenários da spec (**GREEN**).
5. **`archivist`**: Arquiva a spec em disco e atualiza o `PROJECT_MEMORY.md`.
