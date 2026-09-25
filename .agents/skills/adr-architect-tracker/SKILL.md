---
name: adr-architect-tracker
description: Formalização ágil de Architectural Decision Records no padrão MADR 3.0 e detecção contínua de desvio arquitetural (Architectural Drift).
---

# ADR Architect Tracker Skill

Esta skill governa a documentação, rastreabilidade e governança de **Architectural Decision Records (ADRs)** no padrão MADR 3.0 (Markdown Architectural Decision Records), vinculando decisões técnicas diretamente à memória semântica do projeto (`.agents/memory/PROJECT_MEMORY.md`).

---

## 1. Quando Formalizar uma ADR?
Uma ADR é obrigatória sempre que uma decisão de design de software introduzir:
1. Escolha ou troca de tecnologia/framework/banco de dados.
2. Mudança no modelo de consistência ou comunicação assíncrona (ex: de REST para gRPC/Kafka).
3. Padrão estrutural que afeta múltiplos módulos (ex: adoção de Clean Architecture, Hexagonal ou Event Sourcing).
4. Trade-off intencional com impacto na segurança, performance ou custo.

---

## 2. Template Canônico MADR 3.0 (`docs/adr/ADR-NNN-[slug].md`)

```markdown
# ADR-005: Adoção do PostgreSQL com pgvector para Busca Semântica

- **Status:** Aceito
- **Decisores:** Time de Engenharia + Antigravity Agent
- **Data:** 2026-09-25

## Contexto e Problema
Precisamos implementar busca vetorial rápida para chunks de documentação com menos de 50ms de latência P95, sem adicionar a sobrecarga operacional de gerenciar um cluster dedicado do Pinecone ou Qdrant.

## Opções Consideradas
1. Pinecone Gerenciado
2. Qdrant Self-Hosted
3. PostgreSQL com extensão `pgvector`

## Decisão Tomada
Optamos pela opção 3 (`pgvector`), porque já utilizamos PostgreSQL em produção para dados transacionais, eliminando custos adicionais de infraestrutura e simplificando backups transacionais atômicos (ACID).

## Consequências
- **Positivas:** Zero custo de infraestrutura adicional; consistência transacional direta via joins SQL.
- **Negativas:** Requer tuning de índices HNSW/IVFFlat à medida que a base ultrapassar 2 milhões de vetores.
```

---

## 3. Detecção de Desvio Arquitetural (Architectural Drift)
O `navigator` e o `refactor-warden` devem consultar periodicamente as ADRs existentes. Se um novo código implementar uma solução que contrarie uma ADR sem uma nova ADR de revogação/substituição, a PR ou entrega é **bloqueada pelo Quality Gate**.
