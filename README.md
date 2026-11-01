# XP Multi-Agent Kit v4.0.0 — Thin Harness

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Version: 4.0.0](https://img.shields.io/badge/version-4.0.0-brightgreen.svg)](#)
[![TDD: Strict RED-GREEN](https://img.shields.io/badge/TDD-strict-success.svg)](#garantias-de-engenharia)

Thin Harness determinístico de governança para pair-programming com agentes de IA (**Antigravity**, **OpenCode**, **Cursor**, **Codex**, **Qoder** e **Claude**). Substitui prosa redundante por mecanismos verificáveis em código e reduz o contexto base fixo para ≤ 8 KB.

---

## 1. Arquitetura em 4 Camadas

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. HARNESS: PreTool Guard + policy.yaml + kit_events.jsonl (segurança) │
├────────────────────────────────────────────────────────────────────────┤
│ 2. LOOP: xp contract (run.json) + xp gate (10 degraus) + EGM (2 pers.) │
├────────────────────────────────────────────────────────────────────────┤
│ 3. GRAPH: workflow.yaml (8 fluxos) + xp flow (congelamento SHA-256 RED)│
├────────────────────────────────────────────────────────────────────────┤
│ 4. CORE: 6 agentes nucleares + 24 skills + packs (.agents/packs/)      │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Harness (Camada Externa):** Interceptação determinística via hooks (`pre_tool_guard`), tiers de permissão em `policy.yaml` (`auto|review|human`) e telemetria estruturada em `.agents/runtime/events.jsonl`.
2. **Loop (Execução Focada):** Contrato estruturado em `run.json` (`xp contract`), portão de entrega com 10 degraus (`xp gate`) e auditoria EGM com 2 personas (`spec_reviewer`, `code_reviewer`).
3. **Graph (Transições):** Máquina de estados orientada por `workflow.yaml`, avanço verificado e congelamento de testes RED (`xp flow`).
4. **Core (Especialistas):** 6 agentes nucleares (`orchestrator`, `builder`, `reviewer`, `sentinel`, `designer`, `shipper`) e 24 skills no catálogo principal, com pacotes opcionais em `.agents/packs/`.

---

## 2. Instalação e Configuração

```bash
# Instalação global via shell
./scripts/install-global.sh

# Ou via instalador agnóstico Python
python3 scripts/kit_installer.py
```

---

## 3. Comandos Canônicos (`xp`)

A interface CLI unificada `xp` consolida todos os pontos de entrada do kit:

| Comando | Descrição |
|---|---|
| `xp contract <init|show|validate>` | Inicializa e valida contrato da tarefa em `.agents/runtime/run.json` |
| `xp gate <check|--sync-memory>` | Executa os 10 degraus do portão de conformidade e gera o recibo |
| `xp flow <start|next|advance|reopen>` | Conduz o grafo do workflow e gerencia congelamento RED de testes |
| `xp evolve <report|propose|apply>` | Auto-melhoria orientada a evidências de falhas e auditoria de ablação |
| `xp kit <doctor|pack|eval|install>` | Linter de integridade (`kit doctor lint`), packs, eval e instalação |
| `xp memory <sync|search|archive>` | Sincroniza e busca na memória contínua de 4 tiers |
| `xp context <query>` | Recuperação contextual Just-in-Time (JIT) de baixo consumo |
| `xp approve <action_id>` | Registra autorização humana explícita para ações de alto risco |
| `xp run <cmd>` | Execução protegida e monitorada pelo harness |

---

## 4. Garantias de Engenharia

- **Contexto Base ≤ 8.000 B:** `AGENTS.md` (≤ 3.000 B) + `PROJECT_MEMORY.md` (≤ 3.000 B) carregados inicialmente; demais sob demanda.
- **TDD Estrito & Anti-Test-Bypass Mecânico:** Testes unitários RED congelados por hash SHA-256; alteração não autorizada bloqueia no gate.
- **Auditoria Contínua:** `xp kit doctor lint` valida integridade, orçamentos e conformidade com `components.yaml`.

---

## 5. Disciplina Git & Higiene de Repositório

- **Commits Atômicos:** Mensagens estruturadas no padrão Conventional Commits (`feat`, `fix`, `refactor`, `test`, `chore`).
- **Zero Planos no Git:** Planos de trabalho e prompts transitórios são mantidos fora do versionamento via `.gitignore`.
- **Gates Bloqueantes:** Todo push exige aprovação prévia em `xp gate check` e 100% dos testes unitários verdes.
