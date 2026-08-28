# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-08-28 16:15 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v2.7.0 (Strict TDD Multi-Layer Matrix & Anti-Test-Bypass Policy Release)

---

## 1. Quick Project Summary (Semantic)
- **Propósito:** Kit modular de governança, agentes, skills, workflows e políticas para pair programming com IA baseado na metodologia Extreme Programming (XP), Task Routing adaptativo por risco (L0-L3), TDD estrito com Matriz Multi-Camadas, Política Anti-Test-Bypass, SSDLC, Engenharia de Causa Raiz & Anti-Workaround, Code Deslop, DevOps & Zero-Downtime Deployments, Observabilidade & SLOs, Cloud Security & Zero Trust Architecture, Engenharia de Frontend Anti-Slop, Motor de Conversion Copywriting e Sistema de Memória Contínua em 4 Tiers (Karpathy LLM Wiki Pattern).
- **Tech Stack:** Antigravity Agent Framework (Markdown + YAML Frontmatter), Agnóstico de linguagem de produção, Git.
- **Arquitetura Chave:** Estrutura modular em `.agents/` contendo `agents` (especialistas), `skills` (61 capacidades granulares), `workflows` (esteiras L0-L3), `policies` (regras inegociáveis), `templates` (scaffolds) e `memory` (memória viva em 4 tiers e arquivo permanente). Roteamento inteligente via `orchestrator`.
- **Comandos Essenciais:**
  - Validação Git: `git status && git log -n 5 --oneline`
  - Instalação em Novos Projetos: Copiar pasta `.agents/` e `AGENTS.md` para a raiz do repositório destino.

---

## 2. Current Health & System Status
- **Agent Suite Status:** OPERATIONAL (11 Agentes, 61 Skills, 7 Workflows, 9 Policies, Memória em 4 Tiers Ativa)
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (TDD Multi-Camadas, Anti-Test-Bypass, SSDLC, Zero-Downtime, IaC Governance, Observability RED, CloudSec OIDC, Root-Cause Debugging, No Workarounds, Code Deslop, Frontend Anti-Slop, 4-Tier Memory e Token Efficiency)
- **Última Execução / Evidência:** `EV-TEST-INTEGRITY-20260828-01` (Validação de schemas, frontmatter, policies e integridade das regras de testes)
- **Ambiente Ativo:** Local / Antigravity IDE

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)

| Data / Hora | Tipo | Resumo da Alteração | Arquivos Principais | Test Evidence / Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-28 | `FEAT` | Reforço de Diversidade de Tipos de Teste (Matriz de 8 Camadas) e Política Inegociável Anti-Test-Bypass (proibição de mocks cegos, skips e asserções fakes) | `AGENTS.md`, `.agents/policies/tdd.md`, `.agents/skills/tdd-safety-net/SKILL.md`, `.agents/agents/{test-guardian, release-gatekeeper}/`, `README.md` | `PASS (EV-TEST-INTEGRITY-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração da suíte de DevOps, Deploy sem Downtime (Blue/Green, Canary), Governança de IaC, Observabilidade (Métricas RED, Logs JSON) e CloudSec Zero Trust (OIDC, Cosign/SBOM) | `.agents/skills/{zero-downtime-deployment, infrastructure-as-code-governance, observability-and-slo-engineering, cloud-security-and-zero-trust}/`, `.agents/agents/{shipper, sentinel}/`, `.agents/workflows/release.md`, `.agents/policies/release.md`, `README.md` | `PASS (EV-DEVOPS-CLOUDSEC-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração da suíte de Engenharia de Causa Raiz, Debugging Sistemático, Proibição de Remendos (No Workarounds), Code Deslop e Lições Aprendidas (CompozyOS) | `.agents/skills/{systematic-debugging, no-workarounds, code-deslop-review, lesson-learned}/`, `.agents/workflows/bugfix.md`, `.agents/policies/tdd.md`, `.agents/agents/{builder, refactor-warden, test-guardian, archivist}/`, `README.md` | `PASS (EV-ENGINEERING-DESLOP-20260828-01)` |
| 2026-08-28 | `FEAT` | Integração da arquitetura de 4 Tiers de Memória (Working, Episodic, Semantic, Procedural), Handoffs Estruturados, Memory Lint e salvaguarda Untrusted History | `.agents/skills/project-memory/SKILL.md`, `.agents/templates/PROJECT_MEMORY_TEMPLATE.md`, `.agents/policies/memory.md`, `.agents/agents/archivist/agent.md`, `AGENTS.md`, `README.md` | `PASS (EV-MEMORY-4TIER-20260828-01)` |
| 2026-08-28 | `FEAT` | Adição do Motor de Conversion Copywriting, CRO, SEO Semântico/GEO e Psicologia Comportamental (5 novas skills e atualização de agentes) | `.agents/skills/{conversion-copywriting, cro-landing-pages, seo-content-engine, marketing-psychology, copy-editing-sweeps}/`, `.agents/policies/frontend.md`, `.agents/agents/{designer, navigator}/`, `README.md` | `PASS (EV-COPY-SEO-20260828-01)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)
- [x] **[DONE] Reforçar diversidade de tipos de teste e política Anti-Test-Bypass em todas as diretrizes.**
- [x] **[DONE] Integrar suíte de DevOps, Zero-Downtime, IaC Governance, Observabilidade e CloudSec Zero Trust.**
- [x] **[DONE] Integrar suíte de Engenharia de Causa Raiz, No Workarounds, Code Deslop e Lições Aprendidas.**
- [x] **[DONE] Integrar arquitetura de 4 Tiers de memória, Handoffs estruturados e rotina de Memory Lint.**
- [x] **[DONE] Integrar motor de Conversion Copywriting, CRO, SEO Semântico e Psicologia Comportamental.**
- [ ] **[P1] Validar a execução da matriz multi-testes em um projeto piloto complexo.**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
- **2026-08-28 - Matriz de Diversidade de Testes:** Aplicação adaptativa de testes Unitários, Integração, Contrato, Regressão, E2E, Fuzzing, Segurança e Performance.
- **2026-08-28 - Política Anti-Test-Bypass:** Proibição inegociável de mocks cegos excessivos, asserções vazias, skips não autorizados e fabricação de evidências.
- **2026-08-28 - DevOps Zero-Downtime & Observabilidade:** Deploys em produção exigem Blue/Green, Canary ou Rolling Updates com probes e telemetria RED.

---

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
- **[L-001] Schema Injection em Frontend:** Validar scripts de dados estruturados Schema.org JSON-LD via Browser / Rich Results Test.
- **[L-002] Viewport Shifts no Mobile:** Uso estrito de `min-h-[100dvh]` em vez de `h-screen`.
- **[L-003] Regra dos 3 Fixes em Debugging:** Três falhas consecutivas indicam problema arquitetural.
- **[L-004] Autenticação OIDC em CI/CD:** GitHub Actions requer permissão `id-token: write` no workflow.
- **[L-005] Anti-Test-Bypass Check:** Nunca checar apenas o tipo retornado (`typeof`); valide sempre os valores exatos de negócio (`id`, `status`, `amount`).

---

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** O kit está 100% autossuficiente e pronto para distribuição.
