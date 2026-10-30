---
name: goldfish-spec-review
description: >-
  Blind spec review and stress-testing protocol (Elephant-Goldfish Model).
  Spawns stateless Goldfish subagents with zero conversational history to
  audit design proposals, challenge unbacked assumptions, enforce Heilmeier's
  Catechism, and detect architectural drift.
tags: [architecture, review, spec, atdd, anti-glazing, goldfish]
---

# Goldfish Spec Review Protocol

O **Goldfish Spec Review** implementa o padrão *Elephant-Goldfish Model* (EGM) para o XP Multi-Agent Kit.

- **🐘 Elephant (Contexto Profundo)**: O agente raiz (`navigator` ou `orchestrator`) que possui todo o contexto do projeto, requisitos acumulados e rascunha as especificações.
- **🐟 Goldfish (Contexto Zero / Stateless)**: Subagentes disparados via `invoke_subagent` com **zero histórico de conversação**. Eles recebem apenas o documento-alvo e o código referenciado. Seu papel é avaliar o plano como um leitor ingênuo (*naive reader*) ou crítico hostil para expor premissas não ditas e pontos cegos.
- **👤 Humano**: Árbitro final que decide trade-offs antes de liberar a codificação.

---

## 1. Princípios Inegociáveis (Anti-Glazing & Hostile Review)

1. **Critique First**: Mesmo em boas propostas, inicie explicitamente com o que está frágil, ausente ou arriscado antes de pontuar méritos.
2. **Eliminação de Sicofância (No Glazing)**:
   - É **proibido** usar adjetivos vazios de validação ("brilhante", "excelente", "perfeito", "ótima ideia").
   - Elogios sem evidência técnica são ruído e mascaram riscos.
3. **Rejeição do Enquadramento de Eco (No Echo-Chamber)**: Nunca valide uma premissa só porque o usuário ou o agente raiz a afirmaram. Se uma conclusão não tem prova, aponte como premissa não justificada.
4. **Stress-Testing Ativo**: Para toda decisão técnica, responda:
   - *O que o autor não está vendo?*
   - *Qual é o contra-argumento mais forte?*
   - *Como essa solução falha sob alta carga, partição de rede ou concorrência?*
5. **Zero Desculpas (No Apologies)**: Não gaste tokens pedindo desculpas quando corrigido ou desafiado. Ajuste os argumentos e aponte a lógica técnica diretamente.

---

## 2. As 5 Fases do Protocolo Goldfish

Ao auditar uma especificação arquitetural (L2/L3) ou um PRD:

### Fase 1: Initial Zoom Out Review
* **Persona**: `personas/zoom_out.md`
* **Padrão**: `resources/zoom-out-standard.md` (Catecismo de Heilmeier)
* **Perguntas Obrigatórias**:
  - O que estamos tentando fazer? (Sem jargões)
  - Como isso é feito hoje e quais os limites da prática atual?
  - O que há de novo na abordagem e por que achamos que terá sucesso?
  - Quem se importa? Se tivermos sucesso, que diferença isso fará?
  - Quais são os riscos e os custos (QPS, memória, tokens, latência)?
  - Quais são os testes intermediários e finais para medir o sucesso?

### Fase 2: Comprehension & Plain Language Review
* **Persona**: `personas/comprehension.md`
* **Critério**: O texto pode ser compreendido sem ambiguidades por um engenheiro que acabou de entrar no time? Há adjetivos promocionais vazios (*seamless, robust, blazingly fast*)? Mecanismos técnicos são explicados objetivamente?

### Fase 3: Hostile Design Critique
* **Persona**: `personas/design_critic.md`
* **Foco**:
  - Gargalos de escalabilidade e pontos únicos de falha (SPOF).
  - Economia de recursos: QPS de pico, consumo de storage e orçamentos de LLM/tokens.
  - Inconsistências de concorrência, idempotência e tratamento de falhas transacionais.

### Fase 4: Intermediate Alignment & Remediation
* O agente raiz consolida os apontamentos em `[Blocker]`, `[Major]` e `[Nit]`.
* Corrige as lacunas na especificação antes de submeter ao Gate Humano.

### Fase 5: Implementation Readiness
* **Persona**: `personas/implementation_readiness.md`
* **Padrão**: `resources/implementation-readiness-standard.md`
* **Critério**: A equipe de desenvolvimento (`builder` / `test-guardian`) tem tudo o que precisa para codificar sem adivinhar comportamento? Os critérios de aceitação e casos extremos estão 100% delimitados?

---

## 3. Disparo Operacional (Subagents)

O orquestrador ou `navigator` dispara a revisão invocando o subagente em sessão limpa:

```python
# Invocação via Antigravity / CLI Driver
invoke_subagent(
    TypeName="research",  # ou subagente stateless read-only
    Role="Goldfish Design Critic",
    Prompt="""
Você é o Design Critic Goldfish. Leia a persona em:
.agents/skills/goldfish-spec-review/personas/design_critic.md

Audite o documento em modo REVIEW:
TargetFile: docs/designs/<especificacao>.md
Standard: .agents/skills/goldfish-spec-review/resources/heilmeier-standard.md

Seu objetivo é estressar premissas e encontrar falhas de escalabilidade, 
custo e concorrência. Não faça elogios. Seja cirúrgico.
"""
)
```

---

## 4. Auditoria de Desvio (Spec Drift Audit)

Durante a fase de `release-gatekeeper` ou `refactor-warden`:
- Compare a especificação aprovada em `docs/designs/` com o código final implementado.
- Relate qualquer divergência de contrato, schema de banco ou endpoints em um relatório de desvio (`docs/designs/drift_report.md`).
