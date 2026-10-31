# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-10-31 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v3.9.2 (Integração CodeRabbit Review & Template Declarativo com Fallback Não-Bloqueante)

---

## 1. Quick Project Summary (Semantic)

- **Propósito:** Kit modular e agnóstico de governança, agentes, skills, workflows e políticas para pair programming com IA em **Antigravity, OpenCode, Cursor, Codex, Qoder e Claude (IDE & CLI)**, priorizando **Completude Exaustiva Acima de Velocidade (`COMPLETENESS_OVER_SPEED = True`)**, **Revisão Cega Multi-Pass EGM (Elephant-Goldfish Model)** em 3 passadas (Spec/Heilmeier/Zero-Decision + Codebase Details + Spec-vs-Code Drift), Task Routing L0-L3, Pirâmide ATDD/BDD, TDD estrito, Anti-Test-Bypass, Motor Multiagente Boss-Worker e Memória Contínua em 4 Tiers.
- **Tech Stack:** Multi-Host Agent Framework (`AGENTS.md`, `opencode.json`, `.cursor/rules/*.mdc`, `.codex/rules/`, `.qoder/rules/`, `CLAUDE.md`), Python 3.8+, Bash, PowerShell 5.1+, Windows CMD, Git, GitHub Actions CLI (`gh`). Agnóstico de SO (Linux, macOS, Windows).
- **Arquitetura Chave:** `.agents/` (11 agentes, 80 skills `< 6KB` em Inglês, 11 workflows, 12 policies, 5 templates com saída obrigatória em Português). Suíte modular em `scripts/goldfish_review.py` (`xp-goldfish` / `agy-goldfish`), `scripts/antigravity_multiagent.py`, `scripts/agy_effort_router.py`, `scripts/host_adapters.py`, `scripts/mcp_installers.py`, `scripts/spec_tool.py`, `scripts/windows_support.py` e binários globais em `~/.local/bin/`.
- **Comandos Essenciais:** (Catálogo completo em [details/commands.md](details/commands.md))
  - Instalação: `./install.sh [--global|--project <dir>|--both <dir>] [--target all|...] [--lang pt|en]`
  - Auditoria Multi-Pass EGM (Goldfish): `xp-goldfish --multipass <spec.md> --code-files ... --test-files ...` / `agy-goldfish`
  - Gestão e Diagnóstico do Kit: `xp-kit [doctor|init <dir>|sync|update|version]` / `agy-kit`
  - Ferramenta ATDD de Specs: `xp-spec [new <slug>|validate <file>]` / `agy-spec`
  - Orquestração Multiagente: `xp-orchestrate [run|validate|dashboard|init]` / `agy-orchestrate`
  - Orçamento de Contexto & Skills: `python3 scripts/skill_index.py [generate|audit]`

---

## 2. Current Health & System Status

- **Agent Suite Status:** OPERATIONAL (11 Agentes, 80 Skills `< 6KB`, 11 Workflows, 12 Policies, 6 Hosts Nativos com Motor Multiagente Boss-Worker e Revisão Multi-Pass EGM em 3 Passadas).
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (385/385 testes unitários e de aceitação `PASS`, `AGENTS.md <= 6KB`, `PROJECT_MEMORY.md <= 8KB`).
- **Última Execução / Evidência:** `EV-KIT-V3.9.2-CODERABBIT-REVIEW-INTEGRATION-20261031` (Skill `coderabbit-review`, template `.coderabbit.yaml`, acoplamento no `refactor-warden` e `release-gatekeeper`, fallback gracioso não-bloqueante e 385/385 testes PASS).
- **Ambiente Ativo:** Local & Global / Linux, macOS e Windows nativo.

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5 Entregas)

| Data | Tipo | Descrição Concisa | Arquivos Chave | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-31 | `FEAT` | CodeRabbit Review & Template Declarativo (v3.9.2) — Skill `coderabbit-review` com fallback não-bloqueante à CLI, template `.coderabbit.yaml` (No God Files <500L, Zero Workarounds, WCAG AA), acoplamento aos agentes `refactor-warden` (EGM Pass 2) e `release-gatekeeper` e 80 skills ativas | `.agents/skills/coderabbit-review/`, `.agents/templates/.coderabbit.yaml`, `.agents/agents/` | `PASS (385/385 tests)` |
| 2026-10-31 | `FEAT` | Motor de Memória JIT e Auto-Injeção via Hook (v3.9.1) — Expansão de `scripts/memory_search.py` (FTS5 BM25) cobrindo policies/specs/details/ADRs com contextual chunking, motor `context_retriever.py` (CLI `agy-context`/`xp-context` <300 tokens) e auto-injeção em `dynamic_effort_hook.py` | `scripts/context_retriever.py`, `scripts/memory_search.py`, `tests/test_context_engine.py` | `PASS (385/385 tests)` |
| 2026-10-31 | `FEAT` | Motor de Completude Exaustiva & Revisão Multi-Pass EGM (v3.9.0 / SPEC-005) — Mandato `COMPLETENESS_OVER_SPEED`, 3 passadas de EGM em `scripts/goldfish_review.py` (`xp-goldfish`/`agy-goldfish`), `EFFORT_HIGH` no `agy_effort_router.py` e 6 novos testes TDD | `AGENTS.md`, `scripts/goldfish_review.py`, `tests/test_egm_completeness_engine.py` | `PASS (379/379 tests)` |
| 2026-10-30 | `FEAT` | Integração Inicial do Modelo Elephant-Goldfish (EGM) (v3.8.0) — Criação da skill `goldfish-spec-review`, 9 personas de revisores cegos, padrões Heilmeier e 4 testes unitários | `.agents/skills/goldfish-spec-review/`, `scripts/goldfish_review.py`, `tests/test_goldfish_review.py` | `PASS (373/373 tests)` |
| 2026-10-30 | `FEAT` | Expansão Multiagente Multi-Host — Etapas 4 (Cursor) e 5 (Qoder) (v3.7.0) — Implementação de `CursorWorkerDriver` e `QoderWorkerDriver` em `scripts/multiagent_drivers.py` e 17 testes TDD | `scripts/multiagent_drivers.py`, `scripts/host_adapters.py`, `tests/test_cursor_multiagent.py` | `PASS (369/369 tests)` |

*(Histórico anterior arquivado em [details/episodic-archive.md](details/episodic-archive.md))*

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

### 📌 Ponto de Parada Atual (Sessão 2026-10-31):
- **Status:** Implementada e integrada a skill **`coderabbit-review`** e template **`.coderabbit.yaml`** (v3.9.2), provendo auditoria externa de diffs para o `refactor-warden` (EGM Pass 2) e `release-gatekeeper` (Conformance Gate) com fallback 100% não-bloqueante.
- **Suíte de Testes:** 385/385 testes PASS (100% GREEN, zero regressão).
- **Orçamento de Contexto:** `AGENTS.md` e `PROJECT_MEMORY.md` 100% dentro dos tetos (`audit_context_budget` GREEN).

### 📋 Próximos Passos:
1. **[P1] Projeto Piloto Multi-IDE com Multi-Pass EGM:** Validar execução de um projeto externo aplicando as 3 passadas obrigatórias do `xp-goldfish --multipass`.

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
> Conteúdo em [details/5-architectural-decisions-domain-models-semantic-memory.md](details/5-architectural-decisions-domain-models-semantic-memory.md).

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
> Conteúdo em [details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md](details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md).

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** Orçamento de contexto base (`AGENTS.md`, `PROJECT_MEMORY.md`, 80 `SKILL.md` e `SKILLS_INDEX.md`) 100% dentro dos tetos de `kit_constants.py`.
