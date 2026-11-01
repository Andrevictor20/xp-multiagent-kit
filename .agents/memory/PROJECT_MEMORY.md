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
| 2026-11-01 | `FEAT` | Thin Harness Fase 1 (v4.0.0-alpha) — Implementação determinística de contrato (`xp_contract.py`), política por custo de reversão (`.agents/policy.yaml`), hook `pre_tool_guard.py`, telemetria local (`kit_events.py`), gate barato-primeiro (`xp_gate.py`) com recibo de 7 campos em PT-BR e esqueleto CLI `xp` | `scripts/xp*`, `.agents/policy.yaml`, `.agents/components.yaml`, `tests/*` | `PASS (406/406 tests)` |
| 2026-10-31 | `FEAT` | CodeRabbit Review & Template Declarativo (v3.9.2) — Skill `coderabbit-review` com fallback não-bloqueante à CLI, template `.coderabbit.yaml` (No God Files <500L, Zero Workarounds, WCAG AA), acoplamento aos agentes `refactor-warden` (EGM Pass 2) e `release-gatekeeper` e 80 skills ativas | `.agents/skills/coderabbit-review/`, `.agents/templates/.coderabbit.yaml`, `.agents/agents/` | `PASS (385/385 tests)` |
| 2026-10-31 | `FEAT` | Motor de Memória JIT e Auto-Injeção via Hook (v3.9.1) — Expansão de `scripts/memory_search.py` (FTS5 BM25) cobrindo policies/specs/details/ADRs com contextual chunking, motor `context_retriever.py` (CLI `agy-context`/`xp-context` <300 tokens) e auto-injeção em `dynamic_effort_hook.py` | `scripts/context_retriever.py`, `scripts/memory_search.py`, `tests/test_context_engine.py` | `PASS (385/385 tests)` |
| 2026-10-31 | `FEAT` | Motor de Completude Exaustiva & Revisão Multi-Pass EGM (v3.9.0 / SPEC-005) — Mandato `COMPLETENESS_OVER_SPEED`, 3 passadas de EGM em `scripts/goldfish_review.py` (`xp-goldfish`/`agy-goldfish`), `EFFORT_HIGH` no `agy_effort_router.py` e 6 novos testes TDD | `AGENTS.md`, `scripts/goldfish_review.py`, `tests/test_egm_completeness_engine.py` | `PASS (379/379 tests)` |
| 2026-10-30 | `FEAT` | Integração Inicial do Modelo Elephant-Goldfish (EGM) (v3.8.0) — Criação da skill `goldfish-spec-review`, 9 personas de revisores cegos, padrões Heilmeier e 4 testes unitários | `.agents/skills/goldfish-spec-review/`, `scripts/goldfish_review.py`, `tests/test_goldfish_review.py` | `PASS (373/373 tests)` |

*(Histórico anterior arquivado em [details/episodic-archive.md](details/episodic-archive.md))*

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

### 📌 Ponto de Parada Atual (Sessão 2026-11-01):
- **Status:** Concluída a Fase 1 da migração Thin Harness (v4.0.0-alpha / SPEC-006) com TDD estrito. Implementados: contrato em software (`scripts/xp_contract.py`), matriz declarativa por custo de reversão (`.agents/policy.yaml`), hook PreToolUse (`scripts/hooks/pre_tool_guard.py`), telemetria local (`scripts/kit_events.py`), gate determinístico (`scripts/xp_gate.py`), ledger de componentes (`.agents/components.yaml`) e esqueleto CLI (`scripts/xp`).
- **Suíte de Testes:** 406/406 testes PASS (100% GREEN, zero regressão).
- **Orçamento de Contexto:** `AGENTS.md` e `PROJECT_MEMORY.md` 100% dentro dos tetos (`audit_context_budget` GREEN).

### 📋 Próximos Passos:
1. **[P1] Fase 2 — Cortes Seguros:** Reduzir `AGENTS.md` (≤3.000 B) e `PROJECT_MEMORY.md` (≤3.000 B) para fechar base ≤8.000 B; mover `token-economy.md` para sob demanda; implementar `kit_lint.py`; unificar CLI `xp` (9 subcomandos).

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
> Conteúdo em [details/5-architectural-decisions-domain-models-semantic-memory.md](details/5-architectural-decisions-domain-models-semantic-memory.md).

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
> Conteúdo em [details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md](details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md).

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** Orçamento de contexto base (`AGENTS.md`, `PROJECT_MEMORY.md`, 80 `SKILL.md` e `SKILLS_INDEX.md`) 100% dentro dos tetos de `kit_constants.py`.
