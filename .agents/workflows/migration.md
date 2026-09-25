---
name: migration
description: "Workflow de migração estrutural segura (banco de dados, infra, ORMs, contratos) com padrão Expand-and-Contract e Zero Downtime."
---
# Database & Infrastructure Migration Workflow

## Flow
Passo 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `sentinel` (Threat Modeling & Data Loss Risk Analysis) → `navigator` (Elaboração do Plano Expand-and-Contract) → **User Review Gate (Aprovação do Plano de Migração e Rollback)** → `test-guardian` (Testes de Paridade e Shadow Testing RED) → `builder` (Implementação de Dual-Write, Backfill e Adapters GREEN) → `shipper` (Canary Cutover com Telemetria RED) → `refactor-warden` (Remoção da Versão Legada / Fase Contract) → **Passo Final OBRIGATÓRIO: Persistência em Disco no `.agents/memory/PROJECT_MEMORY.md` pelo `archivist`** → `release-gatekeeper`

## Guidelines
- **Zero Downtime Absoluto:** Proibido operações bloqueantes de tabela (como `ALTER TABLE ... ADD COLUMN ... DEFAULT` pesado sem lock timeout).
- **Expand-and-Contract em 3 Fases:**
  1. *Expand:* Adiciona a nova coluna/tabela sem remover a antiga; aplica escrita dupla (dual-write).
  2. *Migrate/Backfill:* Script assíncrono em lotes pequenos migra os dados históricos.
  3. *Contract:* Remove leitura legada, direciona 100% do tráfego para a nova estrutura e descarta campos obsoletos.
- **Rollback Imediato Testado:** Todo script de migração `UP` DEVE possuir seu correspondente `DOWN` testado localmente.
