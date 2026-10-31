# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-10-31 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v3.9.0 (SPEC-005: Motor de Completude Exaustiva & Revisão Multi-Pass EGM)

---

## 1. Quick Project Summary (Semantic)

- **Propósito:** Kit modular e agnóstico de governança, agentes, skills, workflows e políticas para pair programming com IA em **Antigravity, OpenCode, Cursor, Codex, Qoder e Claude (IDE & CLI)**, priorizando **Completude Exaustiva Acima de Velocidade (`COMPLETENESS_OVER_SPEED = True`)**, **Revisão Cega Multi-Pass EGM (Elephant-Goldfish Model)** em 3 passadas (Spec/Heilmeier/Zero-Decision + Codebase Details + Spec-vs-Code Drift), Task Routing L0-L3, Pirâmide ATDD/BDD, TDD estrito, Anti-Test-Bypass, Motor Multiagente Boss-Worker e Memória Contínua em 4 Tiers.
- **Tech Stack:** Multi-Host Agent Framework (`AGENTS.md`, `opencode.json`, `.cursor/rules/*.mdc`, `.codex/rules/`, `.qoder/rules/`, `CLAUDE.md`), Python 3.8+, Bash, PowerShell 5.1+, Windows CMD, Git, GitHub Actions CLI (`gh`). Agnóstico de SO (Linux, macOS, Windows).
- **Arquitetura Chave:** `.agents/` (11 agentes, 79 skills `< 6KB` em Inglês, 11 workflows, 12 policies, 5 templates com saída obrigatória em Português). Suíte modular em `scripts/goldfish_review.py` (`xp-goldfish` / `agy-goldfish`), `scripts/antigravity_multiagent.py`, `scripts/agy_effort_router.py`, `scripts/host_adapters.py`, `scripts/mcp_installers.py`, `scripts/spec_tool.py`, `scripts/windows_support.py` e binários globais em `~/.local/bin/`.
- **Comandos Essenciais:** (Catálogo completo em [details/commands.md](details/commands.md))
  - Instalação: `./install.sh [--global|--project <dir>|--both <dir>] [--target all|...] [--lang pt|en]`
  - Auditoria Multi-Pass EGM (Goldfish): `xp-goldfish --multipass <spec.md> --code-files ... --test-files ...` / `agy-goldfish`
  - Gestão e Diagnóstico do Kit: `xp-kit [doctor|init <dir>|sync|update|version]` / `agy-kit`
  - Ferramenta ATDD de Specs: `xp-spec [new <slug>|validate <file>]` / `agy-spec`
  - Orquestração Multiagente: `xp-orchestrate [run|validate|dashboard|init]` / `agy-orchestrate`
  - Orçamento de Contexto & Skills: `python3 scripts/skill_index.py [generate|audit]`

---

## 2. Current Health & System Status

- **Agent Suite Status:** OPERATIONAL (11 Agentes, 79 Skills `< 6KB`, 11 Workflows, 12 Policies, 6 Hosts Nativos com Motor Multiagente Boss-Worker e Revisão Multi-Pass EGM em 3 Passadas).
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (379/379 testes unitários e de aceitação `PASS`, `AGENTS.md <= 6KB`, `PROJECT_MEMORY.md <= 8KB`).
- **Última Execução / Evidência:** `EV-KIT-V3.9.0-EGM-MULTIPASS-COMPLETENESS-20261031` (Implementação da SPEC-005: diretriz Completeness Over Speed, motor de 3 passadas EGM em `scripts/goldfish_review.py`, binários `xp-goldfish`/`agy-goldfish`, elevação automática de esforço para HIGH em planejamento/EGM sem turn-throttle, `goldfish-spec-review` em `CORE_SKILLS`, e 379/379 testes PASS).
- **Ambiente Ativo:** Local & Global / Linux, macOS e Windows nativo.

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5 Entregas)

| Data | Tipo | Descrição Concisa | Arquivos Chave | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-31 | `FEAT` | Motor de Completude Exaustiva & Revisão Multi-Pass EGM (v3.9.0 / SPEC-005) — (1) Mandato `COMPLETENESS_OVER_SPEED = True` e `EGM_MIN_REVIEW_PASSES = 2` em `kit_constants.py` e `AGENTS.md`, (2) Evolução de `scripts/goldfish_review.py` com 3 passadas (`validate_implementation_readiness`, `audit_code_completeness`, `audit_spec_code_drift`, `run_multipass_egm_review`) e binários `xp-goldfish`/`agy-goldfish`, (3) Elevação de planejamento/EGM para `EFFORT_HIGH` sem turn-throttle em `agy_effort_router.py`, (4) Inclusão de `goldfish-spec-review` e `spec-driven-development` em `CORE_SKILLS`, (5) Integração nos agentes, workflows, templates e 6 novos testes TDD (`379/379 PASS`) | `AGENTS.md`, `scripts/goldfish_review.py`, `scripts/agy_effort_router.py`, `scripts/skill_profiles.py`, `.agents/specs/SPEC-005-EGM-COMPLETENESS-ENGINE.md`, `tests/test_egm_completeness_engine.py` | `PASS (379/379 tests)` |
| 2026-10-30 | `FEAT` | Integração Inicial do Modelo Elephant-Goldfish (EGM) (v3.8.0) — Criação da skill `goldfish-spec-review`, 9 personas de revisores cegos, padrões Heilmeier e 4 testes unitários | `.agents/skills/goldfish-spec-review/`, `scripts/goldfish_review.py`, `tests/test_goldfish_review.py` | `PASS (373/373 tests)` |
| 2026-10-30 | `FEAT` | Expansão Multiagente Multi-Host — Etapas 4 (Cursor) e 5 (Qoder) (v3.7.0) — Implementação de `CursorWorkerDriver` e `QoderWorkerDriver` em `scripts/multiagent_drivers.py` e 17 testes TDD | `scripts/multiagent_drivers.py`, `scripts/host_adapters.py`, `tests/test_cursor_multiagent.py`, `tests/test_qoder_multiagent.py` | `PASS (369/369 tests)` |
| 2026-10-30 | `FEAT` | Integração de Toolchain Alethe Orchestrator (v3.6.5) — Implementação de `AletheInstaller` em `scripts/mcp_installers.py` expondo `alethe`, `xp-alethe` e `agy-alethe` | `scripts/mcp_installers.py`, `scripts/kit_installer.py` | `PASS (352/352 tests)` |
| 2026-10-30 | `FEAT` | Mandato Rígido de AST CodeReviewGraph (CRG) & Auto-Bootstrap (v3.6.4) — Uso obrigatório de `code-review-graph` para Impact Mapping (L1+) e auto-bootstrap de `graph.db` | `AGENTS.md`, `scripts/skill_profiles.py`, `scripts/hooks/crg-auto-update.sh` | `PASS (351/351 tests)` |

*(Histórico anterior arquivado em [details/episodic-archive.md](details/episodic-archive.md))*

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

### 📌 Ponto de Parada Atual (Sessão 2026-10-31):
- **Status:** Implementada e validada em múltiplas passadas EGM a **SPEC-005 (Motor de Completude Exaustiva & Revisão Multi-Pass EGM v3.9.0)**.
- **Suíte de Testes:** 379/379 testes PASS (100% GREEN, zero regressão).
- **Orçamento de Contexto:** `AGENTS.md` e `PROJECT_MEMORY.md` 100% dentro dos tetos (`audit_context_budget` GREEN).

### 📋 Próximos Passos:
1. **[P1] Projeto Piloto Multi-IDE com Multi-Pass EGM:** Validar execução de um projeto externo aplicando as 3 passadas obrigatórias do `xp-goldfish --multipass`.

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
> Conteúdo em [details/5-architectural-decisions-domain-models-semantic-memory.md](details/5-architectural-decisions-domain-models-semantic-memory.md).

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
> Conteúdo em [details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md](details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md).

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** Orçamento de contexto base (`AGENTS.md`, `PROJECT_MEMORY.md`, 79 `SKILL.md` e `SKILLS_INDEX.md`) 100% dentro dos tetos de `kit_constants.py`.
