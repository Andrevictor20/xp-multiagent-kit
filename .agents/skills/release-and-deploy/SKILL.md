---
name: release-and-deploy
description: End-to-end continuous deployment, CI security gates, dependency governance, observability/SLOs, and zero-downtime release strategies.
---

# Release and Deploy (`release-and-deploy`)

Consolida as disciplinas de **CI/CD**, **Gates de Release**, **Governança de Dependências**, **Observabilidade** e **Zero-Downtime Deployment**.

## 1. Portões de CI (Continuous Integration)
- Pipelines automatizados com execução sequencial: Lint -> Audit -> SAST -> Testes Unitários -> Testes de Integração.
- Falha em qualquer etapa bloqueia imediatamente o avanço do release.

## 2. Governança de Dependências & Licenças
- Avaliação de dependências de terceiros contra inchaço (bloat) e licenças restritivas incompatíveis.
- Lockfiles estritos com hashes SHA-256 fixados em versionamento.

## 3. Estratégias de Deploy com Zero Downtime
- **Canary & Blue/Green:** Promoção gradual de tráfego (10% -> 50% -> 100%) monitorando taxa de erro.
- **Rollback Instantâneo Automatizado:** Se a taxa de erro HTTP 5xx ou latência p99 exceder o SLO durante o deploy, abortar e reverter imediatamente.

## 4. Observabilidade & Métricas RED/SLO
- Logs em formato JSON estruturado com campos obrigatórios: `timestamp`, `level`, `trace_id`, `service`, `message`.
- Monitoramento contínuo das métricas RED (Rate, Errors, Duration) e SLIs/SLOs de disponibilidade.
