# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-08-28 17:40 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v2.8.1 (Git History Recapture & Reverse Ingestion Release)

---

## 1. Quick Project Summary (Semantic)
- **Propósito:** Kit modular de governança, agentes, skills, workflows e políticas para pair programming com IA baseado na metodologia Extreme Programming (XP), Task Routing adaptativo por risco (L0-L3), TDD estrito com Matriz Multi-Camadas, Política Anti-Test-Bypass, SSDLC, Engenharia de Causa Raiz & Anti-Workaround, Code Deslop, DevOps & Zero-Downtime Deployments, Observabilidade & SLOs, Cloud Security & Zero Trust Architecture, Engenharia de Frontend Anti-Slop, Motor de Conversion Copywriting e Sistema de Memória Contínua em 4 Tiers com Auto-Onboarding, Recaptura Retroativa de Histórico Git (Reverse Ingestion) e Ciclo de Vida 100% Autônomo Zero-Prompt.
- **Tech Stack:** Antigravity Agent Framework (Markdown + YAML Frontmatter), Agnóstico de linguagem de produção, Git.
- **Arquitetura Chave:** Estrutura modular em `.agents/` contendo `agents` (especialistas), `skills` (61 capacidades granulares), `workflows` (esteiras L0-L3 com Passo 0 e Passo Final autônomos), `policies` (regras inegociáveis), `templates` (scaffolds) e `memory` (memória viva em 4 tiers, auto-onboarding, recaptura git e arquivo permanente). Roteamento inteligente via `orchestrator`.
- **Comandos Essenciais:**
  - Validação Git: `git status && git log -n 5 --oneline`
  - Instalação em Novos/Existentes Projetos: Copiar pasta `.agents/` e `AGENTS.md` para a raiz do repositório destino (o kit executa a Recaptura Git e o Auto-Onboarding automaticamente).

---

## 2. Current Health & System Status
- **Agent Suite Status:** OPERATIONAL (11 Agentes, 61 Skills, 7 Workflows, 9 Policies, Memória em 4 Tiers com Recaptura Git Ativa)
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (TDD Multi-Camadas, Anti-Test-Bypass, SSDLC, Zero-Downtime, IaC Governance, Observability RED, CloudSec OIDC, Root-Cause Debugging, No Workarounds, Code Deslop, Frontend Anti-Slop, 4-Tier Memory, Auto-Onboarding, Reverse Ingestion e Zero-Prompt Lifecycle)
- **Última Execução / Evidência:** `EV-GIT-RECAPTURE-20260828-01` (Validação de schemas, frontmatter, policies, workflows e integridade das regras de memória contínua com recaptura git)
- **Ambiente Ativo:** Local / Antigravity IDE

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)

| Data / Hora | Tipo | Resumo da Alteração | Arquivos Principais | Test Evidence / Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-28 | `FEAT` | Adição do protocolo de Recaptura Retroativa de Contexto Git (Reverse Ingestion) para repositórios existentes adicionados tardiamente | `AGENTS.md`, `.agents/policies/memory.md`, `.agents/skills/project-memory/SKILL.md`, `.agents/agents/{archivist, orchestrator}/`, `README.md` | `PASS (EV-GIT-RECAPTURE-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração do Auto-Onboarding para projetos alvo (Passo 0-A) e ciclo de vida de memória 100% autônomo (Zero-Prompt Lifecycle) | `AGENTS.md`, `.agents/policies/memory.md`, `.agents/skills/project-memory/SKILL.md`, `.agents/agents/{orchestrator, archivist, genesis}/`, `.agents/workflows/*`, `README.md` | `PASS (EV-MEMORY-AUTONOMOUS-20260828-01)` |
| 2026-08-28 | `FEAT` | Reforço de Diversidade de Tipos de Teste (Matriz de 8 Camadas) e Política Inegociável Anti-Test-Bypass (proibição de mocks cegos, skips e asserções fakes) | `AGENTS.md`, `.agents/policies/tdd.md`, `.agents/skills/tdd-safety-net/SKILL.md`, `.agents/agents/{test-guardian, release-gatekeeper}/`, `README.md` | `PASS (EV-TEST-INTEGRITY-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração da suíte de DevOps, Deploy sem Downtime (Blue/Green, Canary), Governança de IaC, Observabilidade (Métricas RED, Logs JSON) e CloudSec Zero Trust (OIDC, Cosign/SBOM) | `.agents/skills/{zero-downtime-deployment, infrastructure-as-code-governance, observability-and-slo-engineering, cloud-security-and-zero-trust}/`, `.agents/agents/{shipper, sentinel}/`, `.agents/workflows/release.md`, `.agents/policies/release.md`, `README.md` | `PASS (EV-DEVOPS-CLOUDSEC-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração da suíte de Engenharia de Causa Raiz, Debugging Sistemático, Proibição de Remendos (No Workarounds), Code Deslop e Lições Aprendidas (CompozyOS) | `.agents/skills/{systematic-debugging, no-workarounds, code-deslop-review, lesson-learned}/`, `.agents/workflows/bugfix.md`, `.agents/policies/tdd.md`, `.agents/agents/{builder, refactor-warden, test-guardian, archivist}/`, `README.md` | `PASS (EV-ENGINEERING-DESLOP-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração da arquitetura de 4 Tiers de Memória (Working, Episodic, Semantic, Procedural), Handoffs Estruturados, Memory Lint e salvaguarda Untrusted History | `.agents/skills/project-memory/SKILL.md`, `.agents/templates/PROJECT_MEMORY_TEMPLATE.md`, `.agents/policies/memory.md`, `.agents/agents/archivist/agent.md`, `AGENTS.md`, `README.md` | `PASS (EV-MEMORY-4TIER-20260828-01)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)
- [x] **[DONE] Integrar Recaptura Retroativa de Histórico Git e Contexto para repositórios existentes.**
- [x] **[DONE] Integrar Auto-Onboarding automático de novos projetos e ciclo de vida zero-prompt da memória viva.**
- [x] **[DONE] Reforçar diversidade de tipos de teste e política Anti-Test-Bypass em todas as diretrizes.**
- [x] **[DONE] Integrar suíte de DevOps, Zero-Downtime, IaC Governance, Observabilidade e CloudSec Zero Trust.**
- [x] **[DONE] Integrar suíte de Engenharia de Causa Raiz, No Workarounds, Code Deslop e Lições Aprendidas.**
- [x] **[DONE] Integrar arquitetura de 4 Tiers de memória, Handoffs estruturados e rotina de Memory Lint.**
- [ ] **[P1] Validar a execução da matriz multi-testes em um projeto piloto complexo.**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
- **2026-08-28 - Recaptura Retroativa Git (Reverse Ingestion):** Ao ser introduzido em repositórios pré-existentes, o kit reconstrói a memória viva a partir do git log, manifestos e código existente, prosseguindo com o desenvolvimento contínuo.
- **2026-08-28 - Zero-Prompt Memory & Auto-Onboarding:** Todo agente e workflow roda Passo 0 (Bootstrap com Auto-Onboarding se repositório não inicializado/divergente) e Passo Final (Auto-Sync pelo Archivist) de forma nativa e incondicional sem depender de comandos do usuário.
- **2026-08-28 - Matriz de Diversidade de Testes:** Aplicação adaptativa de testes Unitários, Integração, Contrato, Regressão, E2E, Fuzzing, Segurança e Performance.
- **2026-08-28 - Política Anti-Test-Bypass:** Proibição inegociável de mocks cegos excessivos, asserções vazias, skips não autorizados e fabricação de evidências.

---

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
- **[L-001] Schema Injection em Frontend:** Validar scripts de dados estruturados Schema.org JSON-LD via Browser / Rich Results Test.
- **[L-002] Viewport Shifts no Mobile:** Uso estrito de `min-h-[100dvh]` em vez de `h-screen`.
- **[L-003] Regra dos 3 Fixes em Debugging:** Três falhas consecutivas indicam problema arquitetural.
- **[L-004] Autenticação OIDC em CI/CD:** GitHub Actions requer permissão `id-token: write` no workflow.
- **[L-005] Anti-Test-Bypass Check:** Nunca checar apenas o tipo retornado (`typeof`); valide sempre os valores exatos de negócio (`id`, `status`, `amount`).
- **[L-006] Auto-Onboarding de Repositórios:** Se o repositório aberto for novo ou diferente do kit, o Passo 0-A deve detectar manifestos e reconstruir `PROJECT_MEMORY.md` imediatamente antes de qualquer outra ação.
- **[L-007] Ingestão Reversa de Commits:** Usar formato conciso de git log (`%h - %ad : %s`) com janela deslizante de 5 a 10 commits para não estourar o orçamento de tokens da memória ativa.

---

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** O kit está 100% autossuficiente e pronto para distribuição.
